import configparser
import sys
import importlib
import argparse


def read_config(file_path):
    config = configparser.ConfigParser(default_section=None)
    config.optionxform = str
    config.read(file_path)
    defaults = {
        "LANG_SETTINGS": {"file_extension": "cfgl"},
        "SYNTAX": {
            "PRINT": "print",
            "VAR_DEF": "var",
            "VAR_ASSIGN": "set",
            "ARITHMETIC": "calc",
            "STR": "str",
            "CONCAT": "++",
            "IMPORT_LIB": "import",
            "FUNC_DEF": "def",
            "FUNC_END": "end",
            "FUNC_CALL": "call",
            "SLC": "#",
            "AS": "as",
        },
    }
    for section, section_defaults in defaults.items():
        if section not in config:
            config[section] = {}
        for key, value in section_defaults.items():
            if key not in config[section]:
                config[section][key] = value
    return config


def read_code(file_path):
    with open(file_path, "r") as file:
        return file.read().splitlines()


class SimpleInterpreter:

    def __init__(self, syntax):
        self.syntax = syntax
        self.functions = {}
        self.variables = {}
        self.libraries = {}

    def interpret(self, code):
        in_function_definition = False
        function_name = None
        function_code = []
        for line in code:
            if self.syntax["SLC"] in line:
                line = line[: line.index(self.syntax["SLC"])]
            if not line.strip():
                continue
            command, *command_args = line.split(None, 1)
            if command == self.syntax["PRINT"]:
                if in_function_definition:
                    function_code.append(line)
                else:
                    if command_args and self.syntax["STR"] in command_args[0]:
                        str_var_name = command_args[0][
                            command_args[0].index("(") + 1 : command_args[0].index(")")
                        ]
                        if str_var_name in self.variables:
                            command_args[0] = command_args[0].replace(
                                f"{self.syntax['STR']}({str_var_name})",
                                str(self.variables[str_var_name]),
                            )
                        else:
                            print(f"Unknown variable: {str_var_name}")
                            sys.exit(1)
                    if self.syntax["CONCAT"] in command_args[0]:
                        strings_to_concat = command_args[0].split(self.syntax["CONCAT"])
                        strings_to_concat = [
                            string.strip() for string in strings_to_concat
                        ]
                        for i, string in enumerate(strings_to_concat):
                            if string in self.variables:
                                strings_to_concat[i] = self.variables[string]
                            elif string.startswith('"') and string.endswith('"'):
                                strings_to_concat[i] = string[1:-1]
                        print("".join(strings_to_concat))
                    elif command_args[0] in self.variables:
                        print(self.variables[command_args[0]])
                    elif command_args[0].startswith('"') and command_args[0].endswith(
                        '"'
                    ):
                        print(command_args[0][1:-1])
                    else:
                        print(" ".join(command_args))
            elif command == self.syntax["VAR_DEF"]:
                var_name = command_args[0]
                self.variables[var_name] = None
            elif command == self.syntax["VAR_ASSIGN"]:
                if len(command_args) >= 1:
                    _, *a = line.split(maxsplit=2) 
                    var_name, var_value = a[0], ' '.join(a[1:])
                    # Check if the value is a string enclosed in quotes
                    if var_value.startswith('"') and var_value.endswith('"'):
                        var_value = var_value[1:-1]  # Remove the quotes
                    # Check if the value is a string enclosed in the str function
                    elif var_value.startswith(self.syntax["STR"] + "(") and var_value.endswith(")"):
                        var_value = var_value[len(self.syntax["STR"])+1:-1]  # Remove the str function
                    elif self.syntax["STR"] in var_value:
                        str_var_name = var_value[
                            var_value.index("(") + 1 : var_value.index(")")
                        ]
                        if str_var_name in self.variables:
                            var_value = var_value.replace(
                                f"{self.syntax['STR']}({str_var_name})",
                                str(self.variables[str_var_name]),
                            )
                        else:
                            print(f"Unknown variable: {str_var_name}")
                            sys.exit(1)
                    self.variables[var_name] = var_value
                    if self.syntax["CONCAT"] in var_value:
                        strings_to_concat = var_value.split(self.syntax["CONCAT"])
                        strings_to_concat = [string.strip() for string in strings_to_concat]
                        for i, string in enumerate(strings_to_concat):
                            if string in self.variables:
                                strings_to_concat[i] = self.variables[string]
                            elif string.startswith('"') and string.endswith('"'):
                                strings_to_concat[i] = string[1:-1]
                        self.variables[var_name] = "".join(strings_to_concat)
                    elif var_value.startswith('"') and var_value.endswith('"'):
                        self.variables[var_name] = var_value[1:-1]
                    elif var_value in self.variables:
                        self.variables[var_name] = self.variables[var_value]
                    else:
                        try:
                            self.variables[var_name] = int(var_value)
                        except ValueError:
                            try:
                                self.variables[var_name] = float(var_value)
                            except ValueError:
                                if var_value.lower() == "true":
                                    self.variables[var_name] = True
                                elif var_value.lower() == "false":
                                    self.variables[var_name] = False
                                else:
                                    self.variables[var_name] = var_value
                else:
                    print(f"Invalid variable assignment: {line}")
                    sys.exit(1)
            elif command == self.syntax["ARITHMETIC"]:
                var_name, expression = " ".join(command_args).split(maxsplit=1)
                for var_name in self.variables:
                    expression = expression.replace(
                        var_name, str(self.variables[var_name])
                    )
                result = eval(expression)
                self.variables[var_name] = result
            elif command == self.syntax["IMPORT_LIB"]:
                import_statement = command_args[0]
                if " as " in import_statement:
                    lib_name, alias = import_statement.split(f" {self.syntax["AS"]} ")
                    try:
                        self.libraries[alias] = importlib.import_module(lib_name)
                    except ImportError:
                        print(f"Failed to import library: {lib_name}")
                        sys.exit(1)
                else:
                    lib_name = import_statement
                    try:
                        self.libraries[lib_name] = importlib.import_module(lib_name)
                    except ImportError:
                        print(f"Failed to import library: {lib_name}")
                        sys.exit(1)
            else:
                command_args = ' '.join(command_args).split()
                if command == self.syntax["FUNC_DEF"]:
                    in_function_definition = True
                    function_name, *function_args = command_args
                    self.functions[function_name] = {"args": function_args, "code": []}
                elif command == self.syntax["FUNC_END"]:
                    in_function_definition = False
                    self.functions[function_name]["code"] = function_code
                    function_code = []
                elif command == self.syntax["FUNC_CALL"]:
                    function_name, *function_args = command_args
                    if function_name in self.functions:
                        function = self.functions[function_name]
                        function_args = [self.variables[arg] if arg in self.variables else arg for arg in function_args]
                        if len(function_args) != len(function["args"]):
                            print(f"Function {function_name} expects {len(function['args'])} arguments, but got {len(function_args)}.")
                            sys.exit(1)
                        old_variables = self.variables.copy()
                        self.variables.update(dict(zip(function["args"], function_args)))
                        self.interpret(function["code"])
                        self.variables = old_variables
                    elif "." in function_name:
                        lib_name, func_name = function_name.split(".")
                        if lib_name in self.libraries and hasattr(self.libraries[lib_name], func_name):
                            func = getattr(self.libraries[lib_name], func_name)
                            function_args = [self.variables[arg] if arg in self.variables else arg for arg in function_args]
                            if function_args:  # Check if function_args is not empty
                                result = func(*function_args)  # Call the function with all function_args
                                self.variables['RESULT'] = result  # Set RESULT to the result of the function call
                        else:
                            print(f"Unknown function: {function_name}")
                            sys.exit(1)
                    else:
                        print(f"Unknown function: {function_name}")
                        sys.exit(1)
                else:
                    print(f"Unknown command: {line}")
                    sys.exit(1)


config = read_config("cfgl.config")
lang_settings = {k: v for k, v in config.items("LANG_SETTINGS")}
parser = argparse.ArgumentParser()
parser.add_argument("file_path", type=str, help="Path to the file to interpret")
args = parser.parse_args()
try:
    with open(args.file_path, "r") as file:
        file.read()
except FileNotFoundError:
    print("File not found.")
    sys.exit(1)
if not args.file_path.endswith(f".{lang_settings['file_extension']}"):
    print(
        f"Invalid file extension. Only {lang_settings['file_extension']} files are supported."
    )
    sys.exit(1)
syntax = {k: v for k, v in config.items("SYNTAX")}
code = read_code(args.file_path)
interpreter = SimpleInterpreter(syntax)
interpreter.interpret(code)
