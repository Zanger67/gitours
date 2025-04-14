



from cmath import inf
import json
import os

from programs.repo_data import gitRepo


def parse_prompt_1(data: str, attempt: int = 5) -> list :
    """
    Parse the prompt data for the first prompt for the key information.
    """
    if attempt <= 0 :
        print("Max attempts reached. Exiting.")
        return []
    
    try :
        data_dict = json.loads(data)
    except json.JSONDecodeError as e :
        print(f"Error decoding JSON on try {attempt}: {e}")
        print("Retrying...")
        return parse_prompt_1(data, attempt - 1)
    
    parsed_data = []
    
    for file_name_path, file_sums in data_dict.items() :
        for section, sec_data in file_sums.items() :
            ord_num, start_line, end_line, summary, core = (
                sec_data.get('RECOMMENDED_ORDER_NUMBER', None),
                sec_data.get('STARTING_LINE_NUMBER', None),
                sec_data.get('LINE_NUMBER_END', None),
                sec_data.get('SUMMARY', None),
                sec_data.get('CORE', False)
            )
            
            if not core :
                continue
            if summary is None :
                print(f"Summary is None for {file_name_path} in section {section}.")
                continue
            if start_line is None or end_line is None :
                print(f"Start or end line is None for {file_name_path} in section {section}.")
                continue                
            if ord_num is None :
                ord_num = inf

            parsed_data.append({
                'path':         file_name_path,
                'line_start':   start_line,
                'line_end':     end_line,
                'summary':      summary,
                'order':        ord_num,
            })
    
    return parsed_data

def generate_codetour(data: list, repo: gitRepo) -> dict :
    """
    Generate the codetour from the parsed data.
    """
    codetour = {
        "$schema": "https://aka.ms/codetour-schema",
        "title": "Your generated codetour!",
        "description": "This is your AI generated codetour of your provided GitHub repository! Please follow the steps one by one to get a wholisitic understanding of your chosen repo.",
        "steps": []
    }
    
    data.sort(key=lambda x: x.get('order', inf))
    
    steps = codetour['steps']
    steps.append({
        'description': "## 👋 Welcome to your AI generated codetour!\nPlease proceed by clicking and following the series of \"next\"s to proceed through your project!",
    })
    
    for item in data :
        step = {
            'description':  item['summary'],
        }
        if 'path' in item and os.path.exists(os.path.join(repo.get_repo_path(), item['path'])) :
            step['file'] = item['path']
        else :
            print('Path not found for item:', item)
        if 'line_start' in item :
            step['line'] = int(item['line_start'])
        steps.append(step)
    
    return codetour