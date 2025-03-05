import os
import readline
import shlex
import subprocess
import sys

executable_cache = set()
full_path_executable_cache = {}

def discover_system_executables():
    """
    Scan all directories in the system PATH to discover and cache executable files.

    This method builds two caches:
    - executable_cache: A set of executable filenames
    - full_path_executable_cache: A dictionary mapping filenames to their full paths

    Handles potential errors like:
    - Non-existent directories
    - Permission-denied directories
    """
    for directory in os.environ["PATH"].split(os.pathsep):
        if not os.path.isdir(directory):
            continue
        try:
            for filename in os.listdir(directory):
                full_path = os.path.join(directory, filename)
                if is_executable(full_path):
                    executable_cache.add(filename)
                    full_path_executable_cache[filename] = full_path
        except FileNotFoundError:
            print(f"Warning: Directory not found - {directory}")
        except PermissionError:
            print(f"Warning: Permission denied - {directory}")


def is_executable(path):
    """
    Verify if a given file path represents an executable file.

    Args:
        path (str): Full path to the file to be checked

    Returns:
        bool: True if the file is executable, False otherwise
    """
    return os.path.isfile(path) and os.access(path, os.X_OK)


def execute_subprocess(command, args):
    """
    Execute an external command as a subprocess with given arguments.

    Args:
        command (str): The command to execute
        args (list): Command-line arguments for the command

    Returns:
        tuple: A pair of strings containing subprocess stdout and stderr

    Raises:
        subprocess.CalledProcessError: If the subprocess execution fails
    """
    try:
        result = subprocess.run([command] + args, capture_output=True, text=True, check=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr


def handle_echo_command(args):
    """
    Process the 'echo' shell command by concatenating arguments.

    Args:
        args (list): Arguments to be echoed back

    Returns:
        tuple: A pair of strings (output, error_message)
    """
    return " ".join(args) + "\n", ""


def handle_type_command(args, commands):
    """
    Implement the 'type' shell command to identify command origins.

    Determines whether a command is:
    - A shell builtin
    - An executable in the system PATH
    - Not found

    Args:
        args (list): Command name to query
        commands (dict): Dictionary of shell builtin commands

    Returns:
        tuple: A pair of strings (output, error_message)
    """
    if not args:
        return "", "type: missing argument\n"
    command_name = args[0]
    full_command = full_path_executable_cache.get(command_name)
    if command_name in commands and command_name != "cat":
        return f"{command_name} is a shell builtin\n", ""
    elif full_command:
        return f"{command_name} is {full_command}\n", ""
    else:
        return "", f"{command_name}: not found\n"


def handle_change_directory(args):
    """
    Change the current working directory based on provided arguments.

    Supports:
    - No argument (defaults to home directory)
    - '~' as home directory shortcut
    - Specific directory path

    Args:
        args (list): Directory path or empty list

    Returns:
        tuple: A pair of strings (output, error_message)
    """
    target_dir = os.environ.get("HOME", "/") if not args or args[0] == "~" else args[0]
    try:
        os.chdir(target_dir)
        return "", ""
    except FileNotFoundError:
        return "", f"cd: {target_dir}: No such file or directory\n"
    except PermissionError:
        return "", f"cd: {target_dir}: Permission denied\n"


def handle_cat_command(args):
    """
    Implement the 'cat' command to read and display file contents.

    Supports multiple file arguments and handles various file access errors.

    Args:
        args (list): Paths of files to concatenate and display

    Returns:
        tuple: A pair of strings (concatenated_file_contents, error_messages)
    """
    stdout, stderr = "", ""
    for path in args:
        try:
            with open(path, 'r') as f:
                stdout += f.read()
        except FileNotFoundError:
            stderr += f"cat: {path}: No such file or directory\n"
        except PermissionError:
            stderr += f"cat: {path}: Permission denied\n"
    return stdout, stderr


def parse_command_redirection(cmd_args):
    """
    Parse command arguments to detect and handle output/error redirection.

    Supports various redirection syntax:
    - Stdout: '>', '>>', '1>', '1>>'
    - Stderr: '2>', '2>>'
    - Compact forms like '>file', '2>file'

    Args:
        cmd_args (list): Full list of command arguments

    Returns:
        tuple: Processed arguments, stdout file, stderr file, and redirection modes
    """
    stdout_file, stderr_file = None, None
    remaining_args = []
    stdout_mode, stderr_mode = 'w', 'w'
    i = 0

    while i < len(cmd_args):
        arg = cmd_args[i]

        if arg in ('>>', '1>>'):
            stdout_file, stdout_mode = cmd_args[i + 1], 'a'
            i += 2
        elif arg in ('>', '1>'):
            stdout_file, stdout_mode = cmd_args[i + 1], 'w'
            i += 2
        elif arg == '2>>':
            stderr_file, stderr_mode = cmd_args[i + 1], 'a'
            i += 2
        elif arg == '2>':
            stderr_file, stderr_mode = cmd_args[i + 1], 'w'
            i += 2
        elif arg.startswith('2>>') and len(arg) > 3:
            stderr_file, stderr_mode = arg[3:], 'a'
            i += 1
        elif arg.startswith('2>') and len(arg) > 2:
            stderr_file, stderr_mode = arg[2:], 'w'
            i += 1
        elif arg.startswith('1>>') and len(arg) > 3:
            stdout_file, stdout_mode = arg[3:], 'a'
            i += 1
        elif arg.startswith('1>') and len(arg) > 2:
            stdout_file, stdout_mode = arg[2:], 'w'
            i += 1
        elif arg.startswith('>>') and len(arg) > 2:
            stdout_file, stdout_mode = arg[2:], 'a'
            i += 1
        elif arg.startswith('>') and len(arg) > 1:
            stdout_file, stdout_mode = arg[1:], 'w'
            i += 1
        else:
            remaining_args.append(arg)
            i += 1

    return remaining_args, stdout_file, stderr_file, {'stdout': stdout_mode, 'stderr': stderr_mode}


def write_output_to_file(filename, content, mode):
    """
    Write content to a file with specified mode, creating directories if needed.

    Args:
        filename (str): Path to the output file
        content (str): Content to write
        mode (str): File open mode ('w' for write, 'a' for append)

    Handles file and directory creation errors gracefully.
    """
    try:
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        with open(filename, mode) as f:
            f.write(content)
    except FileNotFoundError:
        print(f"Error: {filename}: No such file or directory", file=sys.stderr)
    except PermissionError:
        print(f"Error: {filename}: Permission denied", file=sys.stderr)


def command_name_completer(text, state):
    """
    Readline completer for shell command names.

    Provides tab-completion for built-in commands and system executables.
    Handles single/multiple matches and provides user feedback.

    Args:
        text (str): Current text being completed
        state (int): Completion state for multiple matches

    Returns:
        str or None: Completed command or None if no match
    """
    builtins = ["exit ", "echo ", "type ", "pwd ", "cd ", "cat "]

    matches_builtins = [cmd for cmd in builtins if cmd.startswith(text)]
    matches_executables = [cmd for cmd in executable_cache if cmd.startswith(text)]

    if not matches_builtins and not matches_executables and state == 0:
        sys.stdout.write('\a')
        sys.stdout.flush()
        return None

    if matches_builtins:
        return matches_builtins[state]
    elif matches_executables:
        if len(matches_executables) == 1:
            return matches_executables[state] + " "
        else:
            return matches_executables[state]
    return None


readline.parse_and_bind("tab: complete")
readline.set_completer(command_name_completer)


def main():
    """
    Main shell execution loop.

    Features:
    - Shell built-in commands: exit, echo, type, pwd, cd, cat
    - System executable support
    - Output and error redirection
    - Tab completion
    - Error handling for various scenarios
    """
    discover_system_executables()

    commands = {
        "exit": lambda arguments: sys.exit(0),
        "echo": handle_echo_command,
        "type": lambda arguments: handle_type_command(arguments, commands),
        "pwd": lambda arguments: (os.getcwd() + "\n", ""),
        "cd": handle_change_directory,
        "cat": handle_cat_command,
    }

    while True:
        try:
            user_input = input("$ ").strip()
            if not user_input:
                continue

            args = shlex.split(user_input)
            if not args:
                continue

            cmd, *cmd_args = args
            filtered_args, stdout_file, stderr_file, modes = parse_command_redirection(cmd_args)

            if cmd in commands:
                stdout, stderr = commands[cmd](filtered_args)
            else:
                if cmd in executable_cache:
                    stdout, stderr = execute_subprocess(cmd, filtered_args)
                else:
                    stdout, stderr = "", f"{cmd}: command not found\n"

            if stdout_file:
                write_output_to_file(stdout_file, stdout, modes['stdout'])
            elif stdout:
                print(stdout, end='')

            if stderr_file:
                write_output_to_file(stderr_file, stderr, modes['stderr'])
            elif stderr:
                print(stderr, end='', file=sys.stderr)

        except KeyboardInterrupt:
            print()
        except EOFError:
            print()
            sys.exit(0)


if __name__ == "__main__":
    main()