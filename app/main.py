import sys


def main():

    while True:
        sys.stdout.write("$ ")
        s = input()
        if s == "exit 0":
            break
        print(f"{s}: command not found")


if __name__ == "__main__":
    main()
