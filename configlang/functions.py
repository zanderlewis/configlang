def interpret_func_def(line, syntax, functions):
    command_args = line.split()[1:]
    function_name, *function_args = command_args
    functions[function_name] = {"args": function_args, "code": []}
    return (functions, True, function_name, [])


def interpret_func_end(line, syntax, functions, function_name, function_code):
    functions[function_name]["code"] = function_code
    return (functions, False, None, [])
