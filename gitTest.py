import os
from git import Repo
COMMITS_TO_PRINT = 5


def print_commit(commit):
    print('----')
    print(str(commit.hexsha))
    print("\"{}\" by {} ({})".format(commit.summary,
                                     commit.author.name,
                                     commit.author.email))
    print(str(commit.authored_datetime))
    print(str("count: {} and size: {}".format(commit.count(),
                                              commit.size)))

def print_repository(repo):
    print('Repo description: {}'.format(repo.description))
    print('Repo active branch is {}'.format(repo.active_branch))
    for remote in repo.remotes:
        print('Remote named "{}" with URL "{}"'.format(remote, remote.url))
    print('Last commit for repo is {}.'.format(str(repo.head.commit.hexsha)))

if __name__ == "__main__":
    repo_local_path = os.getenv('NORSK_SAMPLE_CODE_PATH')
    repo_git_url = os.getenv('NORSK_SAMPLE_CODE_GIT_URL')
    ok = True

    if repo_local_path and repo_git_url :

        # Repo object used to programmatically interact with Git repositories
        if os.path.isdir(repo_local_path) :      # if repo exists, pull newest data 
            repo = Repo(repo_local_path) 
            repo.remotes.origin.pull()  # this assumes that git url is valid, which it may not be tk
        else:                           # otherwise, clone from remote
            repo = Repo.clone_from(repo_git_url, repo_local_path)
                                
        # repo = Repo(repo_local_path)
        # check that the repository loaded correctly
        if not repo.bare:
            print('Repo at {} successfully loaded.'.format(repo_local_path))
            print_repository(repo)
            # create list of commits then print some of them to stdout
            commits = list(repo.iter_commits('main'))[:COMMITS_TO_PRINT]
            for commit in commits:
                print_commit(commit)
                pass
        else:
            print('Could not load repository at {} :('.format(repo_local_path))
            ok = False
    else:
        print('Seomething wrong at {} and or ... :('.format(repo_local_path))
        ok = False

    if ok :
        excerptsFilePath = os.path.join(repo_local_path, "excerpts.csv")
        with open(excerptsFilePath, 'r', encoding='UTF-8') as file:
            while (line := file.readline().rstrip()):
                print(line)
        
