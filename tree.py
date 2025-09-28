import os

ignore_dirs = {'venv', '__pycache__','.git'}

def print_tree(root='.', indent=""):
    entries = sorted(os.listdir(root))
    for i, item in enumerate(entries):
        if item in ignore_dirs:
            continue
        path = os.path.join(root, item)
        connector = "└── " if i == len(entries) - 1 else "├── "
        if os.path.isdir(path):
            print(f"{indent}{connector}{item}/")
            print_tree(path, indent + ("    " if i == len(entries) - 1 else "│   "))
        else:
            print(f"{indent}{connector}{item}")

print_tree(".")
