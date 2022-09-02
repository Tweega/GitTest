import getopt
import sys
import os
import re
from git import Repo

PROGRAM = "ProgamName tbd"
VERSION = '0.1'
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

cachedFiles = {}
errorState = None

if __name__ == "__main__":
    cachedFiles.clear()
    reTemplateExcerpt = r'.*?\[excerpt](.+)\[\/excerpt]'
    reStartExcerpt  =  r'.*?\[excerpt\s*(.+)\]'
    reEndExcerpt = r'.*?\[\/excerpt\s*(.+)\]'
    reExcerpt = f"{reStartExcerpt}|{reEndExcerpt}"
        
    filesToBeExamined = []
    accumulatedOutput = []
    completedExcerptsMap = {}
    openExcerptsMap = {}
    filesToSearchMap = {}
    # errorState = "Debugging for now"

    
    print (f'ARGV: {sys.argv[1:]}')

    # the arguments that I want are 
        # sample code path
        # git repo (optional?)
        # training manual file name (template)
        # comment string
        # verbose?
        # error log path?

    options, remainder = getopt.getopt(sys.argv[1:], 'p:g:t:o:vh', ['codepath=', 
                                                        'gitrepo=',
                                                        'template=',
                                                        'outputpath=',
                                                        'strip',
                                                        'version',
                                                        'help',
                                                        'verbose',
                                                        ])

    repo_path = os.getenv('NORSK_SAMPLE_CODE_PATH')
    repo_git_url = os.getenv('NORSK_SAMPLE_CODE_GIT_URL')
    template_file = "media_proto.html"
    output_path = r"~/work/python/hello"
    verbose = True
    comment = "#"
    strip = False

    def getFileLines(file_name, cache=False): # cache would be for when getting data from git
        err = None

        cachedLines = cachedFiles.get(file_name)
        if cachedLines:
            return cachedLines, err
        else:
            # assume source is file for the moment
            fileLines = []
            if repo_path != "":
                file_path = os.path.join(repo_path, file_name)
                with open(file_path, 'r', encoding='UTF-8') as file:
                    while (bool(lineIn := file.readline())):
                        line = lineIn.rstrip()
                        fileLines.append(line)
            elif repo_git_url != "":
                # load file lines direct from git repo tbd
                print ("tbd")
            else:
                err = f"unable to load file: {file_name}"
            
            if (err is None) and cache:
                cachedFiles[file_name] = fileLines

            return fileLines, err
        

    def saveTextFile(fileText, outPath):
        vPrint(fileText)
        vPrint(f"Saving to : {outPath}")
        print ("saveTextFile to be done")

    def vPrint(str):
        if verbose:
            print(f"{str}\n")

    for opt, arg in options:
        if opt in ('-p', '--codepath'):
            repo_path = arg            
        elif opt in ('-g', '--gitrepo'):
            repo_git_url = arg
        elif opt in ('-t', '--template'):
            template_file = arg
            verbose = True
        elif opt in ('-o', '--outputpath'):
            output_path = arg
        elif opt in ('-s', '--strip'):
            strip = True
        elif opt in ('-v', '--version'):
            errorState = f"Version: {PROGRAM}: {VERSION}"
        elif opt in ('-h', '--help'):
            usageLines = ["programName.py",
            "options: ", 
            "-p, --codepath : the local path to code repository. Required unless --strip flag is specified, in which case only strip operation performed",
            "-g, --gitrepo: the url to git repo to extract code examples from. (optional?)",
            "-t, --template: the file into which excerpts should be inserted",
            "-o, --output: the path (if only file name supplied, repo_path is assumed as directory) to file to save result of interpolating template with excerpts (or directory to copy stripped files into)",
            "-s, --strip: Strips files listed in template file of [excerpt] markup and copies to --output directory.",
            "-v, --version: prints version of this program (the program does not execute when this option is provided)",
            "-h, --help: displays this usage text (the program does not execute when this option is provided)"
            ]
            usage = "\n".join(usageLines)
            errorState = f"usage: {usage}"            
        elif opt in ('--verbose'):
            verbose = True
    
    if not(os.path.isdir(repo_path)):
        # this will probably change so that either file path or git repo should be specified as alternative file access mechanisms
        errorState = "Unable to access code path: {repo_path}"

    
    print (repo_path)
    print (repo_git_url)
    print (template_file)
    print (verbose)
    print (comment)

    # keep track of 
        # list of files to be examined
        # accumulated output - a copy of the file with code excerpts interpolated in
        # map of the completed excerpts keyed on file name and excerptid - value being a list of content lines
        # map of the open excerpts keyed on file name and excerptid - - value being a list of content lines

    if errorState is None : 
        if repo_git_url :
            try:
                action = "pull"
                if os.path.isdir(repo_path) :   # we actually need to check if git initialised yet tk
                    repo = Repo(repo_path) 
                    repo.remotes.origin.pull()  # this assumes that git url is valid, which it may not be tk
                else:         
                    action = "clone" 
                    repo = Repo.clone_from(repo_git_url, repo_path)
            except Exception as e:
                msg = str(e)
                errorState = f"Error occured when interacting with git.  Action: {action}.  Error: {msg}"

                                    
            # repo = Repo(repo_path)
            # check that the repository loaded correctly
            if errorState is None:
                if not repo.bare:
                    vPrint('Repo at {} successfully loaded.'.format(repo_path))
                    print_repository(repo)
                    # create list of commits then print some of them to stdout
                    commits = list(repo.iter_commits('main'))[:COMMITS_TO_PRINT]
                    for commit in commits:
                        print_commit(commit)
                        pass
                else:
                    errMsg = 'Could not load repository at {} :('.format(repo_path)
                    errorState = errMsg
        

    if errorState is None :
        # open the template file and get a list of files that excerpts need to be retrieved from 
                
        # assume for the moment that the template file is in the same repo as code samples
        templateFile = os.path.join(repo_path, template_file)
        fileLines, errorState = getFileLines(templateFile, True)
        numLines = len(fileLines)
        lineIndex = 0
        while ((lineIndex < numLines) and (errorState is None)):
            line = fileLines[lineIndex]
            lineIndex += 1
            
            vPrint(f"lineIn: {line}")

            match = re.search(reTemplateExcerpt, line)
            if match:
                excerptContents = match.groups()[0]
                vPrint(f"found, {excerptContents}")
                # add this file to the map, if it does not already exist
                splitDetails = excerptContents.split(",")
                if len(splitDetails) == 2:
                    codeFile = splitDetails[0].strip()
                    excerptID = splitDetails[1].strip()
                    excerptKey = ":".join([codeFile, excerptID])
                        
                    vPrint(f"excerpt key is : {excerptKey}")

                    existingExcerpts = filesToSearchMap.get(codeFile)
                    excerpts = [excerptKey]
                    if existingExcerpts: 
                        vPrint(f"Existing excerpts: {existingExcerpts}")
                        existingExcerpts.append(excerptKey)
                    else: 
                        filesToSearchMap[codeFile] = excerpts

                else:
                    errorState = f"Could not split contents of excerpt tag {excerptContents}"

        vPrint("Iterating map")

        if errorState is None:
        
            for i in filesToSearchMap:
                extracts = filesToSearchMap.get(i)
                vPrint(f"file: {i}, excerpts: {extracts}")

            #  we have a list of files to extract excerpts from
            for codeFile in filesToSearchMap:
                codeFilePath = os.path.join(repo_path, codeFile)
                
                fileLines, errorState = getFileLines(codeFilePath, strip) # if stripping coode files then keep in cache
                numLines = len(fileLines)
                lineIndex = 0
                while ((lineIndex < numLines) and (errorState is None)):
                    line = fileLines[lineIndex]
                    lineIndex += 1
                    vPrint(f"lineInCode: {line}")
                
                    match = re.search(reStartExcerpt, line)
                    if match:
                        excerptContents = match.groups()[0]
                        excerptID = excerptContents.strip()
                        excerptKey = ":".join([codeFile, excerptID])
                        
                        vPrint(f"Start excerpt for {excerptContents}")
                        # add excerpt id to openExcerptsMap
                        openExcerpt = openExcerptsMap.get(excerptKey)
                        if openExcerpt: 
                            msg = (f"openExcerpt: {excerptKey} already exists")
                            errorState = msg
                        else: 
                            # check that this excerptID is not in the closed map
                            closedExcerpt = completedExcerptsMap.get(excerptKey)
                            if closedExcerpt: 
                                msg = (f"closedExcerpt: {excerptKey} already exists in completed map")
                                errorState = msg
                            else: 
                                vPrint(f"adding excerptKey: {excerptKey}")
                                openExcerptsMap[excerptKey] = []

                    else:
                        match = re.search(reEndExcerpt, line)
                        if match:
                            excerptContents = match.groups()[0]
                            excerptID = excerptContents.strip()                                
                            excerptKey = ":".join([codeFile, excerptID])
                        
                            vPrint(f"End excerpt for {excerptKey}")
                            openExcerptLines = openExcerptsMap.get(excerptKey)
                            if openExcerptLines: 
                                completedExcerptsMap[excerptKey] = openExcerptLines
                                del openExcerptsMap[excerptKey]
                            else:
                                msg = (f"openExcerpt: {excerptKey} could not be found - probably never opened in the first place)")
                                errorState = msg 

                        else:
                            vPrint(f"standard content {excerptContents}")
                            # add this line to any open excerpts
                            for exKey in openExcerptsMap:
                                openExcerptsMap[exKey].append (line)

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
            fileLines, errorState = getFileLines(templateFile)
            numLines = len(fileLines)
            lineIndex = 0
            while ((lineIndex < numLines) and (errorState is None)):
                line = fileLines[lineIndex]
                lineIndex += 1
            
                vPrint(f"lineIn: {line}")

                match = re.search(reTemplateExcerpt, line)
                if match:
                    excerptContents = match.groups()[0]
                    vPrint(f"found, {excerptContents}")
                    # add this file to the map, if it does not already exist
                    splitDetails = excerptContents.split(",")
                    if len(splitDetails) == 2:
                        codeFile = splitDetails[0].strip()
                        excerptID = splitDetails[1].strip()
                        excerptKey = ":".join([codeFile, excerptID])
                        
                        vPrint(f"excerpt key is : {excerptKey}")
                        # copy over the contents of this excerpt into the accumulator
                        excerptLines = completedExcerptsMap.get(excerptKey)
                        if excerptLines:
                            for l in excerptLines:
                                accumulatedOutput.append(l)
                        else:
                            errorState = f"could not find excerpt contents for {excerptKey}"
                        
                    else:
                        errorState = f"Could not split contents of excerpt tag {excerptContents} this would be unusual as we have already iterated over this file"
                else:
                    # append this line to the accumulator
                    accumulatedOutput.append(line)

        if errorState is None:
            guideStr = "\n".join(accumulatedOutput)
            saveTextFile(guideStr, "some file name")
            strip = True #DEBUG ONLY remove tbd
            if strip: 
                excerptFilter = lambda l: not(bool(re.search(reExcerpt, line)))
                for codeFile in filesToSearchMap:
                    codeFilePath = os.path.join(repo_path, codeFile)
            
                    codeLines, errorState = getFileLines(codeFilePath)
                    strippedLines = filter(excerptFilter, codeLines)
                    strippedText = "\n".join(strippedLines)
                    outPath = os.path.join(output_path, codeFile)

                    saveTextFile(strippedText, outPath)



        else:
            print(f"There was a problem: {errorState}")
            
        print ("END")
        # excerptsFilePath = os.path.join(repo_path, "excerpts.csv")
        # with open(excerptsFilePath, 'r', encoding='UTF-8') as file:
        #     while (line := file.readline().rstrip()):
        #         print(line)

                # start excerpt ^#.+?\[excerpt\s*(.+)\]
                # end excerpt  ^#.+?\[\/excerpt\s*(.+)\]
                
        