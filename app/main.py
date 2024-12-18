import sys


def main():

    while True:
        sys.stdout.write("$ ")
        s = input()
        print(f"{s}: command not found")


if __name__ == "__main__":
    main()
