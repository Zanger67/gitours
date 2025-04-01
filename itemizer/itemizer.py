import os
import ast
import json
from collections import defaultdict
from tqdm import tqdm

def extract_definitions(file_path):
    """
    Extract top-level definitions from a Python file:
      - Classes (and their methods)
      - Functions
      - Top-level variables
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        node = ast.parse(source, filename=file_path)
    except Exception:
        return None

    classes = []
    functions = []
    variables = []

    for n in node.body:
        if isinstance(n, ast.ClassDef):
            methods = [m.name for m in n.body if isinstance(m, ast.FunctionDef)]
            classes.append({"name": n.name, "methods": methods})
        elif isinstance(n, ast.FunctionDef):
            functions.append(n.name)
        elif isinstance(n, ast.Assign):
            for target in n.targets:
                if isinstance(target, ast.Name):
                    variables.append(target.id)

    return {
        "classes": classes,
        "functions": functions,
        "variables": variables
    }

def find_imports(file_path):
    """
    Uses modulefinder to list imported modules in a file.
    """
    from modulefinder import ModuleFinder
    finder = ModuleFinder()
    try:
        finder.run_script(file_path)
    except Exception:
        return []
    imports = []

    for name, mod in finder.modules.items():
        if mod.__file__ and mod.__file__.endswith(".py"):
            imports.append(name)
    return imports

def analyze_project(root_dir):
    """
    Walk through the project directory and build a reference map for each Python file.
    """
    reference_map = {}
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                abs_path = os.path.join(subdir, file)
                rel_path = os.path.relpath(abs_path, root_dir)
                defs = extract_definitions(abs_path)
                if defs is None:
                    continue
                imports = find_imports(abs_path)
                reference_map[rel_path] = {
                    "imports": imports,
                    "definitions": defs
                }
    return reference_map

def extract_usages(file_path):
    """
    Extract names used in function and method calls from a Python file.
    """
    usages = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)
    except Exception:
        return usages

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_node = node.func
            if isinstance(func_node, ast.Name):
                usages.append(func_node.id)
            elif isinstance(func_node, ast.Attribute):
                usages.append(func_node.attr)
    return usages

def analyze_usages(root_dir):
    """
    Walk through all Python files in the project directory and build a usage map.
    The usage map maps each used name to the set of files (relative paths) where it is called.
    """
    usage_map = defaultdict(set)
    for subdir, _, files in os.walk(root_dir):
        for file in tqdm(files, desc="Analyzing usages"):
            if file.endswith(".py"):
                abs_path = os.path.join(subdir, file)
                rel_path = os.path.relpath(abs_path, root_dir)
                names = extract_usages(abs_path)

                for name in names:
                    usage_map[name].add(rel_path)

    return {name: list(files) for name, files in usage_map.items()}

def combine_maps(reference_map, usage_map):
    """
    For each file in the reference map, add a 'usage' field that maps each defined name
    (functions, classes, methods, and variables) to the list of files where they are used.
    """
    combined = {}
    for file, info in reference_map.items():
        defs = info.get("definitions", {})
        combined[file] = {
            "imports": info.get("imports", []),
            "definitions": defs,
            "usage": {}
        }
        defined_names = defs.get("functions", []) + defs.get("variables", [])

        for cls in defs.get("classes", []):
            defined_names.append(cls.get("name"))
            defined_names.extend(cls.get("methods", []))

        for name in defined_names:
            combined[file]["usage"][name] = usage_map.get(name, [])

    return combined

def generate_origin_map(reference_map):
    """
    Build a dictionary mapping each symbol (functions, variables, classes, and methods)
    to a list of file(s) where it is defined.
    """
    origin_map = defaultdict(list)
    for file, info in reference_map.items():
        defs = info.get("definitions", {})

        for symbol in defs.get("functions", []):
            origin_map[symbol].append(file)

        for symbol in defs.get("variables", []):
            origin_map[symbol].append(file)

        for cls in defs.get("classes", []):
            origin_map[cls.get("name")].append(file)

            for method in cls.get("methods", []):
                origin_map[method].append(file)

    return origin_map

def generate_global_cross_reference(reference_map, usage_map):
    """
    For each symbol in the usage map, determine its origin using the origin map,
    and produce entries that indicate "File A uses symbol X from File B".
    """
    origin_map = generate_origin_map(reference_map)
    cross_refs = []
    for symbol, usage_files in usage_map.items():
        if symbol in origin_map:
            for usage_file in usage_files:
                for origin_file in origin_map[symbol]:
                    if usage_file != origin_file:
                        cross_refs.append({
                            "symbol": symbol,
                            "used_in": usage_file,
                            "defined_in": origin_file
                        })
    return cross_refs

if __name__ == "__main__":
    import tempfile, shutil, subprocess

    repo_url = 'https://github.com/indmdev/Free-Telegram-Store-Bot'
    temp_dir = tempfile.mkdtemp()
    print(f"Cloning into temp directory: {temp_dir}")

    try:
        subprocess.run(["git", "clone", repo_url, temp_dir], check=True)
        project_path = temp_dir
    except subprocess.CalledProcessError:
        print("Failed to clone the repository.")
        exit()

    print("Analyzing project for definitions and imports...")
    reference_map = analyze_project(project_path)
    with open("reference_map.json", "w", encoding="utf-8") as f:
        json.dump(reference_map, f, indent=2)
    print("reference_map.json saved.")

    print("Analyzing project for usage information...")
    usage_map = analyze_usages(project_path)
    with open("usage_map.json", "w", encoding="utf-8") as f:
        json.dump(usage_map, f, indent=2)
    print("usage_map.json saved.")

    print("Combining reference and usage maps...")
    combined_map = combine_maps(reference_map, usage_map)
    with open("combined_map.json", "w", encoding="utf-8") as f:
        json.dump(combined_map, f, indent=2)
    print("combined_map.json saved.")

    print("Generating global cross-reference map...")
    cross_reference = generate_global_cross_reference(reference_map, usage_map)
    with open("cross_reference.json", "w", encoding="utf-8") as f:
        json.dump(cross_reference, f, indent=2)
    print("cross_reference.json saved.")

    shutil.rmtree(temp_dir)
    print("Temporary repo folder cleaned up.")
    print("All maps have been successfully generated and saved!")