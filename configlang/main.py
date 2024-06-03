import configparser
import sys
import argparse
import var
import arith
import print as p
import import_lib
import functions as f


def read_config(file_path):
    config = configparser.ConfigParser(default_section=None)
    config.optionxform = str
    config.read(file_path)
    defaults = {
        "LANG_SETTINGS": {"file_extension": "cfgl"},
        "SYNTAX": {
            "PRINT": "print",
            "VAR": "var",
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


class Interpreter:

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
                    p.interpret_print(line, self.syntax, self.variables)
            elif command == self.syntax["VAR"]:
                if len(command_args) >= 1:
                    self.variables = var.interpret_var(
                        line, self.syntax, self.variables
                    )
            elif command == self.syntax["ARITHMETIC"]:
                self.variables = arith.interpret_arithmetic(
                    line, self.syntax, self.variables
                )
            elif command == self.syntax["IMPORT_LIB"]:
                self.libraries = import_lib.interpret_import(
                    line, self.syntax, self.libraries
                )
            else:
                command_args = " ".join(command_args).split()
                if command == self.syntax["FUNC_DEF"]:
                    (
                        self.functions,
                        in_function_definition,
                        function_name,
                        function_code,
                    ) = f.interpret_func_def(line, self.syntax, self.functions)
                elif command == self.syntax["FUNC_END"]:
                    (
                        self.functions,
                        in_function_definition,
                        function_name,
                        function_code,
                    ) = f.interpret_func_end(
                        line, self.syntax, self.functions, function_name, function_code
                    )
                elif command == self.syntax["FUNC_CALL"]:
                    function_name, *function_args = command_args
                    if function_name in self.functions:
                        function = self.functions[function_name]
                        function_args = [
                            self.variables[arg] if arg in self.variables else arg
                            for arg in function_args
                        ]
                        if len(function_args) != len(function["args"]):
                            print(
                                f"Function {function_name} expects {len(function['args'])} arguments, but got {len(function_args)}."
                            )
                            sys.exit(1)
                        old_variables = self.variables.copy()
                        self.variables.update(
                            dict(zip(function["args"], function_args))
                        )
                        self.interpret(function["code"])
                        self.variables = old_variables
                    elif "." in function_name:
                        lib_name, func_name = function_name.split(".")
                        if lib_name in self.libraries and hasattr(
                            self.libraries[lib_name], func_name
                        ):
                            func = getattr(self.libraries[lib_name], func_name)
                            function_args = [
                                self.variables[arg] if arg in self.variables else arg
                                for arg in function_args
                            ]
                            if function_args:
                                result = func(*function_args)
                                self.variables["RESULT"] = result
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
interpreter = Interpreter(syntax)
interpreter.interpret(code)
