import os
import subprocess
import ast
import openai
import json

from .repo_data import gitRepo

SYSTEM_DEF_PROMPT = '''
You are a GitHub repository summarizer. You will be presented with 2 JSON files for context and reference containing 1. a mapping of all python symbols present in the project mapped to their location and usages, and 2. a json containing all the contents of the project including all python code. 

You evaluate the contents of a project based on the files provided to you and return summaries of each method, important variable, class, etc.
'''

PROMPT_ONE = '''
You are a GitHub repository summarizer. You will be presented with 2 JSON files for context and reference containing 1. a mapping of all python symbols present in the project mapped to their location and usages, and 2. a json containing all the contents of the project including all python code. 

You evaluate the contents of a project based on the files provided to you and return summaries of each method, important variable, class, etc. in the following JSON-consistent format:

{
    "FILE_NAME_AND_PATH_RELATIVE_TO_ROOT": {
        "STARTING_LINE_NUMBER": {
            "RECOMMENDED_ORDER_NUMBER": INTEGER,
            "STARTING_LINE_NUMBER": INTEGER
            "LINE_NUMBER_END": INTEGER,
            "SUMMARY": "INSERT SUMMARY HERE",
            "CORE": BOOLEAN
        },
        ...
    },
    ...
}

Mark summary items that you deem "essential" or "more important" with a TRUE boolean value in the "CORE" attribute. Note that "RECOMMENDED_ORDER_NUMBER" is a number you can assign to each summary item to indicate the order in which they should be presented if presented in a powerpoint style presentation based on what you believe is the best relative order to present them in.

Summarize all the contents including every file present.



The first JSON context file is by the name of "cross_reference.json" containing a list of all python symbols present in a github project and their mappings to usages and source definitions. "cross_reference.json" is in the following format:

[
    {
        "symbol": "PYTHON_ATTRIBUTE_OR_METHOD_NAME",
        "symbol_type": "method",
        "used_in": "RELATIVE_PATH_FROM_GITHUB_ROOT_OF_CALLER_PYTHON_FILE",
        "defined_in": "RELATIVE_PATH_FROM_GITHUB_ROOT_OF_DEFINITION_PYTHON_FILE"
    },
    ...
]


The second JSON context file is by the name of "repo_summary.json" containing a dictionary of each file present in the project, their file types, and their contents if they are a python file. "repo_summary.json" is in the following format:

{
    "RELATIVE_PATH_FROM_GITHUB_ROOT": {
        "path": "RELATIVE_PATH_FROM_GITHUB_ROOT",
        "name": "FILE_NAME",
        "type": "FILE_EXTENSION",
        "content": "ALL TEXT CONTENTS WITHIN FILE IF THE FILE IS A PYTHON DOCUMENT"
    },
    ...
}

'''

# def clone_repo(repo_url, destination="./sample_repo"):
#     if os.path.exists(destination):
#         print(f"Repo already exists at {destination}. Pulling latest changes...")
#         subprocess.run(["git", "-C", destination, "pull"], check=True)
#     else:
#         print(f"Cloning {repo_url} into {destination}...")
#         subprocess.run(["git", "clone", repo_url, destination], check=True)

def extract_definitions(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        node = ast.parse(source, filename=file_path)
    except Exception as e:
        print(f"Failed to parse {file_path}: {e}")
        return None

    classes = []
    functions = []

    for n in node.body:
        if isinstance(n, ast.ClassDef):
            methods = [m.name for m in n.body if isinstance(m, ast.FunctionDef)]
            classes.append({"name": n.name, "methods": methods})
        elif isinstance(n, ast.FunctionDef):
            functions.append(n.name)

    return {"classes": classes, "functions": functions}

def analyze_repo(repo_path):
    summary = {}
    
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                definitions = extract_definitions(file_path)
                if definitions:
                    summary[rel_path] = definitions

    return summary

def get_repo_json_tempfile(repo: gitRepo) -> gitRepo:
    # if isinstance(repo_path, gitRepo):
    #     repo_path = repo_path.get_repo_path()
    
    summary = {}
    repo_path = repo.get_repo_path()
    
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, repo_path)
            
            split_file_name = os.path.splitext(file)
            if split_file_name[1] in ['.py']:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    summary[rel_path] = {
                        'path': rel_path,
                        'name': file,
                        'type': split_file_name[1],
                        'content': content
                    }
            elif split_file_name[1] in ['.jpeg', '.jpg', '.png']:
                summary[rel_path] = {
                    'path': rel_path,
                    'name': file,
                    'type': split_file_name[1],
                }
    repo.save_repo_json_format(summary)
    # tempfile_path = 
    return repo

def summarize_with_llm(summary):
    openai.api_key = os.getenv("OPENAI_API_KEY") 

    prompt = f"""Summarize the following code structure:\n{json.dumps(summary, indent=2)}"""
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a helpful code summarizer."},
                  {"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

def summarize_with_llm_2(cross_ref_dict: list, repo_summary_dict: dict) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY") 

    prompt = PROMPT_ONE + f"""\n\n
        The JSON context files are as follows:
        cross_reference.json:
        {json.dumps(cross_ref_dict)}

        repo_summary.json:
        {json.dumps(repo_summary_dict)}
    """
    
    with open('temp_output_PROMPT.txt', 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    response = openai.ChatCompletion.create(
        model="o3-mini",              # 200k token limit
        # model="chatgpt-4o-latest",      # 500k token limit
        messages=[{"role": "system", "content": SYSTEM_DEF_PROMPT},
                  {"role": "user", "content": prompt}]
    )
    
    resp_text = response['choices'][0]['message']['content']
    
    with open('temp_output_RESPONSE.txt', 'w', encoding='utf-8') as f:
        f.write(resp_text)

    return resp_text


def main(git_repo: gitRepo = None):
    if git_repo is None:
        repo_url = input("Enter the GitHub repo URL: ")
        git_repo = gitRepo(repo_url)
    # clone_repo(gitRepo.get_repo_path)

    # repo_path = "./sample_repo"
    repo_path = git_repo.get_repo_path()
    summary = analyze_repo(repo_path)
    
    if summary:
        llm_output = summarize_with_llm(summary)
        print("\n--- LLM Summary ---")
        print(llm_output)
    else:
        print("\nNo Python code found or failed to parse.")

if __name__ == "__main__":
    main()
