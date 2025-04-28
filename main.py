# General imports


# Component imports
import json
import os
import shutil
from programs import helpers
from programs import itemizer
from programs import clone_summary as get_files
from programs.codetours import generate_codetour, parse_prompt_1

import dotenv










def main(override_url: str = None) -> None :
    dotenv.load_dotenv()

    # Obtain input github URL
    if override_url is not None :
        github_url = override_url
        print(f"Using provided URL: {github_url}")
    else :
        github_url = input("Enter the GitHub URL: ")
    print()


    # Clean the URL
    try:
        cleaned_url = helpers.convert_git_url_to_cloner(github_url)
        print(f"Cleaned clonable URL: {cleaned_url}")
    except helpers.InvalidUrlError as e:
        raise e
    print()
    
    
    # Clone repo data
    try :
        repo = itemizer.generate_repo_mappings(repo_url=cleaned_url, save_record=True)
        
        print(f'Mapping directories: {repo.get_mapping_path()}')
        print(f'Cloned repo path: {repo.get_repo_path()}')
        
        # with open(os.path.join(repo.get_mapping_path(), 'reference_map.json'), "r", encoding="utf-8") as f:
        #     reference_map = json.load(f)
            # print(json.dumps(reference_map, indent=2))
        
        print(f'Temp repo path: {repo.get_repo_path()}')
        print(f'Repo files: {os.listdir(repo.get_repo_path())}')
        
        get_files.get_repo_json_tempfile(repo)
        git_file_json = repo.get_repo_json_data()
        
        # print(f'File JSON: ')
        # print(json.dumps(git_file_json, indent=2))
        
        with open(os.path.join(repo.get_mapping_path(), 'cross_reference.json'), "r", encoding="utf-8") as f:
            cross_reference = json.load(f)
            # print(json.dumps(cross_reference, indent=2))
        
        llm_response_1 = get_files.summarize_with_llm_2(cross_ref_dict=cross_reference, 
                                                        repo_summary_dict=git_file_json)
        # print(get_files.summarize_with_llm(cross_reference))
        
        # print(f'LLM response: {llm_response_1}')
        codetour_data = parse_prompt_1(data=llm_response_1)
        
        codetour = generate_codetour(data=codetour_data, repo=repo)
        
        with open('temp_output_codetour.tour', "w", encoding="utf-8") as f:
            json.dump(codetour, f, indent=2)
        print(f'Codetour: {json.dumps(codetour, indent=2)}')
        
    finally :
        print('\nCleaning up temporary files...')
        repo._close()
        # if isinstance(repo.get_mapping_path(), str) and os.path.exists(repo.get_mapping_path()):
        #     print("Cleaning up temporary output folder...")
        #     # Clean up the temporary output folder
        #     shutil.rmtree(repo.get_mapping_path())
        #     print("Temporary output folder cleaned up.")
        # else :
        #     print("No temporary output folder to clean up.")
            
        # # Clean up the cloned repository
        # if isinstance(repo.get_repo_path(), str) and os.path.exists(repo.get_repo_path()):
        #     print("Cleaning up cloned repository...")
        #     shutil.rmtree(repo.get_repo_path())
        #     print("Cloned repository cleaned up.")
        # else :
        #     print("No cloned repository to clean up.")
            
        print()
        print(f'{os.path.exists(repo.get_mapping_path()) = }')
        print(f'{os.path.exists(repo.get_repo_path()) = }')
            
    
    

def tester() -> None :
    # test_url = 'https://github.com/indmdev/Free-Telegram-Store-Bot'
    # main(override_url=test_url)


    # test_err = 'https://github.com/indmdev/Free-Telegram-Store-Bot/smt/smt/smt'
    # main(override_url=test_err)    


    main()
    
if __name__ == '__main__':
    tester()
    # main()