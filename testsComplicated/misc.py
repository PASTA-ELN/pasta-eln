from pasta_eln.elabFTWsync import MERGE_LABELS

def verify(backend): # Verify DB
  output = backend.checkDB(outputStyle='text')
  print(output)
  output = '\n'.join(output.split('\n')[8:])
  assert '**ERROR' not in output, 'Error in checkDB'
  assert len(output.split('\n')) == 5, 'Check db should have 5 more-less empty lines'
  return


def handleReports(reports, targets=[]):
  print('\n'.join([f'{i[0]} {MERGE_LABELS[i[1]]}' for i in reports]))
  if targets:
    cases = [i[1] for i in reports]
    for idx,target in enumerate(targets):
      assert cases.count(idx+1) == target, f'You should have {target} of case {idx+1}'
