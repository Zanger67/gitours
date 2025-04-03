import os
import subprocess
import ast
import openai
import json

def clone_repo(repo_url, destination="./sample_repo"):
    if os.path.exists(destination):
        print(f"Repo already exists at {destination}. Pulling latest changes...")
        subprocess.run(["git", "-C", destination, "pull"], check=True)
    else:
        print(f"Cloning {repo_url} into {destination}...")
        subprocess.run(["git", "clone", repo_url, destination], check=True)

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

def summarize_with_llm(summary):
    openai.api_key = os.getenv("OPENAI_API_KEY") 

    prompt = f"Summarize the following code structure:\n{json.dumps(summary, indent=2)}"  
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful code summarizer."},
                  {"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

def main():
    repo_url = input("Enter the GitHub repo URL: ")
    clone_repo(repo_url)

    repo_path = "./sample_repo"
    summary = analyze_repo(repo_path)
    
    if summary:
        llm_output = summarize_with_llm(summary)
        print("\n--- LLM Summary ---")
        print(llm_output)
    else:
        print("\nNo Python code found or failed to parse.")

if __name__ == "__main__":
    main()
