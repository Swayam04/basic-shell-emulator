import os
import readline
import shlex
import subprocess
import sys


def is_executable(path):
    """Check if the given path is an executable file.
        Args:
            path (str): The path to the file.
        Returns:
            bool: True if the file is executable, False otherwise.
    """
    return os.path.isfile(path) and os.access(path, os.X_OK)


def find_file(filename):
    """Find an executable file in the system PATH.
        Args:
            filename (str): The name of the file to find.
        Returns:
            str: The full path to the executable file if found, None otherwise.
    """
    for directory in os.environ["PATH"].split(os.pathsep):
        full_path = os.path.join(directory, filename)
        if is_executable(full_path):
            return full_path
    return None


def run_subprocess(command, args):
    """Run a subprocess with the given command and arguments.
        Args:
            command (str): The command to run.
            args (list): A list of arguments for the command.
        Returns:
            tuple: A tuple containing the stdout and stderr output of the command.
    """
    try:
        executable_name = os.path.basename(command)
        result = subprocess.run([executable_name] + args, capture_output=True, text=True, check=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr


def echo_handler(args):
    """Handle the `echo` command.
        Args:
            args (list): A list of arguments passed to the `echo` command.
        Returns:
            tuple: A tuple containing the stdout and stderr output of the command.
    """
    return " ".join(args) + "\n", ""


def type_handler(args, commands):
    """Handle the `type` command.
        Args:
            args (list): A list of arguments passed to the `type` command.
            commands (dict): A dictionary of available commands.
        Returns:
            tuple: A tuple containing the stdout and stderr output of the command.
    """
    if not args:
        return "", "type: missing argument\n"
    command_name = args[0]
    if command_name in commands and command_name != "cat":
        return f"{command_name} is a shell builtin\n", ""
    elif (full_path := find_file(command_name)) is not None:
        return f"{command_name} is {full_path}\n", ""
    else:
        return "", f"{command_name}: not found\n"


def cd_handler(args):
    """Handle the `cd` command.
        Args:
            args (list): A list of arguments passed to the `cd` command.
        Returns:
            tuple: A tuple containing the stdout and stderr output of the command.
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
    """Handle the `cat` command.
        Args:
            args (list): A list of file paths to concatenate and display.
        Returns:
            tuple: A tuple containing the stdout and stderr output of the command.
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
    """Parse and handle command redirection for stdout (>, 1>) and stderr (2>> or 2>).
        Args:
            cmd_args (list): A list of command arguments including potential redirection operators.
        Returns:
            tuple: A tuple containing remaining arguments, stdout file, stderr file, and modes for redirection.
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


def write_to_file(filename, content, mode):
    """Write content to a file.
        Args:
            filename (str): The path to the file.
            content (str): The content to write to the file.
            mode (str): The mode to open the file in, e.g., 'w' for write, 'a' for append.
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


def command_completer(text, index):
    commands = ["exit ", "echo ", "type ", "pwd ", "cd ", "cat "]
    matches = [command for command in commands if command.startswith(text)]
    return matches[index] if matches else None

readline.parse_and_bind("tab: complete")
readline.set_completer(command_completer)

def main():
    """Main function to run the shell.
        Supports 'exit', 'echo', 'type', 'pwd', 'cd', 'cat' as shell built-ins.
        Supports other bash commands as executables.
        Supports output and error redirection to files.
    """
    commands = {
        "exit": lambda arguments: sys.exit(0),
        "echo": echo_handler,
        "type": lambda arguments: type_handler(arguments, commands),
        "pwd": lambda arguments: (os.getcwd() + "\n", ""),
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

            if cmd in commands:
                stdout, stderr = commands[cmd](filtered_args)
            else:
                full_path = find_file(cmd)
                if full_path:
                    stdout, stderr = run_subprocess(full_path, filtered_args)
                else:
                    stdout, stderr = "", f"{cmd}: command not found\n"

            if stdout_file:
                write_to_file(stdout_file, stdout, modes['stdout'])
            elif stdout:
                print(stdout, end='')

            if stderr_file:
                write_to_file(stderr_file, stderr, modes['stderr'])
            elif stderr:
                print(stderr, end='', file=sys.stderr)

        except KeyboardInterrupt:
            print()
        except EOFError:
            print()
            sys.exit(0)


if __name__ == "__main__":
    main()
