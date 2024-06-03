import ast
import black
import os

def remove_comments_and_format(file_path):
    with open(file_path, "r") as source:
        tree = ast.parse(source.read())

    code_without_comments = ast.unparse(tree)

    formatted_code = black.format_str(code_without_comments, mode=black.FileMode())

    with open(file_path, "w") as source:
        source.write(formatted_code)

# Get all Python files in the 'configlang/' directory
python_files = [f for f in os.listdir('configlang/') if f.endswith('.py')]

# Call remove_comments_and_format on each Python file
for file in python_files:
    remove_comments_and_format(f"configlang/{file}")