import sys


def main():
    sys.stdout.write("$ ")

    # Wait for user input
    s = input()
    print(f"{s}: command not found")


if __name__ == "__main__":
    main()
