import os
import readline
import shlex
import subprocess
import sys



executable_cache = set()
full_path_executable_cache = {}


def get_executables():
    """
    Populate the cache with system executables found in directories listed in the PATH environment variable.
    This speeds up command lookup for the shell.
    """
    for directory in os.environ.get("PATH", "").split(os.pathsep):
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
    Check if a given path corresponds to an executable file.

    Args:
        path (str): The file path to check.

    Returns:
        bool: True if the file is executable, False otherwise.
    """
    return os.path.isfile(path) and os.access(path, os.X_OK)


def run_subprocess(command, args):
    """
    Run a subprocess with the given command and arguments.

    Args:
        command (str): The command to execute.
        args (list): Arguments for the command.

    Returns:
        tuple: (stdout output, stderr output)
    """
    try:
        result = subprocess.run([command] + args, capture_output=True, text=True, check=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr


def echo_handler(args):
    """
    Implementation of the `echo` command.

    Args:
        args (list): Arguments to be echoed.

    Returns:
        tuple: (stdout output, stderr output)
    """
    return " ".join(args) + "\n", ""


def type_handler(args, commands):
    """
    Implementation of the `type` command.

    Args:
        args (list): List of command names to check.
        commands (dict): Dictionary of built-in commands.

    Returns:
        tuple: (stdout output, stderr output)
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


def cd_handler(args):
    """
    Implementation of the `cd` command.

    Args:
        args (list): Directory to change to.

    Returns:
        tuple: (stdout output, stderr output)
    """
    target_dir = os.environ.get("HOME", "/") if not args or args[0] == "~" else args[0]

    try:
        os.chdir(target_dir)
        return "", ""
    except FileNotFoundError:
        return "", f"cd: {target_dir}: No such file or directory\n"
    except PermissionError:
        return "", f"cd: {target_dir}: Permission denied\n"


def cat_handler(args):
    """
    Implementation of the `cat` command.

    Args:
        args (list): List of file paths to read.

    Returns:
        tuple: (stdout output, stderr output)
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


def handle_redirection(cmd_args):
    """
    Parse and handle output redirection.

    Args:
        cmd_args (list): Command arguments, including potential redirection operators.

    Returns:
        tuple: (remaining arguments, stdout file, stderr file, redirection modes)
    """
    stdout_file, stderr_file = None, None
    stdout_mode, stderr_mode = 'w', 'w'
    remaining_args = []
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
        else:
            remaining_args.append(arg)
            i += 1

    return remaining_args, stdout_file, stderr_file, {'stdout': stdout_mode, 'stderr': stderr_mode}


def write_to_file(filename, content, mode):
    """
    Write content to a file.

    Args:
        filename (str): File path.
        content (str): Content to write.
        mode (str): File write mode.
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


def command_completer(text, state):
    """
    Auto-completes shell commands using readline.

    Args:
        text (str): The command input by the user.
        state (int): The state of the completion (e.g., first match, second match).

    Returns:
        str or None: Suggested completion or None if no match.
    """
    builtins = ["exit ", "echo ", "type ", "pwd ", "cd ", "cat "]

    matches = [cmd for cmd in builtins + list(executable_cache) if cmd.startswith(text)]

    if not matches and state == 0:
        sys.stdout.write('\a')
        sys.stdout.flush()
        return None

    return matches[state] if state < len(matches) else None


readline.parse_and_bind("tab: complete")
readline.set_completer(command_completer)


def main():
    """
    Main function for the shell.

    Supports built-in commands:
    - exit
    - echo
    - type
    - pwd
    - cd
    - cat

    Also supports external commands and output redirection.
    """
    get_executables()

    commands = {
        "exit": lambda _: sys.exit(0),
        "echo": echo_handler,
        "type": lambda args: type_handler(args, commands),
        "pwd": lambda _: (os.getcwd() + "\n", ""),
        "cd": cd_handler,
        "cat": cat_handler,
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
            filtered_args, stdout_file, stderr_file, modes = handle_redirection(cmd_args)

            stdout, stderr = commands.get(cmd, lambda _: ("", f"{cmd}: command not found\n"))(filtered_args)

            if stdout_file:
                write_to_file(stdout_file, stdout, modes['stdout'])
            else:
                print(stdout, end='')

            if stderr_file:
                write_to_file(stderr_file, stderr, modes['stderr'])
            else:
                print(stderr, end='', file=sys.stderr)

        except (KeyboardInterrupt, EOFError):
            print()
            sys.exit(0)


if __name__ == "__main__":
    main()
