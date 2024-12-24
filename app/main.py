import os
import shlex
import subprocess
import sys
import io


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
        result = subprocess.run([command] + args, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error running {command}: {e.stderr.strip()}"


def echo_handler(args):
    """Handle the `echo` command."""
    return " ".join(args)


def type_handler(args, commands):
    """Handle the `type` command."""
    if not args:
        return "type: missing argument"
    command_name = args[0]
    if command_name in commands and command_name != "cat":
        return f"{command_name} is a shell builtin"
    elif (full_path := find_file(command_name)) is not None:
        return f"{command_name} is {full_path}"
    else:
        return f"{command_name}: not found"


def cd_handler(args):
    """Handle the `cd` command."""
    target_dir = os.environ.get("HOME", "/") if not args or args[0] == "~" else args[0]
    try:
        os.chdir(target_dir)
        return ""
    except FileNotFoundError:
        return f"cd: {target_dir}: No such file or directory"
    except PermissionError:
        return f"cd: {target_dir}: Permission denied"


def cat_handler(args):
    """Handle the `cat` command."""
    output = ""
    for path in args:
        try:
            with open(path, 'r') as f:
                output += f.read()
        except FileNotFoundError:
            output += f"cat: {path}: No such file or directory\n"
        except PermissionError:
            output += f"cat: {path}: Permission denied\n"
    return output


def handle_redirection(cmd_args):
    """
    Parse and handle command redirection for output (>).
    Returns tuple of (remaining_args, redirect_file)
    """
    redirect_file = None
    remaining_args = []
    it = iter(cmd_args)
    for arg in it:
        if arg == '>' or arg.startswith('>'):
            if arg == '>':
                try:
                    redirect_file = next(it)
                except StopIteration:
                    return cmd_args, None  # Invalid syntax, no file specified
            else:
                redirect_file = arg[1:]
        else:
            remaining_args.append(arg)
    return remaining_args, redirect_file


def write_to_file(filename, content):
    """Write content to a file."""
    try:
        with open(filename, 'w') as f:
            f.write(content if content.endswith('\n') else content + '\n')
    except FileNotFoundError:
        print(f"Error: {filename}: No such file or directory")
    except PermissionError:
        print(f"Error: {filename}: Permission denied")


def main():
    """Main function to run the shell."""
    commands = {
        "exit": lambda arguments: sys.exit(0),
        "echo": echo_handler,
        "type": lambda arguments: type_handler(arguments, commands),
        "pwd": lambda arguments: os.getcwd(),
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

            filtered_args, redirect_file = handle_redirection(cmd_args)

            if cmd in commands:
                output = commands[cmd](filtered_args)
                if output:
                    if redirect_file:
                        write_to_file(redirect_file, output)
                    else:
                        print(output)
            else:
                full_path = find_file(cmd)
                if full_path:
                    output = run_subprocess(full_path, filtered_args)
                    if redirect_file:
                        write_to_file(redirect_file, output)
                    else:
                        print(output)
                else:
                    print(f"{cmd}: command not found")
        except KeyboardInterrupt:
            print()
        except EOFError:
            print()
            sys.exit(0)


if __name__ == "__main__":
    main()
