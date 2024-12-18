import os
import subprocess
import sys


def is_executable(path):
    return os.path.isfile(path) and os.access(path, os.X_OK)

def find_file(filename):
    path_dirs = os.environ["PATH"].split(os.pathsep)
    for directory in path_dirs:
        full_path = os.path.join(directory, filename)
        if is_executable(full_path):
            return full_path
    return None

def run_subprocess(full_path, args):
    try:
        result = subprocess.run([full_path] + args, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running {full_path}: {e.stderr}")
        return None

def main():
    commands = {
        "exit": lambda c: sys.exit(0),
        "echo": lambda c: print(c.removeprefix("echo ").strip()),
        "type": lambda c: type_handler(c, commands),
        "pwd": lambda c: print(os.getcwd()),
        "cd": lambda c: cd_handler(c)
    }
    while True:
        sys.stdout.write("$ ")
        s = input()
        for cmd, handler in commands.items():
            if s.startswith(cmd):
                handler(s)
                break
        else:
            args = s.split(" ")
            full_path = find_file(args[0])
            if full_path is not None:
                output = run_subprocess(full_path, args[1:])
                print(output.strip())
            else:
                print(f"{s}: command not found")

def type_handler(s, commands):
    command_name = s.removeprefix("type ")
    if command_name in commands:
        print(f"{command_name} is a shell builtin")
    elif (full_path := find_file(command_name)) is not None:
        print(f"{command_name} is {full_path}")
    else:
        print(f"{command_name}: not found")

def cd_handler(s):
    dir_path = s.removeprefix("cd ")
    if os.path.isdir(dir_path):
        os.chdir(dir_path)
    else:
        print(f"cd: {dir_path}: No such file or directory")

if __name__ == "__main__":
    main()
