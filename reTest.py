import re


if __name__ == "__main__":
    
    filesToSearchMap = {}
    errorLog = []

    str = r'[excerpt]thisFile, thislabel[/excerpt]'
    reStr = r'^\[excerpt](.+)\[\/excerpt]'
    match = re.search(reStr, str)
    # If-statement after search() tests if it succeeded
    if match:
        excerptContents = match.groups()[0]
        print('found', excerptContents) ## 'found word:cat'
        # add this file to the map, if it does not already exist
        splitDetails = excerptContents.split(",")
        if len(splitDetails) == 2:
            fileName = splitDetails[0].strip()
            excerptID = splitDetails[1].strip()

            existingExcerpts = filesToSearchMap.get(fileName)
            excerpts = [excerptID]
            if existingExcerpts: 
                excerpts = existingExcerpts.append (excerptID)
            
            filesToSearchMap[fileName] = excerpts
            
            for i in filesToSearchMap:
                print(filesToSearchMap.get(i))
        else:
            err = f"Could not split contents of excerpt tag {excerptContents}"
            errorLog.append(err)