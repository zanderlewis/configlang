import sys


def interpret_print(line, syntax, variables):
    command, *command_args = line.split(None, 1)
    if command_args and syntax["STR"] in command_args[0]:
        str_var_name = command_args[0][
            command_args[0].index("(") + 1 : command_args[0].index(")")
        ]
        if str_var_name in variables:
            command_args[0] = command_args[0].replace(
                f"{syntax['STR']}({str_var_name})", str(variables[str_var_name])
            )
        else:
            print(f"Unknown variable: {str_var_name}")
            sys.exit(1)
    if syntax["CONCAT"] in command_args[0]:
        strings_to_concat = command_args[0].split(syntax["CONCAT"])
        strings_to_concat = [string.strip() for string in strings_to_concat]
        for i, string in enumerate(strings_to_concat):
            if string in variables:
                strings_to_concat[i] = variables[string]
            elif string.startswith('"') and string.endswith('"'):
                strings_to_concat[i] = string[1:-1]
        print("".join(strings_to_concat))
    elif command_args[0] in variables:
        print(variables[command_args[0]])
    elif command_args[0].startswith('"') and command_args[0].endswith('"'):
        print(command_args[0][1:-1])
    else:
        print(" ".join(command_args))
