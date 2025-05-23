# from collections import deque

class InvalidUrlError(Exception):
    pass


_URL_TEMPLATE = 'https://github.com/{owner}/{repo}/{tree_const}/{branch}'
_URL_TEMPLATE_CLONING = 'https://github.com/{owner}/{repo}.git'

def clean_url(url: str) -> str :
    orig_url = url
    if 'github.com/' in url:
        url = url[url.find('github.com/') + len('github.com/'):]
    
    url = url.split('/')
    if url[-1].endswith('.git'):
        url[-1] = url[-1][:-4]
    
    if len(url) > 4 or len(url) < 2 :
        raise InvalidUrlError(f'URL is invalid: {orig_url}')  
    
    owner, repo, tree_const, branch = url + ['tree', 'main'][len(url) - 2:]
    
    return _URL_TEMPLATE.format(
        owner=owner,
        repo=repo,
        tree_const=tree_const,
        branch=branch
    )

def convert_git_url_to_cloner(url: str) -> str :
    """
    Converts a GitHub URL to a format suitable for cloning.
    """
    orig_url = url
    if 'github.com/' in url:
        url = url[url.find('github.com/') + len('github.com/'):]
    
    url = url.split('/')
    if url[-1].endswith('.git'):
        url[-1] = url[-1][:-4]
            
    if len(url) > 4 or len(url) < 2 :
        raise InvalidUrlError(f'URL is invalid: {orig_url}')  
    
    owner, repo, _, _ = url + ['tree', 'main'][len(url) - 2:]
    
    return _URL_TEMPLATE_CLONING.format(
        owner=owner,
        repo=repo,
    )
    
    
def main() -> None :
    test = 'https://github.com/indmdev/Free-Telegram-Store-Bot'
    test_err = 'https://github.com/indmdev/Free-Telegram-Store-Bot/smt/smt/smt'

    print(clean_url(test))

if __name__ == '__main__':
    main()