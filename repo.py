import os
from glob import glob
from re import sub as re_sub
from git import Repo, exc

class DTLRepo:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
        
    def __init__(self, args, repo_path, exception_handler):
        self.handle = exception_handler
        self.yaml_extensions = ['yaml', 'yml']
        self.url = args.url
        self.repo_path = repo_path
        self.branch = args.branch
        self.repo = Repo()
        self.cwd = os.getcwd()
        
        if os.path.isdir(self.repo_path):
            self.pull_repo()
        else:
            self.clone_repo()
    
    def get_relative_path(self):
        return self.repo_path
    
    def get_absolute_path(self):
        return os.path.join(self.cwd, self.repo_path)
    
    def slug_format(self, name):
        return re_sub('\W+','-', name.lower())
        
    def pull_repo(self):
        try:
            print("Package devicetype-library is already installed, "
                    + f"updating {self.get_absolute_path()}")
            self.repo = Repo(self.repo_path)
            if not self.repo.remotes.origin.url.endswith('.git'):
                self.handle.exception("GitInvalidRepositoryError", self.repo.remotes.origin.url, f"Origin URL {self.repo.remotes.origin.url} does not end with .git")
            self.repo.remotes.origin.pull()
            self.repo.git.checkout(self.branch)
            print(f"Pulled Repo {self.repo.remotes.origin.url}")
        except exc.GitCommandError as git_error:
            self.handle.exception("GitCommandError", self.repo.remotes.origin.url, git_error)
        except Exception as git_error:
            self.handle.exception("Exception", 'Git Repository Error', git_error)
        
    def clone_repo(self):
        try:
            self.repo = Repo.clone_from(self.url, self.get_absolute_path(), branch=self.branch)
            print(f"Package Installed {self.repo.remotes.origin.url}")
        except exc.GitCommandError as git_error:
            self.handle.exception("GitCommandError", self.url, git_error)
        except Exception as git_error:
            self.handle.exception("Exception", 'Git Repository Error', git_error)

    def get_files(self, vendors:list = None):
        files = []
        discovered_vendors = []
        base_path = './repo/device-types/'
        if vendors:
            for r, d, f in os.walk(base_path):
                for folder in d:
                    for vendor in vendors:
                        if vendor.lower() == folder.lower():
                            discovered_vendors.append({'name': folder,
                                                    'slug': self.slug_format(folder)})
                            for extension in self.yaml_extensions:
                                files.extend(glob(base_path + folder + f'/*.{extension}'))
        else:
            for r, d, f in os.walk(base_path):
                for folder in d:
                    if folder.lower() != "Testing":
                        discovered_vendors.append({'name': folder,
                                                'slug': self.slug_format(folder)})
            for extension in self.yaml_extensions:
                files.extend(glob(base_path + f'[!Testing]*/*.{extension}'))
        return files, discovered_vendors
