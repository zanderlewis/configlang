def interpret_arithmetic(line, syntax, variables):
    _, *command_args = line.split(maxsplit=1)
    var_name, expression = " ".join(command_args).split(maxsplit=1)
    for var_name in variables:
        expression = expression.replace(var_name, str(variables[var_name]))
    result = eval(expression)
    variables[var_name] = result
    return variables
