""" Long strings and dictionaries/JSON that would obfuscate code """
from typing import Any

defaultDocTypes: list[list[str]] = [
  #docType,       PURL, title,          icon,                   shortcut, view
  ['x0',                 'http://purl.obolibrary.org/obo/NCIT_C47885',  'Projects',     '',                     'space', 'name,tags,.status,.objective,comment'],
  ['x1',                 'http://purl.obolibrary.org/obo/NCIT_C101129', 'Folders',      '',                      '',     ''],
  ['measurement',        'http://purl.obolibrary.org/obo/NCIT_C42790',  'Measurements', 'fa5s.thermometer-half', 'm',    'name,tags,comment,type,image,.sample,.workflow/procedure'],
  ['sample',             'http://purl.obolibrary.org/obo/NCIT_C19157',  'Samples',      'fa5s.vial',             's',    'name,tags,.chemistry,comment,qrCodes'],
  ['workflow',           'http://purl.obolibrary.org/obo/NCIT_C42753',  'Workflows',    'fa5s.list-ol',          'w',    'name,tags,comment'],
  ['workflow/procedure', 'https://schema.org/procedure',                'Procedure',    'fa5s.list-ol',          'w',    'name,tags,comment,content'],
  ['workflow/workplan' , 'http://purl.obolibrary.org/obo/PROCO_0000093','Work plan',    'fa5s.list-ol',          'w',    'name,tags,comment,content'],
  ['workflow/worklog'  , '',                                            'Work log',     'fa5s.list-ol',          'w',    'name,tags,comment,content'],
  ['instrument',         'http://purl.obolibrary.org/obo/NCIT_C16742',  'Instruments',  'ri.scales-2-line',      'i',    'name,tags,comment,.vendor']
]


defaultSchema: list[list[str|int]] = [
  #docType,            group,index,key,        unit, mandatory, list
  ['x0',                  '', 0,   'name',      '',   'T',       ''],
  ['x0',                  '', 1,   'tags',      '',   '',        ''],
  ['x0',                  '', 2,   'status',    '',   '',        'active,paused,passive,finished'],
  ['x0',                  '', 3,   'objective', '',   '',        ''],
  ['x0',                  '', 4,   'comment',   '',   '',        ''],
  ['x1',                  '', 0,   'name',      '',   'T',       ''],
  ['x1',                  '', 1,   'tags',      '',   '',        ''],
  ['x1',                  '', 2,   'comment',   '',   '',        ''],
  ['measurement',         '', 0,   'name',      '',   'T',       ''],
  ['measurement',         '', 1,   'tags',      '',   '',        ''],
  ['measurement',         '', 2,   'comment',   '',   '',        ''],
  ['measurement',         '', 3,   'sample',    '',   '',        'sample'],
  ['measurement',         '', 4,   'workflow/procedure','','','workflow/procedure'],
  ['sample',              '', 0,   'name',      '',   'T',       ''],
  ['sample',              '', 1,   'tags',      '',   '',        ''],
  ['sample',              '', 2,   'chemistry', '',   '',        ''],
  ['sample',              '', 3,   'comment',   '',   '',        ''],
  ['sample',              '', 4,   'qrCodes',   '',   '',        ''],
  ['sample',      'geometry', 0,   'height',    'mm', '',        ''],
  ['sample',      'geometry', 1,   'width',     'mm', '',        ''],
  ['sample',      'geometry', 2,   'length',    'mm', '',        ''],
  ['workflow',            '', 0,   'name',      '',   'T',       ''],
  ['workflow',            '', 1,   'tags',      '',   '',        ''],
  ['workflow',            '', 2,   'comment',   '',   '',        ''],
  ['workflow',            '', 3,   'content',   '',   '',        ''],
  ['instrument',          '', 0,   'name',      '',   'T',       ''],
  ['instrument',          '', 1,   'tags',      '',   '',        ''],
  ['instrument',          '', 2,   'comment',   '',   '',        ''],
  ['instrument',          '', 3,   'vendor',    '',   '',        ''],
  ['instrument/extension','', 0,   'name',      '',   'T',       ''],
  ['instrument/extension','', 1,   'tags',      '',   '',        ''],
  ['instrument/extension','', 2,   'comment',   '',   '',        ''],
  ['instrument/extension','', 3,   'vendor',    '',   '',        '']
]


defaultDefinitions = [
  ['name',              'What is the name this item?',                                    ''],
  ['tags',              'What are the tags?',                                             ''],
  ['status',            'What is the project status',                                     ''],
  ['objective',         'What is the objective?',                                         ''],
  ['comment',           'What are the comments?',                                         ''],
  ['content',           'What is procedure (Markdown possible; autofill if file given)?', ''],
  ['vendor',            'Who is the vendor?',                                             ''],
  ['sample',            'Which sample was used?',                                         ''],
  ['workflow/procedure','Which procedure was used?',                                      ''],
  ['chemistry',         'What is its chemical composition?',                              ''],
  ['qrCodes',           '',                                                               ''],
  ['geometry.width',    'Sample width',                                                   ''],
  ['geometry.length',   'Sample length',                                                  ''],
  ['geometry.height',   'Sample height',                         'https://schema.org/height']
]


defaultDataHierarchyNode: list[dict[str, str]] = [
  {'docType':'-','class':'','idx':'0','name':'name',   'query':'What is the name?',     'unit':'','PURL':'','mandatory':'T','list':''},
  {'docType':'-','class':'','idx':'1','name':'tags',   'query':'What are the tags?',    'unit':'','PURL':'','mandatory':'','list':''},
  {'docType':'-','class':'','idx':'2','name':'comment','query':'What are the comments?','unit':'','PURL':'','mandatory':'','list':''}
  ]


CONF_FILE_NAME = '.pastaELN.json'

defaultConfiguration: dict[str, Any] = {
  'defaultProjectGroup': 'research',
  'userID': '$os.getlogin()$',
  'version': 0,
  'qrPrinter': {},
  'authors': [{'first': '', 'last': '', 'title': '', 'email': '', 'orcid': '',
               'organizations': [{'organization': '', 'rorid': ''}]}],
  'GUI': {},
  'projectGroups': {}
}

# level 1: type of property
#   within each: array of 3: description, default, all_choices
configurationGUI: dict[str, Any] = {
  'general': {
    'theme': ['Color style', 'none', ['amber', 'blue', 'cyan', 'pink', 'purple', 'teal', 'yellow', 'none']],
    'loggingLevel': ['Logging level (more->less)', 'INFO', ['DEBUG', 'INFO', 'WARNING', 'ERROR']],
    'autosave': ['Autosave entries in form', 'No', ['Yes', 'No']],
    'showProjectBtn': ['Show project button on top-left', 'Yes', ['Yes', 'No']]
  },
  'dimensions': {
    'sidebarWidth': ['Sidebar width', 280, [220, 280, 340]],
    'maxTableColumnWidth': ['Maximum column width in tables', 400, [300, 400, 500, 600]],
    'imageSizeDetails': ['Image size in details view and form', 600, [300, 400, 500, 600]],
    'imageWidthProject': ['Image width in project view', 300, [200, 250, 300, 350, 400]],
    'maxProjectLeafHeight': ['Maximum height of item in project view', 250, [200, 250, 300, 400]],
    'widthContent': ['Width of procedures in project view', 600, [400, 500, 600, 700]],
    'docTypeOffset': ['Offset of document type in project view', 500, [400, 500, 600, 700]],
    'frameSize': ['Frame width around items in project view', 6, [4, 6, 8, 10]],
  }
}


DEFAULT_COLORS_PALETTE:dict[str,dict[str,str]] = {
    'dark': {
        'text': '#EEEEEE',
        'leafX': '#222222',
        'leafO': '#333333',
        'leafShadow': 'black',
    },
    'light': {
        'text': '#111111',
        'leafX': '#EEEEEE',
        'leafO': '#FFFFFF',
        'leafShadow': '#AAAAAA',
    },
}

SQLiteTranslationDict = {"'":'&prime;'}
SQLiteTranslation     = str.maketrans(SQLiteTranslationDict)

minimalDocInForm = {'tags':[], 'comment':'', '':{}}

SORTED_KEYS     = ['name', 'tags', 'comment', 'metaUser', '']
SORTED_DB_KEYS  = ['id', 'type', 'dateCreated','dateModified','dateSync', 'user','branch','gui','client','externalId','shasum']
DO_NOT_RENDER   = ['image','content','metaVendor','shasum','type','branch','gui','dateCreated',
                 'dateModified','id','user','name','externalId','client','elnIdentifier','oldIdentifier']

AboutMessage  = '### PASTA-ELN | The favorite ELN for experimental scientists\n\nPASTA-ELN provides a streamlined '\
                'and efficient solution for experimental scientists\n\n to manage and organize raw data alongside '\
                'associated metadata.\n\n'

setupText = """
### Welcome to the PASTA-ELN setup
Three components are needed for proper functioning of PASTA-ELN:
- Configuration of preferences
- Shortcut creation
- Example project creation

This setup will analyse and (possibly) correct these items.
If an attempt fails: please follow to this [website](https://pasta-eln.github.io/pasta-eln/install.html).
"""


exampleDataString = """
Do you want to create an example project?

This step helps to verify the installation and provides an helpful example for new users.

!WARNING! This process will RESET everything and thereby DELETE EVERYTHING since you installed pastaELN.

This step usually takes up to 20sec, so please be patient. Sometimes, Linux mentions that the program
is not responding and asks if to close/wait. Please WAIT.
"""

shortcuts = """
### Default shortcuts:

**Ctrl+Space**: List projects

**Ctrl+M**: List measurements

**Ctrl+S**: List samples

**Ctrl+W**: List workflows

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

# FontAwesome 5 icons
allIcons = ['fa5s.address-book', 'fa5s.address-card', 'fa5s.adjust', 'fa5s.align-center', 'fa5s.align-justify',
            'fa5s.align-left', 'fa5s.align-right', 'fa5s.allergies', 'fa5s.ambulance',
            'fa5s.american-sign-language-interpreting', 'fa5s.anchor', 'fa5s.angle-double-down',
            'fa5s.angle-double-left', 'fa5s.angle-double-right', 'fa5s.angle-double-up', 'fa5s.angle-down',
            'fa5s.angle-left', 'fa5s.angle-right', 'fa5s.angle-up', 'fa5s.archive', 'fa5s.arrow-alt-circle-down',
            'fa5s.arrow-alt-circle-left', 'fa5s.arrow-alt-circle-right', 'fa5s.arrow-alt-circle-up',
            'fa5s.arrow-circle-down', 'fa5s.arrow-circle-left', 'fa5s.arrow-circle-right', 'fa5s.arrow-circle-up',
            'fa5s.arrow-down', 'fa5s.arrow-left', 'fa5s.arrow-right', 'fa5s.arrow-up', 'fa5s.arrows-alt',
            'fa5s.arrows-alt-h', 'fa5s.arrows-alt-v', 'fa5s.assistive-listening-systems', 'fa5s.asterisk', 'fa5s.at',
            'fa5s.audio-description', 'fa5s.backward', 'fa5s.balance-scale', 'fa5s.ban', 'fa5s.band-aid',
            'fa5s.barcode', 'fa5s.bars', 'fa5s.baseball-ball', 'fa5s.basketball-ball', 'fa5s.bath',
            'fa5s.battery-empty', 'fa5s.battery-full', 'fa5s.battery-half', 'fa5s.battery-quarter',
            'fa5s.battery-three-quarters', 'fa5s.bed', 'fa5s.beer', 'fa5s.bell', 'fa5s.bell-slash', 'fa5s.bicycle',
            'fa5s.binoculars', 'fa5s.birthday-cake', 'fa5s.blind', 'fa5s.bold', 'fa5s.bolt', 'fa5s.bomb', 'fa5s.book',
            'fa5s.bookmark', 'fa5s.bowling-ball', 'fa5s.box', 'fa5s.box-open', 'fa5s.boxes', 'fa5s.braille',
            'fa5s.briefcase', 'fa5s.briefcase-medical', 'fa5s.bug', 'fa5s.building', 'fa5s.bullhorn', 'fa5s.bullseye',
            'fa5s.burn', 'fa5s.bus', 'fa5s.calculator', 'fa5s.calendar', 'fa5s.calendar-alt', 'fa5s.calendar-check',
            'fa5s.calendar-minus', 'fa5s.calendar-plus', 'fa5s.calendar-times', 'fa5s.camera', 'fa5s.camera-retro',
            'fa5s.capsules', 'fa5s.car', 'fa5s.caret-down', 'fa5s.caret-left', 'fa5s.caret-right',
            'fa5s.caret-square-down', 'fa5s.caret-square-left', 'fa5s.caret-square-right', 'fa5s.caret-square-up',
            'fa5s.caret-up', 'fa5s.cart-arrow-down', 'fa5s.cart-plus', 'fa5s.certificate', 'fa5s.chart-area',
            'fa5s.chart-bar', 'fa5s.chart-line', 'fa5s.chart-pie', 'fa5s.check', 'fa5s.check-circle',
            'fa5s.check-square', 'fa5s.chess', 'fa5s.chess-bishop', 'fa5s.chess-board', 'fa5s.chess-king',
            'fa5s.chess-knight', 'fa5s.chess-pawn', 'fa5s.chess-queen', 'fa5s.chess-rook', 'fa5s.chevron-circle-down',
            'fa5s.chevron-circle-left', 'fa5s.chevron-circle-right', 'fa5s.chevron-circle-up', 'fa5s.chevron-down',
            'fa5s.chevron-left', 'fa5s.chevron-right', 'fa5s.chevron-up', 'fa5s.child', 'fa5s.circle',
            'fa5s.circle-notch', 'fa5s.clipboard', 'fa5s.clipboard-check', 'fa5s.clipboard-list', 'fa5s.clock',
            'fa5s.clone', 'fa5s.closed-captioning', 'fa5s.cloud', 'fa5s.cloud-download-alt', 'fa5s.cloud-upload-alt',
            'fa5s.code', 'fa5s.code-branch', 'fa5s.coffee', 'fa5s.cog', 'fa5s.cogs', 'fa5s.columns', 'fa5s.comment',
            'fa5s.comment-alt', 'fa5s.comment-dots', 'fa5s.comment-slash', 'fa5s.comments', 'fa5s.compass',
            'fa5s.compress', 'fa5s.copy', 'fa5s.copyright', 'fa5s.couch', 'fa5s.credit-card', 'fa5s.crop',
            'fa5s.crosshairs', 'fa5s.cube', 'fa5s.cubes', 'fa5s.cut', 'fa5s.database', 'fa5s.deaf', 'fa5s.desktop',
            'fa5s.diagnoses', 'fa5s.dna', 'fa5s.dollar-sign', 'fa5s.dolly', 'fa5s.dolly-flatbed', 'fa5s.donate',
            'fa5s.dot-circle', 'fa5s.dove', 'fa5s.download', 'fa5s.edit', 'fa5s.eject', 'fa5s.ellipsis-h',
            'fa5s.ellipsis-v', 'fa5s.envelope', 'fa5s.envelope-open', 'fa5s.envelope-square', 'fa5s.eraser',
            'fa5s.euro-sign', 'fa5s.exchange-alt', 'fa5s.exclamation', 'fa5s.exclamation-circle',
            'fa5s.exclamation-triangle', 'fa5s.expand', 'fa5s.expand-arrows-alt', 'fa5s.external-link-alt',
            'fa5s.external-link-square-alt', 'fa5s.eye', 'fa5s.eye-dropper', 'fa5s.eye-slash', 'fa5s.fast-backward',
            'fa5s.fast-forward', 'fa5s.fax', 'fa5s.female', 'fa5s.fighter-jet', 'fa5s.file', 'fa5s.file-alt',
            'fa5s.file-archive', 'fa5s.file-audio', 'fa5s.file-code', 'fa5s.file-excel', 'fa5s.file-image',
            'fa5s.file-medical', 'fa5s.file-medical-alt', 'fa5s.file-pdf', 'fa5s.file-powerpoint', 'fa5s.file-video',
            'fa5s.file-word', 'fa5s.film', 'fa5s.filter', 'fa5s.fire', 'fa5s.fire-extinguisher', 'fa5s.first-aid',
            'fa5s.flag', 'fa5s.flag-checkered', 'fa5s.flask', 'fa5s.folder', 'fa5s.folder-open', 'fa5s.font',
            'fa5s.football-ball', 'fa5s.forward', 'fa5s.frown', 'fa5s.futbol', 'fa5s.gamepad', 'fa5s.gavel', 'fa5s.gem',
            'fa5s.genderless', 'fa5s.gift', 'fa5s.glass-martini', 'fa5s.globe', 'fa5s.golf-ball', 'fa5s.graduation-cap',
            'fa5s.h-square', 'fa5s.hand-holding', 'fa5s.hand-holding-heart', 'fa5s.hand-holding-usd',
            'fa5s.hand-lizard', 'fa5s.hand-paper', 'fa5s.hand-peace', 'fa5s.hand-point-down', 'fa5s.hand-point-left',
            'fa5s.hand-point-right', 'fa5s.hand-point-up', 'fa5s.hand-pointer', 'fa5s.hand-rock', 'fa5s.hand-scissors',
            'fa5s.hand-spock', 'fa5s.hands', 'fa5s.hands-helping', 'fa5s.handshake', 'fa5s.hashtag', 'fa5s.hdd',
            'fa5s.heading', 'fa5s.headphones', 'fa5s.heart', 'fa5s.heartbeat', 'fa5s.history', 'fa5s.hockey-puck',
            'fa5s.home', 'fa5s.hospital', 'fa5s.hospital-alt', 'fa5s.hospital-symbol', 'fa5s.hourglass',
            'fa5s.hourglass-end', 'fa5s.hourglass-half', 'fa5s.hourglass-start', 'fa5s.i-cursor', 'fa5s.id-badge',
            'fa5s.id-card', 'fa5s.id-card-alt', 'fa5s.image', 'fa5s.images', 'fa5s.inbox', 'fa5s.indent',
            'fa5s.industry', 'fa5s.info', 'fa5s.info-circle', 'fa5s.italic', 'fa5s.key', 'fa5s.keyboard',
            'fa5s.language', 'fa5s.laptop', 'fa5s.leaf', 'fa5s.lemon', 'fa5s.level-down-alt', 'fa5s.level-up-alt',
            'fa5s.life-ring', 'fa5s.lightbulb', 'fa5s.link', 'fa5s.lira-sign', 'fa5s.list', 'fa5s.list-alt',
            'fa5s.list-ol', 'fa5s.list-ul', 'fa5s.location-arrow', 'fa5s.lock', 'fa5s.lock-open',
            'fa5s.long-arrow-alt-down', 'fa5s.long-arrow-alt-left', 'fa5s.long-arrow-alt-right',
            'fa5s.long-arrow-alt-up', 'fa5s.low-vision', 'fa5s.magic', 'fa5s.magnet', 'fa5s.male', 'fa5s.map',
            'fa5s.map-marker', 'fa5s.map-marker-alt', 'fa5s.map-pin', 'fa5s.map-signs', 'fa5s.mars', 'fa5s.mars-double',
            'fa5s.mars-stroke', 'fa5s.mars-stroke-h', 'fa5s.mars-stroke-v', 'fa5s.medkit', 'fa5s.meh', 'fa5s.mercury',
            'fa5s.microchip', 'fa5s.microphone', 'fa5s.microphone-slash', 'fa5s.minus', 'fa5s.minus-circle',
            'fa5s.minus-square', 'fa5s.mobile', 'fa5s.mobile-alt', 'fa5s.money-bill-alt', 'fa5s.moon',
            'fa5s.motorcycle', 'fa5s.mouse-pointer', 'fa5s.music', 'fa5s.neuter', 'fa5s.newspaper',
            'fa5s.notes-medical', 'fa5s.object-group', 'fa5s.object-ungroup', 'fa5s.outdent', 'fa5s.paint-brush',
            'fa5s.pallet', 'fa5s.paper-plane', 'fa5s.paperclip', 'fa5s.parachute-box', 'fa5s.paragraph', 'fa5s.paste',
            'fa5s.pause', 'fa5s.pause-circle', 'fa5s.paw', 'fa5s.pen-square', 'fa5s.pencil-alt', 'fa5s.people-carry',
            'fa5s.percent', 'fa5s.phone', 'fa5s.phone-slash', 'fa5s.phone-square', 'fa5s.phone-volume',
            'fa5s.piggy-bank', 'fa5s.pills', 'fa5s.plane', 'fa5s.play', 'fa5s.play-circle', 'fa5s.plug', 'fa5s.plus',
            'fa5s.plus-circle', 'fa5s.plus-square', 'fa5s.podcast', 'fa5s.poo', 'fa5s.pound-sign', 'fa5s.power-off',
            'fa5s.prescription-bottle', 'fa5s.prescription-bottle-alt', 'fa5s.print', 'fa5s.procedures',
            'fa5s.puzzle-piece', 'fa5s.qrcode', 'fa5s.question', 'fa5s.question-circle', 'fa5s.quidditch',
            'fa5s.quote-left', 'fa5s.quote-right', 'fa5s.random', 'fa5s.recycle', 'fa5s.redo', 'fa5s.redo-alt',
            'fa5s.registered', 'fa5s.reply', 'fa5s.reply-all', 'fa5s.retweet', 'fa5s.ribbon', 'fa5s.road',
            'fa5s.rocket', 'fa5s.rss', 'fa5s.rss-square', 'fa5s.ruble-sign', 'fa5s.rupee-sign', 'fa5s.save',
            'fa5s.search', 'fa5s.search-minus', 'fa5s.search-plus', 'fa5s.seedling', 'fa5s.server', 'fa5s.share',
            'fa5s.share-alt', 'fa5s.share-alt-square', 'fa5s.share-square', 'fa5s.shekel-sign', 'fa5s.shield-alt',
            'fa5s.ship', 'fa5s.shipping-fast', 'fa5s.shopping-bag', 'fa5s.shopping-basket', 'fa5s.shopping-cart',
            'fa5s.shower', 'fa5s.sign', 'fa5s.sign-in-alt', 'fa5s.sign-language', 'fa5s.sign-out-alt', 'fa5s.signal',
            'fa5s.sitemap', 'fa5s.sliders-h', 'fa5s.smile', 'fa5s.smoking', 'fa5s.snowflake', 'fa5s.sort',
            'fa5s.sort-alpha-down', 'fa5s.sort-alpha-up', 'fa5s.sort-amount-down', 'fa5s.sort-amount-up',
            'fa5s.sort-down', 'fa5s.sort-numeric-down', 'fa5s.sort-numeric-up', 'fa5s.sort-up', 'fa5s.space-shuttle',
            'fa5s.spinner', 'fa5s.square', 'fa5s.square-full', 'fa5s.star', 'fa5s.star-half', 'fa5s.step-backward',
            'fa5s.step-forward', 'fa5s.stethoscope', 'fa5s.sticky-note', 'fa5s.stop', 'fa5s.stop-circle',
            'fa5s.stopwatch', 'fa5s.street-view', 'fa5s.strikethrough', 'fa5s.subscript', 'fa5s.subway',
            'fa5s.suitcase', 'fa5s.sun', 'fa5s.superscript', 'fa5s.sync', 'fa5s.sync-alt', 'fa5s.syringe', 'fa5s.table',
            'fa5s.table-tennis', 'fa5s.tablet', 'fa5s.tablet-alt', 'fa5s.tablets', 'fa5s.tachometer-alt', 'fa5s.tag',
            'fa5s.tags', 'fa5s.tape', 'fa5s.tasks', 'fa5s.taxi', 'fa5s.terminal', 'fa5s.text-height', 'fa5s.text-width',
            'fa5s.th', 'fa5s.th-large', 'fa5s.th-list', 'fa5s.thermometer', 'fa5s.thermometer-empty',
            'fa5s.thermometer-full', 'fa5s.thermometer-half', 'fa5s.thermometer-quarter',
            'fa5s.thermometer-three-quarters', 'fa5s.thumbs-down', 'fa5s.thumbs-up', 'fa5s.thumbtack',
            'fa5s.ticket-alt', 'fa5s.times', 'fa5s.times-circle', 'fa5s.tint', 'fa5s.toggle-off', 'fa5s.toggle-on',
            'fa5s.trademark', 'fa5s.train', 'fa5s.transgender', 'fa5s.transgender-alt', 'fa5s.trash', 'fa5s.trash-alt',
            'fa5s.tree', 'fa5s.trophy', 'fa5s.truck', 'fa5s.truck-loading', 'fa5s.truck-moving', 'fa5s.tty', 'fa5s.tv',
            'fa5s.umbrella', 'fa5s.underline', 'fa5s.undo', 'fa5s.undo-alt', 'fa5s.universal-access', 'fa5s.university',
            'fa5s.unlink', 'fa5s.unlock', 'fa5s.unlock-alt', 'fa5s.upload', 'fa5s.user', 'fa5s.user-circle',
            'fa5s.user-md', 'fa5s.user-plus', 'fa5s.user-secret', 'fa5s.user-times', 'fa5s.users', 'fa5s.utensil-spoon',
            'fa5s.utensils', 'fa5s.venus', 'fa5s.venus-double', 'fa5s.venus-mars', 'fa5s.vial', 'fa5s.vials',
            'fa5s.video', 'fa5s.video-slash', 'fa5s.volleyball-ball', 'fa5s.volume-down', 'fa5s.volume-off',
            'fa5s.volume-up', 'fa5s.warehouse', 'fa5s.weight', 'fa5s.wheelchair', 'fa5s.wifi', 'fa5s.window-close',
            'fa5s.window-maximize', 'fa5s.window-minimize', 'fa5s.window-restore', 'fa5s.wine-glass', 'fa5s.won-sign',
            'fa5s.wrench', 'fa5s.x-ray', 'fa5s.yen-sign']
