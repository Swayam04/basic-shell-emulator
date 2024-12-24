# Mini Shell

A minimal shell environment written in Python. This script provides basic shell functionalities, including built-in commands and the ability to execute external programs.

---

## Features

- Built-in commands:
  - `echo`: Prints the given arguments to the standard output.
  - `type`: Displays information about a command (e.g., if it is a shell built-in or an external program).
  - `pwd`: Prints the current working directory.
  - `cd`: Changes the current directory.
  - `cat`: Prints the content of files to the standard output.
  - `exit`: Exits the shell.

- Executes external commands available in the system's PATH.
- Redirecting/appending of command outputs into files
- Robust error handling for invalid commands, missing files, and permission issues.
- Graceful handling of keyboard interruptions (`Ctrl+C`) and end-of-input signals (`Ctrl+D`).

## Usage

### Shell Commands

The shell supports the following commands:

1. **`echo [arguments...]`**
   - Prints the arguments to the terminal.
   - Example:
     ```bash
     $ echo Hello, World!
     Hello, World!
     ```

2. **`type [command]`**
   - Displays information about a command (e.g., whether it is a shell built-in or an external program).
   - Example:
     ```bash
     $ type echo
     echo is a shell builtin
     ```

3. **`pwd`**
   - Prints the current working directory.
   - Example:
     ```bash
     $ pwd
     /home/user
     ```

4. **`cd [directory]`**
   - Changes the current working directory. Use `cd ~` to navigate to the home directory.
   - Example:
     ```bash
     $ cd /path/to/directory
     $ pwd
     /path/to/directory
     ```

5. **`cat [file...]`**
   - Prints the contents of one or more files to the terminal.
   - Example:
     ```bash
     $ cat file1.txt file2.txt
     [contents of file1.txt]
     [contents of file2.txt]
     ```

6. **`exit`**
   - Exits the shell.

### External Commands

- You can also run any external commands available in the system PATH:
   ```bash
   $ ls -l
   [output of `ls -l`]
   ```

### Redirection

The shell supports standard output and error redirection for commands. You can redirect the output of both built-in and external commands to files.

### Standard Output Redirection

- **Overwrite existing file (`>` or `1>`)**:
  ```bash
  $ echo "Hello, World!" > output.txt
  ```
  This command will write "Hello, World!" to `output.txt`, overwriting any existing content.

- **Append to existing file (`>>` or `1>>`)**:
  ```bash
  $ echo "Hello, again!" >> output.txt
  ```
  This command will append "Hello, again!" to `output.txt`.

### Standard Error Redirection

- **Overwrite existing file (`2>`)**:
  ```bash
  $ cat non_existent_file 2> error.log
  ```
  This command will redirect the error message to `error.log`, overwriting any existing content.

- **Append to existing file (`2>>`)**:
  ```bash
  $ cat non_existent_file 2>> error.log
  ```
  This command will append the error message to `error.log`.

### Combined Standard Output and Error Redirection

- **Redirect both stdout and stderr to separate files**:
  ```bash
  $ command > output.log 2> error.log
  ```
  This redirects standard output to `output.log` and standard error to `error.log`.

### Examples

1. **Save command output**:
   ```bash
   $ pwd > current_directory.txt
   ```

2. **Log errors**:
   ```bash
   $ cat missing_file.txt 2> error_log.txt
   ```

3. **Append multiple outputs**:
   ```bash
   $ echo "Line 1" >> log.txt
   $ echo "Line 2" >> log.txt
   ```

4. **Save both output and errors**:
   ```bash
   $ ls /some/path > output.log 2> errors.log
   ```

Note: The shell creates directories automatically if they don't exist when redirecting output to a file in a non-existent directory.
  
## Installation

To install and run the **Basic Shell Emulator**, follow these steps:

### 1. Clone the repository

- Clone the repository to your local machine using Git:
   
   ```bash
   git clone git@github.com:Swayam04/basic-shell-emulator.git
   cd basic-shell-emulator
   ```

### 2. **Install dependencies**

- The project uses **Pipenv** for managing dependencies. Install the required Python dependencies using the following command:

   ```bash
   pipenv install
   ```
### 3. Run the shell emulator

- Once the dependencies are installed, you can run the shell emulator using the provided `mini-shell.sh` script. This script will execute the Python code in the virtual environment:

   ```bash
   ./mini-shell.sh
   ```
### 4. (Optional) Running the shell without `mini-shell.sh`

- If you don't want to use the `mini-shell.sh` script, you can run the Python script directly by using Pipenv:

   ```bash
   pipenv run python3 -u -m app.main
   ```

### 5. **Additional Notes**

- **Platform Compatibility**: The shell should work on Linux and macOS. Windows users may need to adjust the script execution process to ensure compatibility with their environment.
- **Dependencies**: The project uses **Pipenv** to manage dependencies. Make sure **Pipenv** is installed on your machine. If it isn't, you can install it with:
  ```bash
  pip install pipenv
  ```
- **Permissions**: Ensure that the mini-shell.sh script is executable. If not, you can make it executable using:
   ```bash
  chmod +x mini-shell.sh
   ```
## Acknowledgments
This project was built as part of the Codecrafters challenge, with all implementation done independently.

  
