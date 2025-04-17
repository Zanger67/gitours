import os
import ast
import json
import tempfile, shutil, subprocess
from collections import defaultdict
from tqdm import tqdm

from .repo_data import gitRepo

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
        "classes":   classes,
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
        if not isinstance(node, ast.Call):
            continue
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
            if not file.endswith(".py"):
                continue
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
    Build a dictionary mapping each symbol to a list of dictionaries
    containing its defining file and type (function, class, method, variable).
    """
    origin_map = defaultdict(list)
    for file, info in reference_map.items():
        defs = info.get("definitions", {})

        for symbol in defs.get("functions", []):
            origin_map[symbol].append({"file": file, "type": "function"})

        for symbol in defs.get("variables", []):
            origin_map[symbol].append({"file": file, "type": "variable"})

        for cls in defs.get("classes", []):
            origin_map[cls.get("name")].append({"file": file, "type": "class"})

            for method in cls.get("methods", []):
                origin_map[method].append({"file": file, "type": "method"})
    return origin_map


def generate_global_cross_reference(reference_map, usage_map):
    """
    For each symbol in the usage map, determine its origin and type,
    and return cross-reference entries that include file usage and symbol type.
    """
    origin_map = generate_origin_map(reference_map)
    cross_refs = []
    for symbol, usage_files in usage_map.items():
        if symbol not in origin_map:
            continue
        for usage_file in usage_files:
            for origin in origin_map[symbol]:
                origin_file = origin["file"]
                symbol_type = origin["type"]
                if usage_file != origin_file:
                    cross_refs.append({
                        "symbol": symbol,
                        "symbol_type": symbol_type,
                        "used_in": usage_file,
                        "defined_in": origin_file
                    })
    return cross_refs

def generate_repo_mappings(repo_url: str, save_record: bool = False) -> gitRepo :
    repo = gitRepo(repo_url=repo_url)
    
    temp_dir_outputs = tempfile.mkdtemp()
    print(f"Created temporary directory for outputs: {temp_dir_outputs}")

    file_names_temp = {
        'reference_map':    os.path.join(temp_dir_outputs, 'reference_map.json'),
        'usage_map':        os.path.join(temp_dir_outputs, 'usage_map.json'),
        'combined_map':     os.path.join(temp_dir_outputs, 'combined_map.json'),
        'cross_reference':  os.path.join(temp_dir_outputs, 'cross_reference.json')
    }
    
    # Local NONTEMP save if save_record is True for debugging
    file_names = {
        'reference_map':    os.path.join('data', 'reference_map.json'),
        'usage_map':        os.path.join('data', 'usage_map.json'),
        'combined_map':     os.path.join('data', 'combined_map.json'),
        'cross_reference':  os.path.join('data', 'cross_reference.json')
    }

    print("Analyzing project for definitions and imports...")
    reference_map = analyze_project(repo.tempdir)
    with open(file_names_temp['reference_map'], "w", encoding="utf-8") as f:
        json.dump(reference_map, f, indent=2)
    print(f"reference_map.json saved to {file_names_temp['reference_map']}")

    print("Analyzing project for usage information...")
    usage_map = analyze_usages(repo.tempdir)
    with open(file_names_temp['usage_map'], "w", encoding="utf-8") as f:
        json.dump(usage_map, f, indent=2)
    print(f"usage_map.json saved to {file_names_temp['usage_map']}")

    print("Combining reference and usage maps...")
    combined_map = combine_maps(reference_map, usage_map)
    with open(file_names_temp['combined_map'], "w", encoding="utf-8") as f:
        json.dump(combined_map, f, indent=2)
    print(f"combined_map.json saved to {file_names_temp['combined_map']}")

    print("Generating global cross-reference map...")
    cross_reference = generate_global_cross_reference(reference_map, usage_map)
    with open(file_names_temp['cross_reference'], "w", encoding="utf-8") as f:
        json.dump(cross_reference, f, indent=2)
    print(f"cross_reference.json saved to {file_names_temp['cross_reference']}")
        
    
    if save_record :
        print("Saving all maps to non-temp data directory...")
        if not os.path.exists('data') :
            os.mkdir('data')
        for key, value in file_names.items():
            shutil.copy(file_names_temp[key], value)
            print(f"Saved '{key}' to '{value}'")

    print("All maps have been successfully generated and saved!")
    print("Temporary output folder contents:")
    for file_name in os.listdir(temp_dir_outputs):
        print(f" - {file_name}")
    print()
    
    repo.set_mapping_path(temp_dir_outputs)
    
    return repo
        
        
        # print(f'{os.listdir(temp_dir_outputs) = }')
        
        # shutil.rmtree(temp_dir_outputs)
        # print("Temporary output folder cleaned up.")
        
    
    # return 

def main(repo_url: str) -> None :
    generate_repo_mappings(repo_url)

if __name__ == "__main__":
    # main()
    pass