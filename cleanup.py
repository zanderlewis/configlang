import ast
import black

def remove_comments_and_format(file_path):
    with open(file_path, "r") as source:
        tree = ast.parse(source.read())

    code_without_comments = ast.unparse(tree)

    formatted_code = black.format_str(code_without_comments, mode=black.FileMode())

    with open(file_path, "w") as source:
        source.write(formatted_code)

remove_comments_and_format("main.py")