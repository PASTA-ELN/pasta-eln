    # TextButton('New',         self, [Command.NEW],       topbarL)
    # TextButton('Fill remote', self, [Command.FILL],      topbarL)
    # TextButton('Create QR',   self, [Command.CREATE_QR], topbarL)
    # TextButton('Check All',   self, [Command.CHECK],     topbarL)
    # self.projectGroupName = QLineEdit('')
    # self.projectGroupName.hide()
    # mainL.addWidget(self.projectGroupName)
    # _, bodyL = widgetAndLayout('H', mainL)
    # #local
    # localW = QGroupBox('Local credentials')
    # localL = QFormLayout(localW)
    # self.userNameL = QLineEdit('')
    # self.userNameL.setValidator(QRegularExpressionValidator("[\\w.]{5,}"))
    # localL.addRow('User name', self.userNameL)
    # self.passwordL = QLineEdit('')
    # self.passwordL.setValidator(QRegularExpressionValidator("\\S{5,}"))
    # self.passwordL.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
    # localL.addRow('Password', self.passwordL)
    # self.databaseL = QLineEdit('')
    # self.databaseL.setValidator(QRegularExpressionValidator("\\w{5,}"))
    # localL.addRow('Database', self.databaseL)
    # pathW, pathL = widgetAndLayout('H', spacing='s')
    # self.pathL = QLineEdit('')
    # pathL.addWidget(self.pathL, stretch=5)
    # if platform.system()=='Windows':
    #   self.pathL.setValidator(QRegularExpressionValidator(r"[\\/~][\\w\\\\\\/:\.~]{5,}"))
    # else:
    #   self.pathL.setValidator(QRegularExpressionValidator(r"[\\/~][\\w\\/]{5,}"))
    # IconButton('fa5.folder-open', self, [Command.OPEN_DIR], pathL, 'Folder to save data in')
    # localL.addRow('Path', pathW)
    # bodyL.addWidget(localW)
    # #remote
    # remoteW = QGroupBox('Remote credentials')
    # remoteL = QFormLayout(remoteW)
    # self.userNameR = QLineEdit('')
    # self.userNameR.setValidator(QRegularExpressionValidator("[\\w.]{5,}"))
    # remoteL.addRow('User name', self.userNameR)
    # self.passwordR = QLineEdit('')
    # self.passwordR.setValidator(QRegularExpressionValidator("\\S{5,}"))
    # self.passwordR.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
    # remoteL.addRow('Password', self.passwordR)
    # self.databaseR = QLineEdit('')
    # self.databaseR.setValidator(QRegularExpressionValidator("\\w{5,}"))
    # remoteL.addRow('Database', self.databaseR)
    # self.serverR = QLineEdit('')
    # self.serverR.setValidator(QRegularExpressionValidator("http:\\/\\/(?:[0-9]{1,3}\\.){3}[0-9]{1,3}:5984"))
    # remoteL.addRow('Server', self.serverR)
    # bodyL.addWidget(remoteW)




    # if btn.text().endswith('Cancel'):
    #   self.reject()
    # elif 'Save' in btn.text() and self.checkEntries():
    #   name = self.projectGroupName.text() if self.selectGroup.isHidden() else self.selectGroup.currentText()
    #   local = remote = {}
    #   if btn.text().endswith('Save'):
    #     localPath = self.pathL.text()
    #     if localPath.startswith('~'):
    #       localPath = (Path.home()/localPath[1:]).as_posix()
    #     local = {'user':self.userNameL.text(), 'password':self.passwordL.text(), \
    #               'database':self.databaseL.text(), 'path':localPath}
    #     remote = {'user':self.userNameR.text(), 'password':self.passwordR.text(), \
    #               'database':self.databaseR.text(), 'url':self.serverR.text()}
    #   elif btn.text().endswith('Save encrypted'):
    #     credL = ''
    #     credR = ''
    #     local = {'cred':credL, 'database':self.databaseL.text(), 'path':self.pathL.text()}
    #     remote = {'cred':credR, 'database':self.databaseR.text(), 'url':self.serverR.text()}
    #   newGroup = {'local':local, 'remote':remote}
    #   self.configuration['projectGroups'][name] = newGroup
    #   self.configuration['defaultProjectGroup'] = name
    #   with open(Path.home()/'.pastaELN.json', 'w', encoding='utf-8') as fConf:
    #     fConf.write(json.dumps(self.configuration,indent=2))
    #   restart()
    # else:
    #   print('dialogProjectGroup: did not get a fitting btn ',btn.text())


    # if command[0] is Command.NEW:
    #   self.selectGroup.hide()
    #   self.projectGroupName.show()
    #   self.projectGroupName.setText('my_project_group_name')
    #   defaultProjectGroup = self.configuration['defaultProjectGroup']
    #   config = self.configuration['projectGroups'][defaultProjectGroup]
    #   u,p = config['local']['user'], config['local']['password']
    #   self.userNameL.setText(u)
    #   self.userNameR.setText('')
    #   self.passwordL.setText(p)
    #   self.passwordR.setText('')
    #   self.databaseL.setText('')
    #   self.databaseR.setText('')
    #   self.pathL.setText('')
    #   self.serverR.setText('')
    # elif command[0] is Command.FILL:
    #   contentFile = QFileDialog.getOpenFileName(self, "Load remote credentials", str(Path.home()), '*.key')[0]
    #   with open(contentFile, encoding='utf-8') as fIn:
    #     content = json.loads( passwordDecrypt(bytes(fIn.read(), 'UTF-8')) )
    #     self.userNameR.setText(content['user-name'])
    #     self.passwordR.setText(content['password'])
    #     self.databaseR.setText(content['database'])
    #     self.serverR.setText(content['Server'])
    # elif command[0] is Command.CREATE_QR:
    #   if self.projectGroupName.isHidden():
    #     configname = self.selectGroup.currentText()
    #   else:
    #     configname = self.projectGroupName.text()
    #   qrCode = {"configname": configname, "credentials":{"server":self.serverR.text(), \
    #       "username":self.userNameR.text(), "password":self.passwordR.text(), "database":self.databaseR.text()}}
    #   img = qrcode.make(json.dumps(qrCode), error_correction=qrcode.constants.ERROR_CORRECT_M)
    #   pixmap = QPixmap.fromImage(ImageQt(img).scaledToWidth(200))
    #   self.image.setPixmap(pixmap)
    # elif command[0] is Command.CHECK:
    #   self.checkEntries()
    # elif command[0] is Command.OPEN_DIR:
    #   if dirName := QFileDialog.getExistingDirectory(self, 'Choose directory to save data', str(Path.home())):
    #     self.pathL.setText(dirName)
    # else:
    #   print("**ERROR projectGroup unknown:",command)
