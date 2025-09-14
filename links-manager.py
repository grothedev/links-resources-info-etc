#!/bin/python3

#a tool to manage the links and resources
# basically a CRUD program for json, sqlite, or postgres, with a REPL interface by default, and optional args to skip user interaction
#  

import readline
import argparse
import sys

class SimpleREPL:
    def __init__(self):
        self.prompt = ">> "
        self.commands = {
            "help": self._show_help,
            "exit": self._exit_repl,
            "quit": self._exit_repl, # Alias for exit
            "echo": self._echo,
            # Add more commands here
            # "my_command": self._handle_my_command,
        }
        # Application-specific state can be initialized here
        # self.app_state = {}

    def _show_help(self, *args):
        """Displays available commands."""
        print("Available commands:")
        for cmd, func in self.commands.items():
            docstring = func.__doc__ or "No description available."
            print(f"  {cmd:<15} - {docstring.strip().splitlines()[0]}") # Show first line of docstring
        return None # No printable result for help

    def _exit_repl(self, *args):
        """Exits the REPL."""
        print("Exiting REPL. Goodbye!")
        sys.exit(0)

    def _echo(self, *args):
        """Echoes the input arguments back to the user.
        Usage: echo <arg1> <arg2> ...
        """
        if not args:
            return "Echo: Nothing to echo!"
        return "Echo: " + " ".join(args)

    # --- Placeholder for your custom commands ---
    # def _handle_my_command(self, arg1, arg2=None, *other_args):
    #     """
    #     Description of my_command.
    #     Usage: my_command <required_arg> [optional_arg] ...
    #     """
    #     # Your command logic here
    #     # Example:
    #     # self.app_state['something'] = arg1
    #     # return f"Processed {arg1} and {arg2}"
    #     pass


    def evaluate(self, line):
        """Evaluates a single line of input."""
        parts = line.strip().split()
        if not parts:
            return None # Empty line

        command_name = parts[0].lower() # Case-insensitive command matching
        args = parts[1:]

        if command_name in self.commands:
            command_func = self.commands[command_name]
            try:
                return command_func(*args)
            except TypeError as e:
                # Catch errors related to incorrect number of arguments
                return f"Error: Invalid arguments for '{command_name}'. Usage: {command_func.__doc__ or ''}"
            except Exception as e:
                return f"Error executing '{command_name}': {e}"
        else: #todo check for partial str match
            
            return f"Unknown command: '{command_name}'. Type 'help' for available commands."

    def run(self):
        """Runs the REPL main loop."""
        print("Welcome to SimpleREPL! Type 'help' for commands or 'exit' to quit.")
        while True:
            try:
                line = input(self.prompt)
                if line.strip(): # Process only if line is not empty
                    result = self.evaluate(line)
                    if result is not None: # Print only if there's a result
                        print(result)
            except EOFError: # Ctrl+D
                print("\nExiting REPL (EOF).")
                break
            except KeyboardInterrupt: # Ctrl+C
                print("\nInterrupted. Type 'exit' or 'quit' to exit.")
                # Optionally, you might want to clear any partial input here
                # or reset some state if an operation was interrupted.
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                # Depending on severity, you might want to break or continue


def parseArgs():
    parser = argparse.ArgumentParser(description='a tool to manage the links database')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose')
    parser.add_argument('-i', '--input', type=str, required=True, help='input file')
    parser.add_argument('-o', '--output', type=str, required=False, help='output file')
    args = parser.parse_args()
    return args

def main():
    parser = argparse.ArgumentParser(description='the program does a thing')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose')
    parser.add_argument('-i', '--input', type=str, required=True, help='input file')
    parser.add_argument('-d', '--database', type=str, required=False, help='database file or type')
    parser.add_argument('-a', '--add', action='store_true', help='add a link to the database')
    parser.add_argument('-r', '--remove', action='store_true', help='remove a link from the database')
    parser.add_argument('-l', '--list', action='store_true', help='list all links in the database')
    parser.add_argument('-s', '--search', type=str, required=False, help='search the database for a link')
    parser.add_argument('-u', '--update', type=str, required=False, help='update a link in the database')
    args = parser.parse_args()

    print(f"Input file: {args.input}")
    if args.output:
        print(f"Output file: {args.output}")

    #
    repl_app = SimpleREPL()
    repl_app.run()

if __name__ == '__main__':
    main()