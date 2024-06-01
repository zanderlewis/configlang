import configparser
import sys

# Create a function to read and parse the configuration file
def read_config(file_path):
    config = configparser.ConfigParser(default_section=None)
    config.optionxform = str  # preserve case for keys
    config.read(file_path)
    return config

# Define a function to read code from a .cl file
def read_code(file_path):
    with open(file_path, 'r') as file:
        return file.read().splitlines()

# Define a simple interpreter
class SimpleInterpreter:
    def __init__(self, syntax):
        self.syntax = syntax
        self.functions = {}
        self.variables = {}

    def interpret(self, code):
        in_function_definition = False
        function_name = None
        function_code = []
        for line in code:
            if not line.strip():
                continue
            command, *command_args = line.split(maxsplit=1)
            if command == self.syntax['PRINT']:
                if in_function_definition:
                    function_code.append(line)
                else:
                    # Check if the command_args is a variable and print its value
                    if command_args[0] in self.variables:
                        print(self.variables[command_args[0]])
                    else:
                        print(' '.join(command_args))
            elif command == self.syntax['VAR_DEF']:
                var_name = command_args[0]
                self.variables[var_name] = None
            elif command == self.syntax['VAR_ASSIGN']:
                var_name, var_value = command_args
                self.variables[var_name] = var_value
            elif command == self.syntax['ARITHMETIC']:
                var_name, expression = ' '.join(command_args).split(maxsplit=1)
                result = eval(expression)
                # Store the result in a variable provided by the user
                self.variables[var_name] = result
            else:
                command_args = ' '.join(command_args)
                if command == self.syntax['FUNC_DEF']:
                    in_function_definition = True
                    function_name = command_args
                elif command == self.syntax['FUNC_END']:
                    in_function_definition = False
                    self.functions[function_name] = function_code
                    function_code = []
                elif command == self.syntax['FUNC_CALL']:
                    function_name = command_args
                    if function_name in self.functions:
                        self.interpret(self.functions[function_name])
                    else:
                        print(f"Unknown function: {function_name}")
                        sys.exit(1)
                else:
                    print(f"Unknown command: {line}")
                    sys.exit(1)

# Read the settings from the configuration file
config = read_config('cl.config')
syntax = {k: v for k, v in config.items('SYNTAX')}

# Read the code from a .cl file
code = read_code('code.cl')

# Create an interpreter and execute the code
interpreter = SimpleInterpreter(syntax)
interpreter.interpret(code)