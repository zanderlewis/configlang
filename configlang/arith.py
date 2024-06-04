def interpret_arithmetic(line, syntax, variables):
    _, *command_args = line.split(maxsplit=1)
    var_name, expression = " ".join(command_args).split(maxsplit=1)
    for var_name in variables:
        if isinstance(variables[var_name], (int, float, bool)):
            expression = expression.replace(var_name, str(variables[var_name]))
    result = eval(expression)
    if isinstance(result, (int, float, bool)):
        variables[var_name] = result
    return variables
