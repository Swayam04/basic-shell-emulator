import os
import shlex
import subprocess
import sys


def is_executable(path):
    """Check if the given path is an executable file."""
    return os.path.isfile(path) and os.access(path, os.X_OK)


def find_file(filename):
    """Find an executable file in the system PATH."""
    for directory in os.environ["PATH"].split(os.pathsep):
        full_path = os.path.join(directory, filename)
        if is_executable(full_path):
            return full_path
    return None


def run_subprocess(command, args):
    """Run a subprocess with the given command and arguments."""
    try:
        result = subprocess.run([command] + args,
                                capture_output=True,
                                text=True,
                                check=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr


def echo_handler(args):
    """Handle the `echo` command."""
    stdout = " ".join(args) + "\n"  # Ensuring a newline at the end
    stderr = ""
    return stdout, stderr


def type_handler(args, commands):
    """Handle the `type` command."""
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
    """Handle the `cd` command."""
    if not args or args[0] == "~":
        target_dir = os.environ.get("HOME", "/")
    else:
        target_dir = args[0]
    try:
        os.chdir(target_dir)
        return "", ""
    except FileNotFoundError:
        return "", f"cd: {target_dir}: No such file or directory\n"
    except PermissionError:
        return "", f"cd: {target_dir}: Permission denied\n"


def cat_handler(args):
    """Handle the `cat` command."""
    stdout = ""
    stderr = ""
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
    Parse and handle command redirection for stdout (>, 1>) and stderr (2>).
    Returns a tuple of (remaining_args, stdout_file, stderr_file, modes)
    """
    stdout_file = None
    stderr_file = None
    remaining_args = []
    stdout_mode = 'w'
    stderr_mode = 'w'
    i = 0

    while i < len(cmd_args):
        arg = cmd_args[i]

        if arg in ('>>', '1>>'):
            try:
                stdout_file = cmd_args[i + 1]
                stdout_mode = 'a'
                i += 2
            except IndexError:
                print("Error: No file specified for stdout redirection.", file=sys.stderr)
                break
        elif arg in ('>', '1>'):
            try:
                stdout_file = cmd_args[i + 1]
                stdout_mode = 'w'
                i += 2
            except IndexError:
                print("Error: No file specified for stdout redirection.", file=sys.stderr)
                break
        elif arg.startswith('2>>'):
            stdout_file = None
            stderr_file = arg[3:]
            stderr_mode = 'a'
            i += 1
        elif arg.startswith('2>'):
            stdout_file = None
            stderr_file = arg[2:]
            stderr_mode = 'w'
            i += 1
        else:
            remaining_args.append(arg)
            i += 1

    return remaining_args, stdout_file, stderr_file, {'stdout': stdout_mode, 'stderr': stderr_mode}


def write_to_file(filename, content, mode):
    """Write content to a file."""
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


def main():
    """Main function to run the shell."""
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
                if stdout_file:
                    write_to_file(stdout_file, stdout, modes['stdout'])
                else:
                    if stdout:
                        print(stdout, end='')
                if stderr_file:
                    write_to_file(stderr_file, stderr, modes['stderr'])
                else:
                    if stderr:
                        print(stderr, end='', file=sys.stderr)

            else:
                full_path = find_file(cmd)
                if full_path:
                    stdout, stderr = run_subprocess(full_path, filtered_args)
                    if stdout_file:
                        write_to_file(stdout_file, stdout, modes['stdout'])
                    else:
                        if stdout:
                            print(stdout, end='')
                    if stderr_file:
                        write_to_file(stderr_file, stderr, modes['stderr'])
                    else:
                        if stderr:
                            print(stderr, end='', file=sys.stderr)
                else:
                    error_message = f"{cmd}: command not found\n"
                    if stderr_file:
                        write_to_file(stderr_file, error_message, modes['stderr'])
                    else:
                        print(error_message, end='', file=sys.stderr)

        except KeyboardInterrupt:
            print()
        except EOFError:
            print()
            sys.exit(0)


if __name__ == "__main__":
    main()
