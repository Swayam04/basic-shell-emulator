import sys


def main():
    commands = {"exit": 0, "echo": 1, "type": 2}
    while True:
        sys.stdout.write("$ ")
        s = input()
        if s == "exit":
            break
        elif s.startswith("echo"):
            print(s.removeprefix("echo "))
        elif s.startswith("type"):
            command_name = s.removeprefix("type ")
            if command_name in commands:
                print(f"{command_name} is a shell builtin")
            else:
                print(f"{command_name}: not found")
        else:
            print(f"{s}: command not found")


if __name__ == "__main__":
    main()
