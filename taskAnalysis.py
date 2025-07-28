import subprocess, json

done = ['EXTRACTOR_TEST', 'EXTRACTOR_RERUN', 'SCAN', 'DELETE_DOC', 'CHECK_DB','SET_GUI','EXPORT_ELN','IMPORT_ELN',
        'SEND_ELAB', 'GET_ELAB', 'SMART_ELAB']
target = {}
toUpdate = []
result1 = subprocess.run(['grep', '-r','uiRequestTask', 'pasta_eln'], capture_output=True, text=True)
for line in result1.stdout.split('\n'):
    if len(line)<10:
        continue
    fileName, code = line.split(':', maxsplit=1)
    if 'uiRequestTask.emit(Task.' in code:  # this is how it should be
        task = code.split('emit(Task.')[1].split(',', maxsplit=1)[0]
        data = code.split('emit(Task.')[1].split(',', maxsplit=1)[1][:-1]
        if task in done:
            continue
        if task not in target:
            target[task] = []
        target[task].append(f'{fileName.strip()}: {data.strip()}')
    else:
        toUpdate.append(line)

result2 = subprocess.run(['grep', r"\.backend\.", '-r', 'pasta_eln/UI/'], capture_output=True, text=True)
for line in  result2.stdout.split('\n'):
    if 'remove' in line or True:
        print(line)


print('Files to update:\n  '+'\n  '.join(toUpdate))
print('Files done:\n'+json.dumps(target, indent=2))