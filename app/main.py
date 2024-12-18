import os
import subprocess
import sys

def find_file(filename):
    path_dirs = os.environ["PATH"].split(os.pathsep)
    for directory in path_dirs:
        full_path = os.path.join(directory, filename)
        if os.path.exists(full_path):
            return full_path
    return None

def run_subprocess(full_path, args):
    result = subprocess.run([full_path] + args, capture_output=True, text=True)
    return result.stdout

def main():
    commands = {"exit": 0, "echo": 1, "type": 2}
    while True:
        sys.stdout.write("$ ")
        s = input()
        if s.startswith("exit"):
            break
        elif s.startswith("echo"):
            print(s.removeprefix("echo "))
        elif s.startswith("type"):
            command_name = s.removeprefix("type ")
            if command_name in commands:
                print(f"{command_name} is a shell builtin")
            elif (full_path := find_file(command_name)) is not None:
                print(f"{command_name} is {full_path}")
            else:
                print(f"{command_name}: not found")
        else:
            args = s.split(" ")
            full_path = find_file(args[0])
            if full_path is not None:
                output = run_subprocess(full_path, args[1:])
                print(output.strip())
            else:
                print(f"{s}: command not found")


if __name__ == "__main__":
    main()
