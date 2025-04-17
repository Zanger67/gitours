
import json
import os
import shutil
import subprocess
import tempfile
from . import helpers



class gitRepo:
    def __init__(self, repo_url: str) -> None:
        '''
        Initialize the gitRepo object with a repository URL.
        
        Args:
            repo_url (str): The URL of the repository.
        Returns:
            str path to tempdir
            '''
        self._set_repo_url(repo_url)
        self._clone_repo()
        
        self.mapping_path = None
        
    def _clone_repo(self) -> None :
        self.tempdir = tempfile.mkdtemp()
        
        print(f"Cloning into temp directory: {self.tempdir}")
        
        try :
            subprocess.run(["git", "clone", self.repo_url, self.tempdir], check=True)
        except subprocess.CalledProcessError:
            print("Failed to clone the repository.")
            self._close()
            exit()
            
    def _close(self) -> None :
        '''
        Close the gitRepo object, cleaning up any resources.
        '''
        if hasattr(self, 'tempdir') and os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)
        if hasattr(self, 'mapping_path') and os.path.exists(self.mapping_path):
            shutil.rmtree(self.mapping_path)
        print(f"Removing temporary directory for cloning and maps:\n - {self.tempdir}\n - {self.mapping_path}")

    def save_repo_json_format(self, data: dict) -> None :
        if not hasattr(self, 'mapping_path') or self.mapping_path is None :
            raise ValueError("Mapping path is not set:", self.mapping_path)
        
        if not os.path.exists(self.mapping_path):
            os.mkdir(self.mapping_path)
            
        with open(os.path.join(self.mapping_path, 'repo_summary.json'), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
    def get_repo_json_data(self) -> dict :
        if not hasattr(self, 'mapping_path') or self.mapping_path is None :
            raise ValueError("Mapping path is not set:", self.mapping_path)
        
        with open(os.path.join(self.mapping_path, 'repo_summary.json'), "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return data

    def get_repo_path(self) -> str :
        return self.tempdir
    
    def set_mapping_path(self, mapping_path: str) -> None :
        self.mapping_path = mapping_path
        print(f"Mapping path set to: {self.mapping_path}")
        
    def get_mapping_path(self) -> str :
        return self.mapping_path
    
    def _set_repo_url(self, repo_url: str):
        self.repo_url = helpers.convert_git_url_to_cloner(repo_url)
    
    def get_url(self) -> str :
        return self.repo_url