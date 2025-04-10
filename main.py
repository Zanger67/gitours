# General imports


# Component imports
import shutil
from itemizer import helpers
from itemizer import itemizer











def main(override_url: str = None) -> None :

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
    mapping_dirs = itemizer.generate_repo_mappings(repo_url=cleaned_url, save_record=True)
    
    print(f'Mapping directories: {mapping_dirs}')
    
    
    
    shutil.rmtree(mapping_dirs)
    print("Temporary output folder cleaned up.")
    
    
    pass

def tester() -> None :
    test_url = 'https://github.com/indmdev/Free-Telegram-Store-Bot'
    main(override_url=test_url)


    # test_err = 'https://github.com/indmdev/Free-Telegram-Store-Bot/smt/smt/smt'
    # main(override_url=test_err)    


if __name__ == '__main__':
    tester()
    # main()