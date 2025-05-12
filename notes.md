Current choice: [87,90,89,65,91,27,82,79,16,97,85,40,26,69,49,25,47,21,84,82,35,4,67,59,13,12,89,51,4,6,75,53,3,82,5,54,2,36,26,19,45,85,33,16,53,63,40,61,82,33,56,10,0,50,5,35,52,82,46,82,78,14,80,75,78,67,19,72,26,33,74,54,7,66,90,78,99,89,88,76,17,15,98,20,89,35,80,34,82,80,64,68,69,95,41,92,62,32,94,67,20,72,25,32,45,4,77,48,50,6,3,59,29,25,74,30,75,78,76,7,23,72,88,0,33,30,61,79,8,19,54,66,58,95,99,3,94,59,32,49,54,75,4,16,14,68,40,83,29,94,61,43,90,42,48,6,4,44,86,13,46,15,75,36,60,76,90,74,85,71,98,77,27,60,92,72,66,88,66,89,21,45,98,9,71,61,42,74,31,53,27,88,94,47,96,64,92,93,5,46,18,61,48,73,56,25,83,11,81,43,77,1,12,20,92,10,53,79,38,55,57,45,21,68,69,92,80,23,69,70,38,22,66,6,48,38,64,53,10,12,39,62,77,97,42,68,57,71,23,75]
Current choice: [65,34,16,97,12,66,78,10,30,41,4,80,83,69,48,51]

PASTAs Example Project | x0 | x-f8cd3cc200ef4f86a91c5c8b25ba939d
  ...
  This is another example task | x1 | x-35125f4b2a3b485e8a33d0c4b324ff2f
    This is an example subtask | x1 | x-66620eb7345c43379d2c8e989ba760f7
>>    NewDirectory | x1 | x-4f88dbe2cc6b46f79e4a76ae1d2b52c8                                                  -> TARGET
**      NewDirectory | x1 | x-a85b76e524314042a89ab78c42e5ee8b
**        NewDirectory | x1 | x-6197546b1b4942c08d4cb7578f6d99bc
**          worklog.log | workflow/worklog | w-110a0cac455449209d09f7ca319e8aa1
**        workplan.py | workflow/workplan | w-27437c89e9804640b1d342be873e90bd
        NewDirectory | x1 | x-d6bed9d66cf649569805e5abf8a94a76
          simple.csv | measurement/csv/linesAndDots | m-f60e21cdfbee4766843f93d153089d36
        simple.csv | measurement/csv/linesAndDots | m-f60e21cdfbee4766843f93d153089d36
        worklog.log | workflow/worklog | w-110a0cac455449209d09f7ca319e8aa1
      NewDirectory | x1 | x-f0a53ae4888a47299656b4b1d8ef00f4
        NewDirectory | x1 | x-44170ab0f0a54c71a44f85c1d1f6b627
          simple.csv | measurement/csv/linesAndDots | m-f60e21cdfbee4766843f93d153089d36
        simple.csv | measurement/csv/linesAndDots | m-f60e21cdfbee4766843f93d153089d36
      simple.png | measurement/image | m-f053cf59e16c471eb43726ac9a066f93
      simple.png | measurement/image | m-f053cf59e16c471eb43726ac9a066f93
>>  This is another example subtask | x1 | x-d3a8be558af94fee926fb4b4c8f57cbc                                 -> SOURCE
    ...


   {'docType': ['x1'], 'gui': [True, True], 'hierStack': 'x-f8cd3cc200ef4f86a91c5c8b25ba939d/x-35125f4b2a3b485e8a33d0c4b324ff2f/x-d3a8be558af94fee926fb4b4c8f57cbc'} ->
   {'docType': ['x1'], 'gui': [True, True], 'hierStack': 'x-f8cd3cc200ef4f86a91c5c8b25ba939d/x-35125f4b2a3b485e8a33d0c4b324ff2f/x-66620eb7345c43379d2c8e989ba760f7/x-4f88dbe2cc6b46f79e4a76ae1d2b52c8'}


*** File status ***
**ERROR Folder on disk but not DB  :PastasExampleProject/001_ThisIsAnotherExampleTask/000_ThisIsAnExampleSubtask/000_Newdirectory/002_Newdirectory/000_Newdirectory
**ERROR File on harddisk but not DB (2): PastasExampleProject/001_ThisIsAnotherExampleTask/000_ThisIsAnExampleSubtask/000_Newdirectory/002_Newdirectory/000_Newdirectory/workplan.py
**ERROR Folder on disk but not DB  :PastasExampleProject/001_ThisIsAnotherExampleTask/000_ThisIsAnExampleSubtask/000_Newdirectory/002_Newdirectory/000_Newdirectory/000_Newdirectory
**ERROR File on harddisk but not DB (2): PastasExampleProject/001_ThisIsAnotherExampleTask/000_ThisIsAnExampleSubtask/000_Newdirectory/002_Newdirectory/000_Newdirectory/000_Newdirectory/worklog.log
**ERROR bch01: These paths of database not on filesystem(3):
  - PastasExampleProject/001_ThisIsAnotherExampleTask/000_ThisIsAnExampleSubtask/000_Newdirectory/001_Newdirectory/workplan.py
  - PastasExampleProject/001_ThisIsAnotherExampleTask/000_ThisIsAnExampleSubtask/000_Newdirectory/001_Newdirectory/000_Newdirectory/worklog.log
  - PastasExampleProject/001_ThisIsAnotherExampleTask/000_ThisIsAnExampleSubtask/000_Newdirectory/001_Newdirectory
  - PastasExampleProject/001_ThisIsAnotherExampleTask/000_ThisIsAnExampleSubtask/000_Newdirectory/001_Newdirectory/000_Newdirectory

# Notes:
link: https://github.com/PASTA-ELN/pasta-eln/actions/runs/14969694824/job/42047639843
no exception; verification fails