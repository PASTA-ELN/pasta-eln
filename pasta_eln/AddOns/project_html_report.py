description = "Create html report"

def main(backend, projID, getFileName):
    backend.changeHierarchy(projID)
    output = backend.outputHierarchy(False, False)
    fileName = getFileName()
    with open(fileName, 'w', encoding='utf-8') as f:
        f.write(output)
    return True
