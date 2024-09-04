#!/usr/bin/python3
from pasta_eln.gui import startMain
from pasta_eln.serverActions import couchDB2SQLite, verifyPasta, translateV2_V3, delete
from pasta_eln.installationTools import exampleData

# exampleData(force=True, projectGroup='research')
verifyPasta('research')
startMain('research')
verifyPasta('research')
# translateV2_V3('/home/steffen/FZJ/pasta_Folder')
# delete('main', 'x-691cf67bf97f409c973d84c9a94ed2be')
#couchDB2SQLite("admin","972551a0baa8407ebf29ba86d67d5c3b", "sb-0bacab30726e181fe1e34d82e59a8ce9", "/home/steffen/FZJ/pasta_misc/testing")
