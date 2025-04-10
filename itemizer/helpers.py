# from collections import deque

class InvalidUrlError(Exception):
    pass


_URL_TEMPLATE = 'https://github.com/{owner}/{repo}/{tree_const}/{branch}'

def clean_url(url: str) -> str :
    orig_url = url
    if 'github.com/' in url:
        url = url[url.find('github.com/') + len('github.com/'):]
    
    url = url.split('/')
    
    if len(url) > 4 or len(url) < 2 :
        raise InvalidUrlError(f'URL is invalid: {orig_url}')  
    
    owner, repo, tree_const, branch = url + ['tree', 'main'][len(url) - 2:]
    
    return _URL_TEMPLATE.format(
        owner=owner,
        repo=repo,
        tree_const=tree_const,
        branch=branch
    )
    
    
    
def main() -> None :
    # test = 'https://github.com/indmdev/Free-Telegram-Store-Bot'
    test = 'https://github.com/indmdev/Free-Telegram-Store-Bot/smt/smt/smt'

    print(clean_url(test))

if __name__ == '__main__':
    main()