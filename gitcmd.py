from git import Repo, exc
from sys import exit as system_exit
import settings

def pull_repo(path: str, branch: str):
    try:
        repo = Repo(path)
        if not repo.remotes.origin.url.endswith('.git'):
            settings.handle_exception("GitInvalidRepositoryError", repo.remotes.origin.url, f"Origin URL {repo.remotes.origin.url} does not end with .git")
        repo.remotes.origin.pull()
        repo.git.checkout(branch)
        print(f"Pulled Repo {repo.remotes.origin.url}")
    except exc.GitCommandError as git_error:
        settings.handle_exception("GitCommandError", repo.remotes.origin.url, git_error)
    except Exception as git_error:
        settings.handle_exception("Exception", 'Git Repository Error', git_error)
    
def clone_repo(url: str, clone_path: str, branch: str):
    try:
        return Repo.clone_from(url, clone_path, branch=branch)
    except exc.GitCommandError as git_error:
        settings.handle_exception("GitCommandError", url, git_error)
    except Exception as git_error:
        settings.handle_exception("Exception", 'Git Repository Error', git_error)
