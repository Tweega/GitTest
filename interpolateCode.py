import getopt
import sys
import os
import re
import shutil
import tempfile
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

    options, remainder = getopt.getopt(sys.argv[1:], 'p:g:b:t:o:vh', ['codepath=', 
                                                        'gitrepo=',
                                                        'gitbranch',
                                                        'template=',
                                                        'outputpath=',
                                                        'strip',
                                                        'version',
                                                        'help',
                                                        'verbose',
                                                        ])

    repoPath = os.getenv('NORSK_SAMPLE_CODE_PATH')
    outputPath = os.getenv('NORSK_SAMPLE_OUTPUT_PATH')
    repoGitUrl = os.getenv('NORSK_SAMPLE_CODE_GIT_URL')
    templateFile = "media_proto.html" #DEBUG ONLY tk
    verbose = True
    strip = False
    useTempDir = False
    repoGitBranch = "main"

    def getFileLines(fileName, cache=False): # cache would be for when getting data from git
        errorMsg = None
        try:
            cachedLines = cachedFiles.get(fileName)
            if cachedLines:
                return cachedLines, errorMsg
            else:
                # assume source is file for the moment
                fileLines = []
                if repoPath != "":
                    filePath = os.path.join(repoPath, fileName)
                    with open(filePath, 'r', encoding='UTF-8') as file:
                        while (bool(lineIn := file.readline())):
                            line = lineIn.rstrip()
                            fileLines.append(line)
                else:
                    errorMsg = f"unable to load file: {fileName}"
                
                if (errorMsg is None) and cache:
                    cachedFiles[fileName] = fileLines

                return fileLines, errorMsg
        except Exception as e:
                msg = str(e)
                errorMsg = f"Error occured in getFileLines: {msg}"
        return [], errorMsg
            

    def saveTextFile(fileText, outPath):
        # vPrint(fileText)
        vPrint(f"Saving to : {outPath}")
        errorMsg = None
        try:
            with open(outPath, 'w') as f:
                f.write(fileText)
        except Exception as e:
                msg = str(e)
                errorMsg = f"Error occured when saving output file. {msg}"
        errorMsg
            

    def vPrint(str):
        if verbose:
            print(f"{str}\n")

    for opt, arg in options:
        if opt in ('-p', '--codepath'):
            repoPath = arg            
        elif opt in ('-g', '--gitrepo'):
            repoGitUrl = arg
        elif opt in ('-b', '--gitbranch'):
            repoGitBranch = arg
        elif opt in ('-t', '--template'):
            templateFile = arg
            verbose = True
        elif opt in ('-o', '--outputpath'):
            outputPath = arg
        elif opt in ('-s', '--strip'):
            strip = True
        elif opt in ('-v', '--version'):
            errorState = f"Version: {PROGRAM}: {VERSION}"
        elif opt in ('-h', '--help'):
            usageLines = ["usage", "programName.py",
            "options: ", 
            "-p, --codepath : the local path to code repository. (Required unless --gitrepo provided).  Alternatively set env variable NORSK_SAMPLE_CODE_PATH",
            "-g, --gitrepo: the url to git repo to extract code examples from. (optional).  Alternatively set env variable NORSK_SAMPLE_CODE_GIT_URL",
            "-b, --gitbranch: defaults to main, and currently only used when no codepath supplied",
            "-t, --template: the file into which excerpts should be inserted (required)",
            "-o, --outputpath: directory to save output files into(required). Alternatively set env variable NORSK_SAMPLE_OUTPUT_PATH",
            "-s, --strip: Strips files listed in template file of [excerpt] markup and copies to --outputpath directory.",
            "-v, --version: prints version of this program (the program does not execute when this option is provided)",
            "-h, --help: displays this usage text (the program does not execute when this option is provided)"
            ]
            errorState = "\n".join(usageLines)            
        elif opt in ('--verbose'):
            verbose = True
    
    if repoPath and not(os.path.isdir(repoPath)):
        errorState = f"Unable to access code path: {repoPath}"

    if not outputPath:
        errorState = "--outputpath must be specified"
    else:
        if outputPath == repoPath:
            errorState = "Repo path and output path should not be the same otherwise files may be overwritten"
        elif not(os.path.isdir(outputPath)):
            errorState = f"Unable to access output path: {outputPath}"

    if not repoPath:
        if not repoGitUrl:
            errorState = "One of --gitrepo or --repopath must be provided"
        else:
            # Create temporary dir
            repoPath = tempfile.mkdtemp()
            useTempDir = True
            # # Clone into temporary dir
            # git.Repo.clone_from('stack@127.0.1.7:/home2/git/stack.git', t, branch='master', depth=1)
            # # Copy desired file from temporary dir
            # shutil.move(os.path.join(t, 'setup.py'), '.')
            # # Remove temporary dir
            # shutil.rmtree(t)
        
    
    vPrint (f"repoPath: {repoPath}")
    vPrint (f"repoGitUrl: {repoGitUrl}")
    vPrint (f"repoGitBranch: {repoGitBranch}")
    vPrint (f"templateFile: {templateFile}")
    vPrint (f"outputPath: {outputPath}")
    vPrint (f"verbose: {verbose}")

    if errorState is None : 
        if repoGitUrl :
            try:
                action = "clone"
                if useTempDir:   # we actually need to check if git initialised yet tk
                    repo = Repo.clone_from(repoGitUrl, repoPath, branch=repoGitBranch, depth=1)
                else:
                    action = "pull" 
                    repo = Repo(repoPath) 
                    repo.remotes.origin.pull() 
                    # checkout specific branch?     
                    
            except Exception as e:
                msg = str(e)
                errorState = f"Error occured when interacting with git.  Action: {action}.  Error: {msg}"
                                    
            # repo = Repo(repoPath)
            # check that the repository loaded correctly
            if errorState is None:
                if not repo.bare:
                    vPrint('Repo at {} successfully loaded.'.format(repoPath))
                    print_repository(repo)
                    # create list of commits then print some of them to stdout
                    commits = list(repo.iter_commits(repoGitBranch))[:COMMITS_TO_PRINT]
                    for commit in commits:
                        print_commit(commit)
                        pass
                else:
                    errMsg = 'Could not load repository at {} :('.format(repoPath)
                    errorState = errMsg
        

    if errorState is None :
        # open the template file and get a list of files that excerpts need to be retrieved from 
                
        # assume for the moment that the template file is in the same repo as code samples
        templateFilePath = os.path.join(repoPath, templateFile)
        fileLines, errorState = getFileLines(templateFilePath, True)
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
                codeFilePath = os.path.join(repoPath, codeFile)
                
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
            fileLines, errorState = getFileLines(templateFilePath)
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
            codeFilePath = os.path.join(outputPath, templateFile)
            errorState = saveTextFile(guideStr, codeFilePath)

            if errorState is None:
                if strip: 
                    excerptFilter = lambda l: not(bool(re.search(reExcerpt, l)))
                    for codeFile in filesToSearchMap:
                        if errorState is None:
                            codeFilePath = os.path.join(repoPath, codeFile)
                    
                            codeLines, errorState = getFileLines(codeFilePath)
                            strippedLines = filter(excerptFilter, codeLines)
                            strippedText = "\n".join(strippedLines)
                            outPath = os.path.join(outputPath, codeFile)

                            errorState = saveTextFile(strippedText, outPath)


    if errorState is None:
        print ("END")

    else:
        print(f"There was a problem:\n{errorState}")
        