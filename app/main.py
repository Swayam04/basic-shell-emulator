import os
import sys

def find_file(filename):
    path_dirs = os.environ["PATH"].split(os.pathsep)
    for directory in path_dirs:
        full_path = os.path.join(directory, filename)
        if os.path.exists(full_path):
            return full_path
    return None

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
            elif find_file(command_name) is not None:
                print(f"{command_name} is {find_file(command_name)}")
            else:
                print(f"{command_name}: not found")
        else:
            print(f"{s}: command not found")


if __name__ == "__main__":
    main()
