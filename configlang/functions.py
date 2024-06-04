def interpret_func_def(line, syntax, functions):
    command_args = line.split(' ', 1)[1]
    if syntax['OPEN_PAREN'] in command_args:
        function_name, function_args = command_args.split(syntax['OPEN_PAREN'])
        function_args = [arg.strip() for arg in function_args.rstrip(syntax['CLOSE_PAREN']).split(',')]
    else:
        function_name = command_args
        function_args = []
    functions[function_name] = {"args": function_args, "code": []}
    return (functions, True, function_name, [])

def interpret_func_end(line, syntax, functions, function_name, function_code):
    functions[function_name]["code"] = function_code
    return (functions, False, None, [])