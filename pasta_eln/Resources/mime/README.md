# File type database

The fallback extractor (`pasta_eln/backend_worker/extractor_fallback.py`) identifies file types with
this database: `aliases`, `globs2`, `magic` and `subclasses` are compiled from the shared-mime-info
database `freedesktop.org.xml`, version 2.4 (https://freedesktop.org/wiki/Software/shared-mime-info);
`comments` lists each type's English name from the same file.

## Licence

Copyright (C) 2002, 2003 Thomas Leonard and contributors.

These files are derived from free software; you can redistribute them and/or modify them under the terms
of the GNU General Public License as published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version. See https://www.gnu.org/licenses/old-licenses/gpl-2.0.html.

The rest of PASTA-ELN is MIT-licensed.

## Update

On Linux, with `freedesktop.org.xml` of the new version (e.g. `/usr/share/mime/packages/` of the package
`shared-mime-info`):

```bash
mkdir -p /tmp/mime/packages && cp freedesktop.org.xml /tmp/mime/packages/
update-mime-database /tmp/mime
cp /tmp/mime/{aliases,globs2,magic,subclasses} pasta_eln/Resources/mime/
python - /tmp/mime/packages/freedesktop.org.xml pasta_eln/Resources/mime/comments <<'EOF'
import sys, xml.etree.ElementTree as ET
ns = '{http://www.freedesktop.org/standards/shared-mime-info}'
lang = '{http://www.w3.org/XML/1998/namespace}lang'
with open(sys.argv[2], 'w', encoding='utf-8', newline='\n') as out:
  for mtype in ET.parse(sys.argv[1]).getroot().iter(f'{ns}mime-type'):
    comment = next((c.text for c in mtype.iter(f'{ns}comment') if lang not in c.attrib), None)
    if comment:
      out.write(f"{mtype.get('type')}\t{comment}\n")
EOF
```

Then update the version above.
