import configparser
import sys


def read_config(file_path):
    config = configparser.ConfigParser(default_section=None)
    config.optionxform = str
    config.read(file_path)
    return config


def read_code(file_path):
    with open(file_path, "r") as file:
        return file.read().splitlines()


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
            if command == self.syntax["PRINT"]:
                if in_function_definition:
                    function_code.append(line)
                else:
                    if self.syntax["STR"] in command_args[0]:
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
                var_name, var_value = (command_args[0], command_args[1])
                if self.syntax["STR"] in var_value:
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
                    self.variables[var_name] = var_value
            elif command == self.syntax["ARITHMETIC"]:
                var_name, expression = " ".join(command_args).split(maxsplit=1)
                for var_name in self.variables:
                    expression = expression.replace(
                        var_name, str(self.variables[var_name])
                    )
                result = eval(expression)
                self.variables[var_name] = result
            elif command == self.syntax["CONCAT"]:
                strings_to_concat = command_args[0].split("++")
                strings_to_concat = [string.strip() for string in strings_to_concat]
                for i, string in enumerate(strings_to_concat):
                    if string in self.variables:
                        strings_to_concat[i] = self.variables[string]
                    elif string.startswith('"') and string.endswith('"'):
                        strings_to_concat[i] = string[1:-1]
                print("".join(strings_to_concat))
            else:
                command_args = " ".join(command_args)
                if command == self.syntax["FUNC_DEF"]:
                    in_function_definition = True
                    function_name = command_args
                elif command == self.syntax["FUNC_END"]:
                    in_function_definition = False
                    self.functions[function_name] = function_code
                    function_code = []
                elif command == self.syntax["FUNC_CALL"]:
                    function_name = command_args
                    if function_name in self.functions:
                        self.interpret(self.functions[function_name])
                    else:
                        print(f"Unknown function: {function_name}")
                        sys.exit(1)
                else:
                    print(f"Unknown command: {line}")
                    sys.exit(1)


config = read_config("cl.config")
syntax = {k: v for k, v in config.items("SYNTAX")}
code = read_code("code.cfgl")
interpreter = SimpleInterpreter(syntax)
interpreter.interpret(code)
