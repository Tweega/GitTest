import os
import interpolateCode

if __name__ == "__main__":
    ## these are not unit tests as the interpolator relies mainly on side effects

    RUN_ALL = True
    SHOW_ALL_RESULTS = True
    repoPath = r"/home/christopher/work/python/some_repo"
    nonGitRepoPath = r"/home/christopher/work/python/not_a_git_repo"

    testOutPath1 = os.path.join(repoPath, "output", "Test1")
    testOutPath2 = os.path.join(repoPath, "output", "Test2")
    testOutPath3 = os.path.join(repoPath, "output", "Test3")
    testOutPath4 = os.path.join(repoPath, "output", "Test4")
    testOutPath5 = os.path.join(repoPath, "output", "Test5")
    testOutPath6 = os.path.join(repoPath, "output", "Test6")
    testOutPath7 = os.path.join(repoPath, "output", "Test7")
    testOutPath8 = os.path.join(repoPath, "output", "Test8")
    testOutPath9 = os.path.join(repoPath, "output", "Test9")
    testOutPath10 = os.path.join(repoPath, "output", "Test10")
    testOutPath11 = os.path.join(repoPath, "output", "Test11")
    testOutPath12 = os.path.join(repoPath, "output", "Test12")
    testOutPath13 = os.path.join(repoPath, "output", "Test13")
    testOutPath14 = os.path.join(repoPath, "output", "Test14")
    testOutPath15 = os.path.join(repoPath, "output", "Test15")
    notAGitRepoPath = os.path.join(nonGitRepoPath, "output", "Test1")
    testOutPathNotExist = os.path.join(repoPath, "output", "DoesNotExist")
    gitURL = r"git@github.com:Tweega/CodeExamples.git"
    gitURLDoesNotExist = r"git@github.com:Tweega/DoesNotExist.git"
    templateFile = "media_proto.html"
    tFile = os.path.join(repoPath,  templateFile)

    successes = []
    failures = []

    print ("Tests for interpolateCode.py")

    reason = "--template must be supplied"
    if RUN_ALL or True:
        res = interpolateCode.runInterpolation([])
        if res == reason:
            successes.append(f"{reason} PASSED")
        else :
            failures.append(f"{reason} FAILED.  Got: {res}")

    

    reason = "One of --gitrepo or --repopath must be provided"
    if RUN_ALL or True:

        res = interpolateCode.runInterpolation(["--template", tFile])
        if res == reason:
            successes.append(f"{reason} PASSED")
        else :
            failures.append(f"{reason} FAILED.  Got: {res}")

    

    reason = "--outputpath must be specified"
    if RUN_ALL or False:
        res = interpolateCode.runInterpolation(["--codepath", repoPath, "--template", tFile])
        if res == reason:
            successes.append(f"{reason} PASSED")
        else :
            failures.append(f"{reason} FAILED.  Got: {res}")
    
    reason = "--template must be supplied"
    if RUN_ALL or False:
        res = interpolateCode.runInterpolation(["--codepath", repoPath, "--outputpath", testOutPath1])
        if res == reason:
            successes.append(f"{reason} PASSED")
        else :
            failures.append(f"{reason} FAILED.  Got: {res}")


    reason = "--output path must be valid"
    if RUN_ALL or False:
        res = interpolateCode.runInterpolation(["--codepath", repoPath, "--outputpath", testOutPathNotExist, "--template", templateFile])
        err = "Unable to access output path:"
        strLen = len(err)
        if res is not None and res[0:strLen] == err:
            successes.append(f"{reason} PASSED")
        else:
            failures.append(f"{reason} FAILED.  Got: {res}")


    reason = "--repo path must be valid"
    if RUN_ALL or False:
        res = interpolateCode.runInterpolation(["--codepath", testOutPathNotExist, "--outputpath", testOutPath1, "--template", tFile])
        err = "Unable to access code path:"
        strLen = len(err)
        if res is not None and res[0:strLen] == err:
            successes.append(f"{reason} PASSED")
        else :
            failures.append(f"{reason} FAILED.  Got: {res}")
            
            

    reason = "template file must be valid"
    if RUN_ALL or False:
        res = interpolateCode.runInterpolation(["--codepath", repoPath, "--outputpath", testOutPath1, "--template", "doesNotExist"])
        err = "template file does not exist:"
        strLen = len(err)
        if res is not None and res[0:strLen] == err:
            successes.append(f"{reason} PASSED")
        else:
            failures.append(f"{reason} FAILED.  Got: {res}")

    
    reason = "Only one of --coderepo or --giturl should be supplied"
    if RUN_ALL or False:
        res = interpolateCode.runInterpolation(["--codepath", repoPath, "--outputpath", testOutPath1, "--template", "doesNotExist"])
        err = "template file does not exist:"
        strLen = len(err)
        if res is not None and res[0:strLen] == err:
        
            # // we should also check that files arrive in the target directory
            successes.append(f"{reason} PASSED")
        else:
            failures.append(f"{reason} FAILED.  Got: {res}")


    reason = "Test1 directory gets processed template file when repoPath is NOT a git repo)"
    if RUN_ALL or False:
        res = interpolateCode.runInterpolation(["--codepath", nonGitRepoPath, "--outputpath", notAGitRepoPath, "--template", templateFile])
        if res is None:
            # // we should also check that files arrive in the target directory
            successes.append(f"{reason} PASSED")
        else :
            failures.append(f"{reason} FAILED")


    reason = "Test1 directory gets processed template file (and local repo is NOT refreshed from git)"
    if RUN_ALL or False:
        res = interpolateCode.runInterpolation(["--codepath", repoPath, "--outputpath", testOutPath1, "--template", templateFile, "--verbose"])
        if res is None:
            # // we should also check that files arrive in the target directory
            successes.append(f"{reason} PASSED")
        else :
            failures.append(f"{reason} FAILED: {res}")


    reason = "We can use a full template path in cnojunction with --codepath)"
    if RUN_ALL or False:
        res = interpolateCode.runInterpolation(["--codepath", repoPath, "--outputpath", testOutPath2, "--template", tFile, "--verbose"])
        if res is None:
            # // we should also check that files arrive in the target directory
            successes.append(f"{reason} PASSED. {testOutPath2}")
        else :
            failures.append(f"{reason} FAILED: {res}")


    reason = "template file processed to target (and local repo is refreshed from git)"
    tFile = os.path.join(repoPath,  templateFile)
    if RUN_ALL or False:
        res = interpolateCode.runInterpolation(["--codepath", repoPath, "--gitpull", "--outputpath", testOutPath3, "--template", tFile, "--verbose"])
        if res is None:
            # // we should also check that files arrive in the target directory
            successes.append(f"{reason} PASSED. {testOutPath3}")

        else :
            failures.append(f"{reason} FAILED: {res}")


    reason = "Git repo cloned to temp file and used for code sources"
    if RUN_ALL or False:
        res = interpolateCode.runInterpolation(["--gitrepo", gitURL, "--outputpath", testOutPath4, "--template", tFile, "--verbose"])
        if res is None:
            # // we should also check that files arrive in the target directory
            successes.append(f"{reason} PASSED. {testOutPath4}")

        else :
            failures.append(f"{reason} FAILED: {res}")




    #RESULTS
    testCount = len(successes) + len(failures)
    if SHOW_ALL_RESULTS:
        print (f"\nTest successes: {len(successes)} out of {testCount} that were run\n")
        for r in successes:
            print (r)
    
    if len(failures) > 0:
        for r in failures:
            print (r)
    
    print (f"\nTest failures: {len(failures)} out of {testCount} that were run\n")
        