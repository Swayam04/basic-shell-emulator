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
        result = subprocess.run([command] + args, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error running {command}: {e.stderr.strip()}"

def echo_handler(args):
    """Handle the `echo` command."""
    print(" ".join(args))

def type_handler(args, commands):
    """Handle the `type` command."""
    command_name = args[0]
    if command_name in commands and command_name != "cat":
        print(f"{command_name} is a shell builtin")
    elif (full_path := find_file(command_name)) is not None:
        print(f"{command_name} is {full_path}")
    else:
        print(f"{command_name}: not found")

def cd_handler(args):
    """Handle the `cd` command."""
    if len(args) == 0 or args[0] == "~":
        target_dir = os.environ.get("HOME", "/")
    else:
        target_dir = args[0]

    try:
        os.chdir(target_dir)
    except FileNotFoundError:
        print(f"cd: {target_dir}: No such file or directory")
    except PermissionError:
        print(f"cd: {target_dir}: Permission denied")

def cat_handler(args):
    """Handle the `cat` command."""
    for path in args:
        try:
            with open(path, 'r') as f:
                print(f.read(), end="")
        except FileNotFoundError:
            print(f"cat: {path}: No such file or directory")
        except PermissionError:
            print(f"cat: {path}: Permission denied")

def main():
    """Main function to run the shell."""
    commands = {
        "exit": lambda _: sys.exit(0),
        "echo": echo_handler,
        "type": lambda arg: type_handler(arg, commands),
        "pwd": lambda _: print(os.getcwd()),
        "cd": cd_handler,
        "cat": cat_handler,
    }

    while True:
        try:
            user_input = input("$ ").strip()
            if not user_input:
                continue

            args = shlex.split(user_input)
            cmd, *cmd_args = args

            redirect_file = None

            for i in range(0, len(cmd_args)):
                if '>' in cmd_args[i]:
                    redirect_file = cmd_args[i + 1]
                    cmd_args = cmd_args[:i]
                    break

            if cmd in commands:
                if redirect_file:
                    output = commands[cmd](cmd_args)
                    write_to_file(redirect_file, output)
                else:
                    commands[cmd](cmd_args)
            else:
                full_path = find_file(cmd)
                if full_path:
                    output = run_subprocess(full_path, cmd_args)
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

def write_to_file(filename, content):
    try:
        with open(filename, 'w') as f:
            f.write(content + "\n")
    except FileNotFoundError:
        print(f"{filename}: No such file or directory")
    except PermissionError:
        print(f"{filename}: Permission denied")

if __name__ == "__main__":
    main()
