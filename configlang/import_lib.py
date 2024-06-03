import importlib
import sys


def interpret_import(line, syntax, libraries):
    command, *command_args = line.split(None, 1)
    import_statement = command_args[0]
    if syntax["AS"] in import_statement:
        lib_name, alias = import_statement.split(f" {syntax['AS']} ")
        try:
            libraries[alias] = importlib.import_module(lib_name)
        except ImportError:
            print(f"Failed to import library: {lib_name}")
            sys.exit(1)
    else:
        lib_name = import_statement
        try:
            libraries[lib_name] = importlib.import_module(lib_name)
        except ImportError:
            print(f"Failed to import library: {lib_name}")
            sys.exit(1)
    return libraries
