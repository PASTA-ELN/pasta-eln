""" Long strings and dictionaries/JSON that would obfuscate code """
from typing import Any

defaultDataHierarchy: dict[str, Any] = {
  "x0": {"IRI": "", "attachments": [], "title": "Projects", "icon": "", "shortcut": "space",
         "view":"-name,-tags,status,objective,comment",
         "meta": {"default": [
           {"name": "-name", "query": "What is the name of the project?", "mandatory": True},
           {"name": "-tags", "query": "What are the tags associated with the project?", "mandatory": True},
           {"name": "status", "query": "What is the project status",
            "list": ["active", "paused", "passive", "finished"]},
           {"name": "objective", "query": "What is the objective?"},
           {"name": "comment", "query": "#tags comments remarks :field:value:"}
         ]}},
  "x1": {"IRI": "", "attachments": [], "title": "Folders", "icon": "", "shortcut": "", "view":"",
         "meta": {"default": [
           {"name": "-name", "query": "What is the name of task?", "mandatory": True},
           {"name": "-tags", "query": "What are the tags associated with the task?", "mandatory": True},
           {"name": "comment", "query": "#tags comments remarks :field:value:"}
         ]}},

  "measurement": {"IRI": "", "attachments": [], "title": "Measurements", "icon": "fa5s.thermometer-half",
                  "shortcut": "m", "view":"-name,-tags,comment,-type,image,sample,procedure",
                  "meta": {"default": [
                    {"name": "-name", "query": "What is the name of file name?", "mandatory": True},
                    {"name": "-tags", "query": "What are the tags associated with the file name?", "mandatory": True},
                    {"name": "comment", "query": "#tags comments remarks :field:value:"},
                    {"name": "-type"},
                    {"name": "image"},
                    {"name": "#_curated"},
                    {"name": "sample", "query": "Which sample was used?", "list": "sample"},
                    {"name": "procedure", "query": "Which procedure was used?", "list": "procedure"}
                  ]}},
  "sample": {"IRI": "", "attachments": [], "title": "Samples", "icon": "fa5s.vial", "shortcut": "s",
             "view":"-name,-tags,chemistry,comment,qrCode",
             "meta": {"default": [
               {"name": "-name", "query": "What is the name / identifier of the sample?", "mandatory": True},
               {"name": "-tags", "query": "What are the tags associated with the sample?", "mandatory": True},
               {"name": "chemistry", "query": "What is its chemical composition?"},
               {"name": "comment", "query": "#tags comments remarks :field:value:"},
               {"name": "qrCode"}
             ]}},
  "procedure": {"IRI": "", "attachments": [], "title": "Procedures", "icon": "fa5s.list-ol", "shortcut": "p",
                "view":"-name,-tags,comment,content",
                "meta": {"default": [
                  {"name": "-name", "query": "What is the name / path of the procedure?", "mandatory": True},
                  {"name": "-tags", "query": "What are the tags associated with the procedure?", "mandatory": True},
                  {"name": "comment", "query": "#tags comments :field:value: e.g. #SOP_v1"},
                  {"name": "content", "query": "What is procedure (Markdown possible; autofill if file given)?"}
                ]}},
  "instrument": {"IRI": "", "attachments": [], "title": "Instruments", "icon": "ri.scales-2-line", "shortcut": "i",
                 "view":"-name,-tags,comment,vendor",
                 "meta": {"default": [
                   {"name": "-name", "query": "What is the name / path of the instrument?", "mandatory": True},
                   {"name": "-tags", "query": "What are the tags associated with the instrument?", "mandatory": True},
                   {"name": "comment", "query": "#tags comments :field:value: e.g. #SOP_v1"},
                   {"name": "vendor", "query": "Who is the vendor?"}
                 ]}}
}

defaultDataHierarchyNode: dict[str, list[dict[str, str]]] = {
  "default": [
    {"name": "-name", "query": "What is the file name?"},
    {"name": "-tags"},
    {"name": "comment", "query": "#tags comments remarks :field:value:"},
    {"name": "-type"}
  ]}

defaultConfiguration: dict[str, Any] = {
  "defaultProjectGroup": "research",
  "userID": "$os.getlogin()$",
  "version": 0,
  "tableColumnsMax": 16,
  "qrPrinter": {},
  "extractorDir": "$(Path(__file__).parent/'Extractors').as_posix()$",
  "extractors": {},
  "authors": [{"first": "", "last": "", "title": "", "email": "", "orcid": "",
               "organizations": [{"organization": "", "rorid": ""}]}],
  "GUI": {},
  "projectGroups": {}
}

# level 1: type of property
#   within each: array of 3: description, default, all_choices
configurationGUI: dict[str, Any] = {
  "general": {
    "theme": ["Theme",
              "light_blue",
              ["dark_amber", "dark_blue", "dark_cyan", "dark_lightgreen", "dark_pink", "dark_purple", "dark_red", \
               "dark_teal", "dark_yellow", "light_amber", "light_blue", "light_cyan", "light_lightgreen", \
               "light_pink", "light_purple", "light_red", "light_teal", "light_yellow", "none"]],
    "loggingLevel":  ["Logging level (more->less)", "INFO", ["DEBUG", "INFO", "WARNING", "ERROR"]],
    "autosave":      ["Autosave entries in form", "No", ["Yes", "No"]],
    "showProjectBtn":["Show project button on top-left", "Yes", ["Yes", "No"]]
  },
  "dimensions": {
    "sidebarWidth": ["Sidebar width", 280, [220, 280, 340]],
    "maxTableColumnWidth": ["Maximum column width in tables", 400, [300, 400, 500, 600]],
    "imageSizeDetails": ["Image size in details view and form", 600, [300, 400, 500, 600]],
    "imageWidthProject": ["Image width in project view", 300, [200, 250, 300, 350, 400]],
    "maxProjectLeafHeight": ["Maximum height of item in project view", 250, [200, 250, 300, 400]],
    "widthContent": ["Width of procedures in project view", 600, [400, 500, 600, 700]],
    "docTypeOffset": ["Offset of document type in project view", 500, [400, 500, 600, 700]],
    "frameSize": ["Frame width around items in project view", 6, [4, 6, 8, 10]],
  }
}

setupTextLinux = """
### Welcome to the PASTA-ELN setup for Linux
Three components are needed for proper functioning of PASTA-ELN:
- CouchDB
- Configuration of preferences / default data hierarchy
- Example project creation

This setup will analyse and (possibly) correct these items.

If the installation is successful, manually and permanently remove the 'pastaELN.log' logfile that is in your home-directory.
"""

setupTextWindows = """
### Welcome to the PASTA-ELN setup for Windows
Four components are needed for proper functioning of PASTA-ELN:
- CouchDB
- Configuration of preferences / default data hierarchy
- Shortcut creation
- Example project creation

This setup will analyse and (possibly) correct these items.

If the installation is successful, manually and permanently remove the 'pastaELN.log' logfile that is in your home-directory (folder above "My Documents").

If an attempt fails: please follow to this [website](https://pasta-eln.github.io/pasta-eln/install.html).
"""

gitWindows = """
Do you want to install git?

Be aware, downloading the installer requires some time, depending on the internet connection.
"""

rootInstallLinux = """
Do you want to install Apache CouchDB (TM)?
If you choose yes, you will be first asked to

- choose a directory to store the data
- enter the super-user password in the new terminal that will open automatically

Be aware that downloading the installer requires time, depending on the internet connection.
"""

couchDBWindows = """
Do you want to install CouchDB?

Be aware that downloading the installer requires time, depending on the internet connection.
"""

restartPastaWindows = """
Close software now (will be done automatically in the future)

Please restart the software by
- clicking on the shortcut OR
- executing the command in a new cmd.exe window
"""

exampleDataLinux = """
Do you want to create an example project?

This step helps to verify the installation and provides an helpful example for new users.

!WARNING! This process will RESET everything and thereby DELETE EVERYTHING since you installed pastaELN.

This step usually takes up to 20sec, so please be patient. Sometimes, Linux mentions that the program
is not responding and asks if to close/wait. Please WAIT.
"""

exampleDataWindows = """
Do you want to create an example project?

This step helps to verify the installation and provides an helpful example for new users.

!WARNING! This process will RESET everything and thereby DELETE EVERYTHING since you installed pastaELN.

This step usually takes up to 1min, so please be patient.
"""

shortcuts = """
### Shortcuts:

**Ctrl+Space**: List projects

**Ctrl+M**: List measurements

**Ctrl+S**: List samples

**Ctrl+P**: List procedures

**Ctrl+I**: List instruments

**Ctrl+T**: List tags

**Ctrl+U**: List unidentified

**F2**: Test file extraction

**F5**: Synchronize

**F9**: Restart

**Ctrl+?**: Verify database integrity

**Ctrl+0**: Configuration
"""

tableHeaderHelp = """
<h4>You can add custom rows via bottom text area.</h4>

If you want to add a column:
<ul>
<li> for a normal data-field (comment, content, name, type, tags, user, date), enter this field : 'comment'
<li> to check the existence of an image: enter 'image'
<li> to check if a tag is present: "#tag", in which you replace "tag" by the tag you want to look for. "_curated" is a special tag for measurements.
<li> for information inside the metadata, use a "/": e.g. "metaVendor/fileExtension", "metaUser/stress". Capitalization is important.
</ul>
"""

allIcons = [
  "fa5s.address-book", "fa5s.address-card", "fa5s.adjust", "fa5s.align-center", "fa5s.align-justify", "fa5s.align-left",
  "fa5s.align-right", "fa5s.allergies", "fa5s.ambulance", "fa5s.american-sign-language-interpreting", "fa5s.anchor",
  "fa5s.angle-double-down", "fa5s.angle-double-left", "fa5s.angle-double-right", "fa5s.angle-double-up",
  "fa5s.angle-down", "fa5s.angle-left", "fa5s.angle-right", "fa5s.angle-up", "fa5s.archive",
  "fa5s.arrow-alt-circle-down", "fa5s.arrow-alt-circle-left", "fa5s.arrow-alt-circle-right", "fa5s.arrow-alt-circle-up",
  "fa5s.arrow-circle-down", "fa5s.arrow-circle-left", "fa5s.arrow-circle-right", "fa5s.arrow-circle-up",
  "fa5s.arrow-down", "fa5s.arrow-left", "fa5s.arrow-right", "fa5s.arrow-up", "fa5s.arrows-alt", "fa5s.arrows-alt-h",
  "fa5s.arrows-alt-v", "fa5s.assistive-listening-systems", "fa5s.asterisk", "fa5s.at", "fa5s.audio-description",
  "fa5s.backward", "fa5s.balance-scale", "fa5s.ban", "fa5s.band-aid", "fa5s.barcode", "fa5s.bars", "fa5s.baseball-ball",
  "fa5s.basketball-ball", "fa5s.bath", "fa5s.battery-empty", "fa5s.battery-full", "fa5s.battery-half",
  "fa5s.battery-quarter", "fa5s.battery-three-quarters", "fa5s.bed", "fa5s.beer", "fa5s.bell", "fa5s.bell-slash",
  "fa5s.bicycle", "fa5s.binoculars", "fa5s.birthday-cake", "fa5s.blind", "fa5s.bold", "fa5s.bolt", "fa5s.bomb",
  "fa5s.book", "fa5s.bookmark", "fa5s.bowling-ball", "fa5s.box", "fa5s.box-open", "fa5s.boxes", "fa5s.braille",
  "fa5s.briefcase", "fa5s.briefcase-medical", "fa5s.bug", "fa5s.building", "fa5s.bullhorn", "fa5s.bullseye",
  "fa5s.burn", "fa5s.bus", "fa5s.calculator", "fa5s.calendar", "fa5s.calendar-alt", "fa5s.calendar-check",
  "fa5s.calendar-minus", "fa5s.calendar-plus", "fa5s.calendar-times", "fa5s.camera", "fa5s.camera-retro",
  "fa5s.capsules", "fa5s.car", "fa5s.caret-down", "fa5s.caret-left", "fa5s.caret-right", "fa5s.caret-square-down",
  "fa5s.caret-square-left", "fa5s.caret-square-right", "fa5s.caret-square-up", "fa5s.caret-up", "fa5s.cart-arrow-down",
  "fa5s.cart-plus", "fa5s.certificate", "fa5s.chart-area", "fa5s.chart-bar", "fa5s.chart-line", "fa5s.chart-pie",
  "fa5s.check", "fa5s.check-circle", "fa5s.check-square", "fa5s.chess", "fa5s.chess-bishop", "fa5s.chess-board",
  "fa5s.chess-king", "fa5s.chess-knight", "fa5s.chess-pawn", "fa5s.chess-queen", "fa5s.chess-rook",
  "fa5s.chevron-circle-down", "fa5s.chevron-circle-left", "fa5s.chevron-circle-right", "fa5s.chevron-circle-up",
  "fa5s.chevron-down", "fa5s.chevron-left", "fa5s.chevron-right", "fa5s.chevron-up", "fa5s.child", "fa5s.circle",
  "fa5s.circle-notch", "fa5s.clipboard", "fa5s.clipboard-check", "fa5s.clipboard-list", "fa5s.clock", "fa5s.clone",
  "fa5s.closed-captioning", "fa5s.cloud", "fa5s.cloud-download-alt", "fa5s.cloud-upload-alt", "fa5s.code",
  "fa5s.code-branch", "fa5s.coffee", "fa5s.cog", "fa5s.cogs", "fa5s.columns", "fa5s.comment", "fa5s.comment-alt",
  "fa5s.comment-dots", "fa5s.comment-slash", "fa5s.comments", "fa5s.compass", "fa5s.compress", "fa5s.copy",
  "fa5s.copyright", "fa5s.couch", "fa5s.credit-card", "fa5s.crop", "fa5s.crosshairs", "fa5s.cube", "fa5s.cubes",
  "fa5s.cut", "fa5s.database", "fa5s.deaf", "fa5s.desktop", "fa5s.diagnoses", "fa5s.dna", "fa5s.dollar-sign",
  "fa5s.dolly", "fa5s.dolly-flatbed", "fa5s.donate", "fa5s.dot-circle", "fa5s.dove", "fa5s.download", "fa5s.edit",
  "fa5s.eject", "fa5s.ellipsis-h", "fa5s.ellipsis-v", "fa5s.envelope", "fa5s.envelope-open", "fa5s.envelope-square",
  "fa5s.eraser", "fa5s.euro-sign", "fa5s.exchange-alt", "fa5s.exclamation", "fa5s.exclamation-circle",
  "fa5s.exclamation-triangle", "fa5s.expand", "fa5s.expand-arrows-alt", "fa5s.external-link-alt",
  "fa5s.external-link-square-alt", "fa5s.eye", "fa5s.eye-dropper", "fa5s.eye-slash", "fa5s.fast-backward",
  "fa5s.fast-forward", "fa5s.fax", "fa5s.female", "fa5s.fighter-jet", "fa5s.file", "fa5s.file-alt", "fa5s.file-archive",
  "fa5s.file-audio", "fa5s.file-code", "fa5s.file-excel", "fa5s.file-image", "fa5s.file-medical",
  "fa5s.file-medical-alt", "fa5s.file-pdf", "fa5s.file-powerpoint", "fa5s.file-video", "fa5s.file-word", "fa5s.film",
  "fa5s.filter", "fa5s.fire", "fa5s.fire-extinguisher", "fa5s.first-aid", "fa5s.flag", "fa5s.flag-checkered",
  "fa5s.flask", "fa5s.folder", "fa5s.folder-open", "fa5s.font", "fa5s.football-ball", "fa5s.forward", "fa5s.frown",
  "fa5s.futbol", "fa5s.gamepad", "fa5s.gavel", "fa5s.gem", "fa5s.genderless", "fa5s.gift", "fa5s.glass-martini",
  "fa5s.globe", "fa5s.golf-ball", "fa5s.graduation-cap", "fa5s.h-square", "fa5s.hand-holding",
  "fa5s.hand-holding-heart", "fa5s.hand-holding-usd", "fa5s.hand-lizard", "fa5s.hand-paper", "fa5s.hand-peace",
  "fa5s.hand-point-down", "fa5s.hand-point-left", "fa5s.hand-point-right", "fa5s.hand-point-up", "fa5s.hand-pointer",
  "fa5s.hand-rock", "fa5s.hand-scissors", "fa5s.hand-spock", "fa5s.hands", "fa5s.hands-helping", "fa5s.handshake",
  "fa5s.hashtag", "fa5s.hdd", "fa5s.heading", "fa5s.headphones", "fa5s.heart", "fa5s.heartbeat", "fa5s.history",
  "fa5s.hockey-puck", "fa5s.home", "fa5s.hospital", "fa5s.hospital-alt", "fa5s.hospital-symbol", "fa5s.hourglass",
  "fa5s.hourglass-end", "fa5s.hourglass-half", "fa5s.hourglass-start", "fa5s.i-cursor", "fa5s.id-badge", "fa5s.id-card",
  "fa5s.id-card-alt", "fa5s.image", "fa5s.images", "fa5s.inbox", "fa5s.indent", "fa5s.industry", "fa5s.info",
  "fa5s.info-circle", "fa5s.italic", "fa5s.key", "fa5s.keyboard", "fa5s.language", "fa5s.laptop", "fa5s.leaf",
  "fa5s.lemon", "fa5s.level-down-alt", "fa5s.level-up-alt", "fa5s.life-ring", "fa5s.lightbulb", "fa5s.link",
  "fa5s.lira-sign", "fa5s.list", "fa5s.list-alt", "fa5s.list-ol", "fa5s.list-ul", "fa5s.location-arrow", "fa5s.lock",
  "fa5s.lock-open", "fa5s.long-arrow-alt-down", "fa5s.long-arrow-alt-left", "fa5s.long-arrow-alt-right",
  "fa5s.long-arrow-alt-up", "fa5s.low-vision", "fa5s.magic", "fa5s.magnet", "fa5s.male", "fa5s.map", "fa5s.map-marker",
  "fa5s.map-marker-alt", "fa5s.map-pin", "fa5s.map-signs", "fa5s.mars", "fa5s.mars-double", "fa5s.mars-stroke",
  "fa5s.mars-stroke-h", "fa5s.mars-stroke-v", "fa5s.medkit", "fa5s.meh", "fa5s.mercury", "fa5s.microchip",
  "fa5s.microphone", "fa5s.microphone-slash", "fa5s.minus", "fa5s.minus-circle", "fa5s.minus-square", "fa5s.mobile",
  "fa5s.mobile-alt", "fa5s.money-bill-alt", "fa5s.moon", "fa5s.motorcycle", "fa5s.mouse-pointer", "fa5s.music",
  "fa5s.neuter", "fa5s.newspaper", "fa5s.notes-medical", "fa5s.object-group", "fa5s.object-ungroup", "fa5s.outdent",
  "fa5s.paint-brush", "fa5s.pallet", "fa5s.paper-plane", "fa5s.paperclip", "fa5s.parachute-box", "fa5s.paragraph",
  "fa5s.paste", "fa5s.pause", "fa5s.pause-circle", "fa5s.paw", "fa5s.pen-square", "fa5s.pencil-alt",
  "fa5s.people-carry", "fa5s.percent", "fa5s.phone", "fa5s.phone-slash", "fa5s.phone-square", "fa5s.phone-volume",
  "fa5s.piggy-bank", "fa5s.pills", "fa5s.plane", "fa5s.play", "fa5s.play-circle", "fa5s.plug", "fa5s.plus",
  "fa5s.plus-circle", "fa5s.plus-square", "fa5s.podcast", "fa5s.poo", "fa5s.pound-sign", "fa5s.power-off",
  "fa5s.prescription-bottle", "fa5s.prescription-bottle-alt", "fa5s.print", "fa5s.procedures", "fa5s.puzzle-piece",
  "fa5s.qrcode", "fa5s.question", "fa5s.question-circle", "fa5s.quidditch", "fa5s.quote-left", "fa5s.quote-right",
  "fa5s.random", "fa5s.recycle", "fa5s.redo", "fa5s.redo-alt", "fa5s.registered", "fa5s.reply", "fa5s.reply-all",
  "fa5s.retweet", "fa5s.ribbon", "fa5s.road", "fa5s.rocket", "fa5s.rss", "fa5s.rss-square", "fa5s.ruble-sign",
  "fa5s.rupee-sign", "fa5s.save", "fa5s.search", "fa5s.search-minus", "fa5s.search-plus", "fa5s.seedling",
  "fa5s.server", "fa5s.share", "fa5s.share-alt", "fa5s.share-alt-square", "fa5s.share-square", "fa5s.shekel-sign",
  "fa5s.shield-alt", "fa5s.ship", "fa5s.shipping-fast", "fa5s.shopping-bag", "fa5s.shopping-basket",
  "fa5s.shopping-cart", "fa5s.shower", "fa5s.sign", "fa5s.sign-in-alt", "fa5s.sign-language", "fa5s.sign-out-alt",
  "fa5s.signal", "fa5s.sitemap", "fa5s.sliders-h", "fa5s.smile", "fa5s.smoking", "fa5s.snowflake", "fa5s.sort",
  "fa5s.sort-alpha-down", "fa5s.sort-alpha-up", "fa5s.sort-amount-down", "fa5s.sort-amount-up", "fa5s.sort-down",
  "fa5s.sort-numeric-down", "fa5s.sort-numeric-up", "fa5s.sort-up", "fa5s.space-shuttle", "fa5s.spinner", "fa5s.square",
  "fa5s.square-full", "fa5s.star", "fa5s.star-half", "fa5s.step-backward", "fa5s.step-forward", "fa5s.stethoscope",
  "fa5s.sticky-note", "fa5s.stop", "fa5s.stop-circle", "fa5s.stopwatch", "fa5s.street-view", "fa5s.strikethrough",
  "fa5s.subscript", "fa5s.subway", "fa5s.suitcase", "fa5s.sun", "fa5s.superscript", "fa5s.sync", "fa5s.sync-alt",
  "fa5s.syringe", "fa5s.table", "fa5s.table-tennis", "fa5s.tablet", "fa5s.tablet-alt", "fa5s.tablets",
  "fa5s.tachometer-alt", "fa5s.tag", "fa5s.tags", "fa5s.tape", "fa5s.tasks", "fa5s.taxi", "fa5s.terminal",
  "fa5s.text-height", "fa5s.text-width", "fa5s.th", "fa5s.th-large", "fa5s.th-list", "fa5s.thermometer",
  "fa5s.thermometer-empty", "fa5s.thermometer-full", "fa5s.thermometer-half", "fa5s.thermometer-quarter",
  "fa5s.thermometer-three-quarters", "fa5s.thumbs-down", "fa5s.thumbs-up", "fa5s.thumbtack", "fa5s.ticket-alt",
  "fa5s.times", "fa5s.times-circle", "fa5s.tint", "fa5s.toggle-off", "fa5s.toggle-on", "fa5s.trademark", "fa5s.train",
  "fa5s.transgender", "fa5s.transgender-alt", "fa5s.trash", "fa5s.trash-alt", "fa5s.tree", "fa5s.trophy", "fa5s.truck",
  "fa5s.truck-loading", "fa5s.truck-moving", "fa5s.tty", "fa5s.tv", "fa5s.umbrella", "fa5s.underline", "fa5s.undo",
  "fa5s.undo-alt", "fa5s.universal-access", "fa5s.university", "fa5s.unlink", "fa5s.unlock", "fa5s.unlock-alt",
  "fa5s.upload", "fa5s.user", "fa5s.user-circle", "fa5s.user-md", "fa5s.user-plus", "fa5s.user-secret",
  "fa5s.user-times", "fa5s.users", "fa5s.utensil-spoon", "fa5s.utensils", "fa5s.venus", "fa5s.venus-double",
  "fa5s.venus-mars", "fa5s.vial", "fa5s.vials", "fa5s.video", "fa5s.video-slash", "fa5s.volleyball-ball",
  "fa5s.volume-down", "fa5s.volume-off", "fa5s.volume-up", "fa5s.warehouse", "fa5s.weight", "fa5s.wheelchair",
  "fa5s.wifi", "fa5s.window-close", "fa5s.window-maximize", "fa5s.window-minimize", "fa5s.window-restore",
  "fa5s.wine-glass", "fa5s.won-sign", "fa5s.wrench", "fa5s.x-ray", "fa5s.yen-sign", "far fa-address-book",
  "far fa-address-card", "far fa-arrow-alt-circle-down", "far fa-arrow-alt-circle-left",
  "far fa-arrow-alt-circle-right", "far fa-arrow-alt-circle-up", "far fa-bell", "far fa-bell-slash", "far fa-bookmark",
  "far fa-building", "far fa-calendar", "far fa-calendar-alt", "far fa-calendar-check", "far fa-calendar-minus",
  "far fa-calendar-plus", "far fa-calendar-times", "far fa-caret-square-down", "far fa-caret-square-left",
  "far fa-caret-square-right", "far fa-caret-square-up", "far fa-chart-bar", "far fa-check-circle",
  "far fa-check-square", "far fa-circle", "far fa-clipboard", "far fa-clock", "far fa-clone",
  "far fa-closed-captioning", "far fa-comment", "far fa-comment-alt", "far fa-comments", "far fa-compass",
  "far fa-copy", "far fa-copyright", "far fa-credit-card", "far fa-dot-circle", "far fa-edit", "far fa-envelope",
  "far fa-envelope-open", "far fa-eye-slash", "far fa-file", "far fa-file-alt", "far fa-file-archive",
  "far fa-file-audio", "far fa-file-code", "far fa-file-excel", "far fa-file-image", "far fa-file-pdf",
  "far fa-file-powerpoint", "far fa-file-video", "far fa-file-word", "far fa-flag", "far fa-folder",
  "far fa-folder-open", "far fa-frown", "far fa-futbol", "far fa-gem", "far fa-hand-lizard", "far fa-hand-paper",
  "far fa-hand-peace", "far fa-hand-point-down", "far fa-hand-point-left", "far fa-hand-point-right",
  "far fa-hand-point-up", "far fa-hand-pointer", "far fa-hand-rock", "far fa-hand-scissors", "far fa-hand-spock",
  "far fa-handshake", "far fa-hdd", "far fa-heart", "far fa-hospital", "far fa-hourglass", "far fa-id-badge",
  "far fa-id-card", "far fa-image", "far fa-images", "far fa-keyboard", "far fa-lemon", "far fa-life-ring",
  "far fa-lightbulb", "far fa-list-alt", "far fa-map", "far fa-meh", "far fa-minus-square", "far fa-money-bill-alt",
  "far fa-moon", "far fa-newspaper", "far fa-object-group", "far fa-object-ungroup", "far fa-paper-plane",
  "far fa-pause-circle", "far fa-play-circle", "far fa-plus-square", "far fa-question-circle", "far fa-registered",
  "far fa-save", "far fa-share-square", "far fa-smile", "far fa-snowflake", "far fa-square", "far fa-star",
  "far fa-star-half", "far fa-sticky-note", "far fa-stop-circle", "far fa-sun", "far fa-thumbs-down",
  "far fa-thumbs-up", "far fa-times-circle", "far fa-trash-alt", "far fa-user", "far fa-user-circle",
  "far fa-window-close", "far fa-window-maximize", "far fa-window-minimize", "far fa-window-restore", "fab fa-500px",
  "fab fa-accessible-icon", "fab fa-accusoft", "fab fa-adn", "fab fa-adversal", "fab fa-affiliatetheme",
  "fab fa-algolia", "fab fa-amazon", "fab fa-amazon-pay", "fab fa-amilia", "fab fa-android", "fab fa-angellist",
  "fab fa-angrycreative", "fab fa-angular", "fab fa-app-store", "fab fa-app-store-ios", "fab fa-apper", "fab fa-apple",
  "fab fa-apple-pay", "fab fa-asymmetrik", "fab fa-audible", "fab fa-autoprefixer", "fab fa-avianex", "fab fa-aviato",
  "fab fa-aws", "fab fa-bandcamp", "fab fa-behance", "fab fa-behance-square", "fab fa-bimobject", "fab fa-bitbucket",
  "fab fa-bitcoin", "fab fa-bity", "fab fa-black-tie", "fab fa-blackberry", "fab fa-blogger", "fab fa-blogger-b",
  "fab fa-bluetooth", "fab fa-bluetooth-b", "fab fa-btc", "fab fa-buromobelexperte", "fab fa-buysellads",
  "fab fa-cc-amazon-pay", "fab fa-cc-amex", "fab fa-cc-apple-pay", "fab fa-cc-diners-club", "fab fa-cc-discover",
  "fab fa-cc-jcb", "fab fa-cc-mastercard", "fab fa-cc-paypal", "fab fa-cc-stripe", "fab fa-cc-visa",
  "fab fa-centercode", "fab fa-chrome", "fab fa-cloudscale", "fab fa-cloudsmith", "fab fa-cloudversify",
  "fab fa-codepen", "fab fa-codiepie", "fab fa-connectdevelop", "fab fa-contao", "fab fa-cpanel",
  "fab fa-creative-commons", "fab fa-css3", "fab fa-css3-alt", "fab fa-cuttlefish", "fab fa-d-and-d", "fab fa-dashcube",
  "fab fa-delicious", "fab fa-deploydog", "fab fa-deskpro", "fab fa-deviantart", "fab fa-digg", "fab fa-digital-ocean",
  "fab fa-discord", "fab fa-discourse", "fab fa-dochub", "fab fa-docker", "fab fa-draft2digital", "fab fa-dribbble",
  "fab fa-dribbble-square", "fab fa-dropbox", "fab fa-drupal", "fab fa-dyalog", "fab fa-earlybirds", "fab fa-edge",
  "fab fa-elementor", "fab fa-ember", "fab fa-empire", "fab fa-envira", "fab fa-erlang", "fab fa-ethereum",
  "fab fa-etsy", "fab fa-expeditedssl", "fab fa-facebook", "fab fa-facebook-f", "fab fa-facebook-messenger",
  "fab fa-facebook-square", "fab fa-firefox", "fab fa-first-order", "fab fa-firstdraft", "fab fa-flickr",
  "fab fa-flipboard", "fab fa-fly", "fab fa-font-awesome", "fab fa-font-awesome-alt", "fab fa-font-awesome-flag",
  "fab fa-fonticons", "fab fa-fonticons-fi", "fab fa-fort-awesome", "fab fa-fort-awesome-alt", "fab fa-forumbee",
  "fab fa-foursquare", "fab fa-free-code-camp", "fab fa-freebsd", "fab fa-get-pocket", "fab fa-gg", "fab fa-gg-circle",
  "fab fa-git", "fab fa-git-square", "fab fa-github", "fab fa-github-alt", "fab fa-github-square", "fab fa-gitkraken",
  "fab fa-gitlab", "fab fa-gitter", "fab fa-glide", "fab fa-glide-g", "fab fa-gofore", "fab fa-goodreads",
  "fab fa-goodreads-g", "fab fa-google", "fab fa-google-drive", "fab fa-google-play", "fab fa-google-plus",
  "fab fa-google-plus-g", "fab fa-google-plus-square", "fab fa-google-wallet", "fab fa-gratipay", "fab fa-grav",
  "fab fa-gripfire", "fab fa-grunt", "fab fa-gulp", "fab fa-hacker-news", "fab fa-hacker-news-square", "fab fa-hips",
  "fab fa-hire-a-helper", "fab fa-hooli", "fab fa-hotjar", "fab fa-houzz", "fab fa-html5", "fab fa-hubspot",
  "fab fa-imdb", "fab fa-instagram", "fab fa-internet-explorer", "fab fa-ioxhost", "fab fa-itunes",
  "fab fa-itunes-note", "fab fa-jenkins", "fab fa-joget", "fab fa-joomla", "fab fa-js", "fab fa-js-square",
  "fab fa-jsfiddle", "fab fa-keycdn", "fab fa-kickstarter", "fab fa-kickstarter-k", "fab fa-korvue", "fab fa-laravel",
  "fab fa-lastfm", "fab fa-lastfm-square", "fab fa-leanpub", "fab fa-less", "fab fa-line", "fab fa-linkedin",
  "fab fa-linkedin-in", "fab fa-linode", "fab fa-linux", "fab fa-lyft", "fab fa-magento", "fab fa-maxcdn",
  "fab fa-medapps", "fab fa-medium", "fab fa-medium-m", "fab fa-medrt", "fab fa-meetup", "fab fa-microsoft",
  "fab fa-mix", "fab fa-mixcloud", "fab fa-mizuni", "fab fa-modx", "fab fa-monero", "fab fa-napster",
  "fab fa-nintendo-switch", "fab fa-node", "fab fa-node-js", "fab fa-npm", "fab fa-ns8", "fab fa-nutritionix",
  "fab fa-odnoklassniki", "fab fa-odnoklassniki-square", "fab fa-opencart", "fab fa-openid", "fab fa-opera",
  "fab fa-optin-monster", "fab fa-osi", "fab fa-page4", "fab fa-pagelines", "fab fa-palfed", "fab fa-patreon",
  "fab fa-paypal", "fab fa-periscope", "fab fa-phabricator", "fab fa-phoenix-framework", "fab fa-php",
  "fab fa-pied-piper", "fab fa-pied-piper-alt", "fab fa-pied-piper-pp", "fab fa-pinterest", "fab fa-pinterest-p",
  "fab fa-pinterest-square", "fab fa-playstation", "fab fa-product-hunt", "fab fa-pushed", "fab fa-python", "fab fa-qq",
  "fab fa-quinscape", "fab fa-quora", "fab fa-ravelry", "fab fa-react", "fab fa-readme", "fab fa-rebel",
  "fab fa-red-river", "fab fa-reddit", "fab fa-reddit-alien", "fab fa-reddit-square", "fab fa-rendact", "fab fa-renren",
  "fab fa-replyd", "fab fa-resolving", "fab fa-rocketchat", "fab fa-rockrms", "fab fa-safari", "fab fa-sass",
  "fab fa-schlix", "fab fa-scribd", "fab fa-searchengin", "fab fa-sellcast", "fab fa-sellsy", "fab fa-servicestack",
  "fab fa-shirtsinbulk", "fab fa-simplybuilt", "fab fa-sistrix", "fab fa-skyatlas", "fab fa-skype", "fab fa-slack",
  "fab fa-slack-hash", "fab fa-slideshare", "fab fa-snapchat", "fab fa-snapchat-ghost", "fab fa-snapchat-square",
  "fab fa-soundcloud", "fab fa-speakap", "fab fa-spotify", "fab fa-stack-exchange", "fab fa-stack-overflow",
  "fab fa-staylinked", "fab fa-steam", "fab fa-steam-square", "fab fa-steam-symbol", "fab fa-sticker-mule",
  "fab fa-strava", "fab fa-stripe", "fab fa-stripe-s", "fab fa-studiovinari", "fab fa-stumbleupon",
  "fab fa-stumbleupon-circle", "fab fa-superpowers", "fab fa-supple", "fab fa-telegram", "fab fa-telegram-plane",
  "fab fa-tencent-weibo", "fab fa-themeisle", "fab fa-trello", "fab fa-tripadvisor", "fab fa-tumblr",
  "fab fa-tumblr-square", "fab fa-twitch", "fab fa-twitter", "fab fa-twitter-square", "fab fa-typo3", "fab fa-uber",
  "fab fa-uikit", "fab fa-uniregistry", "fab fa-untappd", "fab fa-usb", "fab fa-ussunnah", "fab fa-vaadin",
  "fab fa-viacoin", "fab fa-viadeo", "fab fa-viadeo-square", "fab fa-viber", "fab fa-vimeo", "fab fa-vimeo-square",
  "fab fa-vimeo-v", "fab fa-vine", "fab fa-vk", "fab fa-vnv", "fab fa-vuejs", "fab fa-weibo", "fab fa-weixin",
  "fab fa-whatsapp", "fab fa-whatsapp-square", "fab fa-whmcs", "fab fa-wikipedia-w", "fab fa-windows",
  "fab fa-wordpress", "fab fa-wordpress-simple", "fab fa-wpbeginner", "fab fa-wpexplorer", "fab fa-wpforms",
  "fab fa-xbox", "fab fa-xing", "fab fa-xing-square", "fab fa-y-combinator", "fab fa-yahoo", "fab fa-yandex",
  "fab fa-yandex-international", "fab fa-yelp", "fab fa-yoast", "fab fa-youtube", "fab fa-youtube-square"
]
