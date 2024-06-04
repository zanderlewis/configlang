import sys


def interpret_print(line, syntax, variables):
    _, *command_args = line.split(None, 1)
    if command_args:
        arg = command_args[0]
        if syntax["STR"] in arg:
            str_var_name = arg[
                arg.index(syntax["OPEN_PAREN"]) + 1 : arg.index(syntax["CLOSE_PAREN"])
            ]
            if str_var_name in variables:
                arg = arg.replace(
                    f"{syntax['STR']}{syntax['OPEN_PAREN']}{str_var_name}{syntax['CLOSE_PAREN']}",
                    str(variables[str_var_name]),
                )
            else:
                print(f"Unknown variable: {str_var_name}")
                sys.exit(1)
        if syntax["CONCAT"] in arg:
            strings_to_concat = [
                string.strip() for string in arg.split(syntax["CONCAT"])
            ]
            strings_to_concat = [
                (
                    str(variables[string])
                    if string in variables
                    else (
                        string[1:-1]
                        if string.startswith('"') and string.endswith('"')
                        else string
                    )
                )
                for string in strings_to_concat
            ]
            print("".join(strings_to_concat))
        elif arg in variables:
            if isinstance(variables[arg], (int, float, bool)):
                print(variables[arg])
            else:
                print(str(variables[arg]))
        elif arg.startswith('"') and arg.endswith('"'):
            print(arg[1:-1])
        else:
            print(arg)
