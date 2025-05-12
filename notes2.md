PASTAs Example Project | x0 | x-4b37179a3e2a4ff5bfd0301dca9724be
  This is an example task | x1 | x-cd1a970352c54dca9c36cf0858944f23
    NewDirectory | x1 | x-77624951b6854bc0bc3d3b5ef0ed6870
      simple.csv | measurement/csv/linesAndDots | m-9110cae9924b4252acbd6b9853667fe9
      simple.png | measurement/image | m-082d6971e7ae4f45ba7d614dc3de7ab0
    story.odt | - | --da8a1caa72164b18ad6e86e90664a8cb
  This is another example task | x1 | x-8c37a44a9183400ebbcad69177dba6f7
    This is an example subtask | x1 | x-04e6bf29c0684ceeaaa0e10e5eb55f96
      NewDirectory | x1 | x-8dc2edec3fa941be91fb2fbee53c89a1
        NewDirectory | x1 | x-2cbbea5d1b0f43a48e8506379bd8df49
          NewDirectory | x1 | x-1caf88a4c14f4aa2a6d76d902ed9758e
            worklog.log | workflow/worklog | w-416fbb9323bb4a189e4485ccb03ae766
          workplan.py | workflow/workplan | w-a7d71ddaadca4ce585f6c2e70ec7424b
        NewDirectory | x1 | x-41dcff3667524c6da4b94e1e58e78426
          simple.csv | measurement/csv/linesAndDots | m-9110cae9924b4252acbd6b9853667fe9
        simple.csv | measurement/csv/linesAndDots | m-9110cae9924b4252acbd6b9853667fe9
        worklog.log | workflow/worklog | w-416fbb9323bb4a189e4485ccb03ae766
      NewDirectory | x1 | x-096327f76e63476e9ecb312538fbaa62
        NewDirectory | x1 | x-30efaa2d9a1f433a977ec8aba6a4bb0f
          simple.csv | measurement/csv/linesAndDots | m-9110cae9924b4252acbd6b9853667fe9
        simple.csv | measurement/csv/linesAndDots | m-9110cae9924b4252acbd6b9853667fe9
      simple.png | measurement/image | m-082d6971e7ae4f45ba7d614dc3de7ab0
      simple.png | measurement/image | m-082d6971e7ae4f45ba7d614dc3de7ab0
    This is another example subtask | x1 | x-ae44201d9dff411ea3e70c792adb1e3c
    story.odt | - | --da8a1caa72164b18ad6e86e90664a8cb
    worklog.log | workflow/worklog | w-416fbb9323bb4a189e4485ccb03ae766
    workplan.py | workflow/workplan | w-a7d71ddaadca4ce585f6c2e70ec7424b
  Data files | x1 | x-b6195e6fdc47438787e5279a12fe9fbf
    https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Misc_pollen.jpg/315px-Misc_pollen.jpg | measurement/image | m-a22faeb08d3744a99192fa81f8707214
    worklog.log | workflow/worklog | w-416fbb9323bb4a189e4485ccb03ae766
  NewDirectory | x1 | x-d6919ecc46974be69cd79fc5dca45a2a
    NewDirectory | x1 | x-cff6dae1c6a64623beb82bfaf7aadba3
      worklog.log | workflow/worklog | w-416fbb9323bb4a189e4485ccb03ae766
    simple.png | measurement/image | m-082d6971e7ae4f45ba7d614dc3de7ab0
    simple.csv | measurement/csv/linesAndDots | m-9110cae9924b4252acbd6b9853667fe9
    workplan.py | workflow/workplan | w-a7d71ddaadca4ce585f6c2e70ec7424b
  NewDirectory | x1 | x-f54f468f96b442de80c7a0c09e5cb908
    simple.csv | measurement/csv/linesAndDots | m-9110cae9924b4252acbd6b9853667fe9
    worklog.log | workflow/worklog | w-416fbb9323bb4a189e4485ccb03ae766
  Big instrument | instrument | i-cf8fe8bef05340fdbd664c9da3e310d5
  Sensor | instrument/extension | i-dc9d430cb8524c42aff16fd57c69a776
  simple.png | measurement/image | m-082d6971e7ae4f45ba7d614dc3de7ab0
  Example sample | sample | s-563750d36df94cafb05cf09300cdbcbd
  Example_SOP.md | workflow/procedure/markdown | w-1f849a4ca08c4cd88ba1130b03595f06


   {'docType': ['x1'], 'gui': [True, True], 'hierStack': 'x-4b37179a3e2a4ff5bfd0301dca9724be/x-8c37a44a9183400ebbcad69177dba6f7/x-ae44201d9dff411ea3e70c792adb1e3c'} ->
   {'docType': ['x1'], 'gui': [True, True], 'hierStack': 'x-4b37179a3e2a4ff5bfd0301dca9724be/x-8c37a44a9183400ebbcad69177dba6f7/x-04e6bf29c0684ceeaaa0e10e5eb55f96/x-8dc2edec3fa941be91fb2fbee53c89a1'}    child 0

=============================================
Step 1: before new siblings
0 x-2cbbea5d1b0f43a48e8506379bd8df49 NewDirectory
1 x-41dcff3667524c6da4b94e1e58e78426 NewDirectory
9999 m-9110cae9924b4252acbd6b9853667fe9 simple.csv
9999 w-416fbb9323bb4a189e4485ccb03ae766 worklog.log
  x-2cbbea5d1b0f43a48e8506379bd8df49: move: 0 1
  x-41dcff3667524c6da4b94e1e58e78426: move: 1 1
  m-9110cae9924b4252acbd6b9853667fe9: move: 2 1
  w-416fbb9323bb4a189e4485ccb03ae766: move: 3 1
Step 2: after new siblings
1 x-2cbbea5d1b0f43a48e8506379bd8df49 NewDirectory
2 x-41dcff3667524c6da4b94e1e58e78426 NewDirectory
3 m-9110cae9924b4252acbd6b9853667fe9 simple.csv
4 w-416fbb9323bb4a189e4485ccb03ae766 worklog.log
  manual move 1 -> 0: x-ae44201d9dff411ea3e70c792adb1e3c
Start modelChanged
Step 3: before old siblings
0 x-04e6bf29c0684ceeaaa0e10e5eb55f96 This is an example subtask
9999 --da8a1caa72164b18ad6e86e90664a8cb story.odt
9999 w-416fbb9323bb4a189e4485ccb03ae766 worklog.log
9999 w-a7d71ddaadca4ce585f6c2e70ec7424b workplan.py
  --da8a1caa72164b18ad6e86e90664a8cb: move: 1 1
  w-416fbb9323bb4a189e4485ccb03ae766: move: 2 1
  w-a7d71ddaadca4ce585f6c2e70ec7424b: move: 3 1
Step 4: end of function
0 x-04e6bf29c0684ceeaaa0e10e5eb55f96 This is an example subtask
1 --da8a1caa72164b18ad6e86e90664a8cb story.odt
2 w-416fbb9323bb4a189e4485ccb03ae766 worklog.log
3 w-a7d71ddaadca4ce585f6c2e70ec7424b workplan.py
End modelChanged
PASTAs Example Project | x0 | x-4b37179a3e2a4ff5bfd0301dca9724be
  This is an example task | x1 | x-cd1a970352c54dca9c36cf0858944f23
    NewDirectory | x1 | x-77624951b6854bc0bc3d3b5ef0ed6870
      simple.csv | measurement/csv/linesAndDots | m-9110cae9924b4252acbd6b9853667fe9
      simple.png | measurement/image | m-082d6971e7ae4f45ba7d614dc3de7ab0
    story.odt | - | --da8a1caa72164b18ad6e86e90664a8cb
  This is another example task | x1 | x-8c37a44a9183400ebbcad69177dba6f7
    This is an example subtask | x1 | x-04e6bf29c0684ceeaaa0e10e5eb55f96
      NewDirectory | x1 | x-8dc2edec3fa941be91fb2fbee53c89a1
        This is another example subtask | x1 | x-ae44201d9dff411ea3e70c792adb1e3c
        NewDirectory | x1 | x-2cbbea5d1b0f43a48e8506379bd8df49
          NewDirectory | x1 | x-1caf88a4c14f4aa2a6d76d902ed9758e
            worklog.log | workflow/worklog | w-416fbb9323bb4a189e4485ccb03ae766
          workplan.py | workflow/workplan | w-a7d71ddaadca4ce585f6c2e70ec7424b
        NewDirectory | x1 | x-41dcff3667524c6da4b94e1e58e78426
          simple.csv | measurement/csv/linesAndDots | m-9110cae9924b4252acbd6b9853667fe9
        simple.csv | measurement/csv/linesAndDots | m-9110cae9924b4252acbd6b9853667fe9
        worklog.log | workflow/worklog | w-416fbb9323bb4a189e4485ccb03ae766
      NewDirectory | x1 | x-096327f76e63476e9ecb312538fbaa62
        NewDirectory | x1 | x-30efaa2d9a1f433a977ec8aba6a4bb0f
          simple.csv | measurement/csv/linesAndDots | m-9110cae9924b4252acbd6b9853667fe9
        simple.csv | measurement/csv/linesAndDots | m-9110cae9924b4252acbd6b9853667fe9
      simple.png | measurement/image | m-082d6971e7ae4f45ba7d614dc3de7ab0
      simple.png | measurement/image | m-082d6971e7ae4f45ba7d614dc3de7ab0
    story.odt | - | --da8a1caa72164b18ad6e86e90664a8cb
    worklog.log | workflow/worklog | w-416fbb9323bb4a189e4485ccb03ae766
    workplan.py | workflow/workplan | w-a7d71ddaadca4ce585f6c2e70ec7424b
  Data files | x1 | x-b6195e6fdc47438787e5279a12fe9fbf
    https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Misc_pollen.jpg/315px-Misc_pollen.jpg | measurement/image | m-a22faeb08d3744a99192fa81f8707214
    worklog.log | workflow/worklog | w-416fbb9323bb4a189e4485ccb03ae766
  NewDirectory | x1 | x-d6919ecc46974be69cd79fc5dca45a2a
    NewDirectory | x1 | x-cff6dae1c6a64623beb82bfaf7aadba3
      worklog.log | workflow/worklog | w-416fbb9323bb4a189e4485ccb03ae766
    simple.png | measurement/image | m-082d6971e7ae4f45ba7d614dc3de7ab0
    simple.csv | measurement/csv/linesAndDots | m-9110cae9924b4252acbd6b9853667fe9
    workplan.py | workflow/workplan | w-a7d71ddaadca4ce585f6c2e70ec7424b
  NewDirectory | x1 | x-f54f468f96b442de80c7a0c09e5cb908
    simple.csv | measurement/csv/linesAndDots | m-9110cae9924b4252acbd6b9853667fe9
    worklog.log | workflow/worklog | w-416fbb9323bb4a189e4485ccb03ae766
  Big instrument | instrument | i-cf8fe8bef05340fdbd664c9da3e310d5
  Sensor | instrument/extension | i-dc9d430cb8524c42aff16fd57c69a776
  simple.png | measurement/image | m-082d6971e7ae4f45ba7d614dc3de7ab0
  Example sample | sample | s-563750d36df94cafb05cf09300cdbcbd
  Example_SOP.md | workflow/procedure/markdown | w-1f849a4ca08c4cd88ba1130b03595f06

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
