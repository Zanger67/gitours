# General imports


# Component imports
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
        cleaned_url = helpers.clean_url(github_url)
        print(f"Cleaned URL: {cleaned_url}")
    except helpers.InvalidUrlError as e:
        raise e
    print()
    
    
    # Clone repo data
    itemizer.generate_repo_mappings(cleaned_url)
    
    
    
    pass

def tester() -> None :
    test_url = 'https://github.com/indmdev/Free-Telegram-Store-Bot'
    main(override_url=test_url)


    # test_err = 'https://github.com/indmdev/Free-Telegram-Store-Bot/smt/smt/smt'
    # main(override_url=test_err)    


if __name__ == '__main__':
    tester()
    # main()