import sys


def interpret_var(line, syntax, variables):
    _, *a = line.split(maxsplit=2)
    var_name, var_value = (a[0], " ".join(a[1:]))
    if var_value.startswith('"') and var_value.endswith('"'):
        var_value = var_value[1:-1]
    elif var_value.startswith(syntax["STR"] + syntax["OPEN_PAREN"]) and var_value.endswith(syntax["CLOSE_PAREN"]):
        var_value = var_value[len(syntax["STR"]) + 1 : -1]
    elif syntax["STR"] in var_value:
        str_var_name = var_value[var_value.index(syntax["OPEN_PAREN"]) + 1 : var_value.index(syntax["CLOSE_PAREN"])]
        if str_var_name in variables:
            var_value = var_value.replace(
                f"{syntax['STR']}{syntax["OPEN_PAREN"]}{str_var_name}{syntax["CLOSE_PAREN"]}", str(variables[str_var_name])
            )
        else:
            print(f"Unknown variable: {str_var_name}")
            sys.exit(1)
    variables[var_name] = var_value
    if syntax["CONCAT"] in var_value:
        strings_to_concat = var_value.split(syntax["CONCAT"])
        strings_to_concat = [string.strip() for string in strings_to_concat]
        for i, string in enumerate(strings_to_concat):
            if string in variables:
                strings_to_concat[i] = str(variables[string])
            elif string.startswith('"') and string.endswith('"'):
                strings_to_concat[i] = string[1:-1]
        variables[var_name] = "".join(strings_to_concat)
    elif var_value.startswith('"') and var_value.endswith('"'):
        variables[var_name] = var_value[1:-1]
    elif var_value in variables:
        variables[var_name] = variables[var_value]
    else:
        try:
            variables[var_name] = int(var_value)
        except ValueError:
            try:
                variables[var_name] = float(var_value)
            except ValueError:
                if var_value.lower() == "true":
                    variables[var_name] = True
                elif var_value.lower() == "false":
                    variables[var_name] = False
                else:
                    variables[var_name] = var_value
    return variables
