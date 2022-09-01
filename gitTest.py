import os
import re
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
    
    # keep track of 
        # list of files to be examined
        # accumulated output - a copy of the file with code excerpts interpolated in
        # map of the completed excerpts keyed on file name and excerptid - value being a list of content lines
        # map of the open excerpts keyed on file name and excerptid - - value being a list of content lines

    filesToBeExamined = []
    accumulatedOutput = []
    completedExcerptsMap = {}
    openExcerptsMap = {}
    filesToSearchMap = {}
    
    ok = True

    
    if 1 == 2: 
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
        # open the template file and get a list of files that excerpts need to be retrieved from 
        reTemplateExcerpt = r'^\[excerpt](.+)\[\/excerpt]'
        reStartExcerpt  =  r'^#.*?\[excerpt\s*(.+)\]'
        reEndExcerpt =  r'^#.*?\[\/excerpt\s*(.+)\]'
        errorState = None
                
        # assume for the moment that the template file is in the same repo as code samples
        templateFile = os.path.join(repo_local_path, "UserGuide.md")
        with open(templateFile, 'r', encoding='UTF-8') as file:
            while (bool(lineIn := file.readline()) and (errorState is None)):

                print(f"lineIn: {lineIn}")

                line = lineIn.strip()
                match = re.search(reTemplateExcerpt, line)
                if match:
                    excerptContents = match.groups()[0]
                    print('found', excerptContents)
                    # add this file to the map, if it does not already exist
                    splitDetails = excerptContents.split(",")
                    if len(splitDetails) == 2:
                        fileName = splitDetails[0].strip()
                        excerptID = splitDetails[1].strip()
                        print(f"file is: {fileName}, excerpt id is : {excerptID}")

                        existingExcerpts = filesToSearchMap.get(fileName)
                        excerpts = [excerptID]
                        if existingExcerpts: 
                            print ("Do we never get to here?")
                            print(f"Existing excerpts: {existingExcerpts}")
                            existingExcerpts.append(excerptID)
                        else: 
                            filesToSearchMap[fileName] = excerpts

                    else:
                        errorState = f"Could not split contents of excerpt tag {excerptContents}"

        print("Iterating map")

        if errorState is None:
        
            for i in filesToSearchMap:
                extracts = filesToSearchMap.get(i)
                print(f"file: {i}, excerpts: {extracts}")

            #  we have a list of files to extract excerpts from
            for codeFile in filesToSearchMap:
                codeFilePath = os.path.join(repo_local_path, codeFile)

                with open(codeFilePath, 'r', encoding='UTF-8') as file:
                    while (bool(lineIn := file.readline()) and (errorState is None)):

                        print(f"lineInCode: {lineIn}")

                        line = lineIn.strip()
                    
                        match = re.search(reStartExcerpt, line)
                        if match:
                            excerptContents = match.groups()[0]
                            excerptID = excerptContents.strip()
                            
                            print(f"Start excerpt for {excerptContents}")
                            # add excerpt id to openExcerptsMap
                            openExcerpt = openExcerptsMap.get(excerptID)
                            if openExcerpt: 
                                msg = (f"openExcerpt: {excerptID} already exists")
                                print(msg)
                                errorState = msg
                            else: 
                                # check that this excerptID is not in the closed map
                                closedExcerpt = completedExcerptsMap.get(excerptID)
                                if closedExcerpt: 
                                    msg = (f"closedExcerpt: {excerptID} already exists in completed map")
                                    print(msg)
                                    errorState = msg
                                else: 
                                    openExcerptsMap[excerptID] = []

                        else:
                            match = re.search(reEndExcerpt, line)
                            if match:
                                excerptContents = match.groups()[0]
                                print(f"End excerpt for {excerptContents}")
                                openExcerptLines = openExcerptsMap.get(excerptID)
                                if openExcerptLines: 
                                    completedExcerptsMap[excerptID] = openExcerptLines
                                    del openExcerptsMap[excerptID]
                                else:
                                    msg = (f"openExcerpt: {excerptID} could not be found - probably never opened in the first place)")
                                    print(msg)
                                    errorState = msg 

                            else:
                                print(f"standard content {excerptContents}")
                                # add this line to any open excerpts
                                for excerptID in openExcerptsMap:
                                    openExcerptsMap[excerptID].append (line)

        if errorState is None: 

            # all code files have been read and excerpts extracted - check that there are no open excerpts left
            if len(openExcerptsMap) > 0: 
                stillOpenList = []
                for k in openExcerptsMap.keys():
                    stillOpenList.append (k)
                
                keyStr = ", ".join(stillOpenList)
                    
                errorState = f"The following excerpts were not correctly closed: {keyStr}"
        
        # still to do is to incorporate the file name into the map structure for excerpts tk
        if errorState is None: 
            '# now iterate through the user guide creating another copy with extracts inserted'
            with open(templateFile, 'r', encoding='UTF-8') as file:
                while (bool(lineIn := file.readline()) and (errorState is None)):

                    print(f"lineIn: {lineIn}")

                    line = lineIn.rstrip()
                    match = re.search(reTemplateExcerpt, line)
                    if match:
                        excerptContents = match.groups()[0]
                        print('found', excerptContents)
                        # add this file to the map, if it does not already exist
                        splitDetails = excerptContents.split(",")
                        if len(splitDetails) == 2:
                            fileName = splitDetails[0].strip()
                            excerptID = splitDetails[1].strip()
                            print(f"file is: {fileName}, excerpt id is : {excerptID}")
                            # copy over the contents of this excerpt into the accumulator
                            hh = completedExcerptsMap.get(excerptID)
                            if hh:
                                for l in hh:
                                    accumulatedOutput.append(l)
                            else:
                                errorState = f"could not find excerpt contents for {excerptID}"


                            
                        else:
                            errorState = f"Could not split contents of excerpt tag {excerptContents} this would be unusual as we have already iterated over this file"
                    else:
                        # append this line to the accumulator
                        accumulatedOutput.append(line)

        if errorState is None:

            guideStr = "\n".join(accumulatedOutput)
            print(guideStr)
        else:
            print(f"There was a problem: {errorState}")
            
        print ("END")
        # excerptsFilePath = os.path.join(repo_local_path, "excerpts.csv")
        # with open(excerptsFilePath, 'r', encoding='UTF-8') as file:
        #     while (line := file.readline().rstrip()):
        #         print(line)

                # start excerpt ^#.+?\[excerpt\s*(.+)\]
                # end excerpt  ^#.+?\[\/excerpt\s*(.+)\]
                  
        
