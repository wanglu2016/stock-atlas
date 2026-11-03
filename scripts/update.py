#!/usr/bin/env python3
"""Update the two flat public data files; restore their old bytes on failure."""
import pathlib,subprocess,sys,tempfile,shutil
root=pathlib.Path(__file__).resolve().parents[1]
names=['snapshot.json','history.json']
with tempfile.TemporaryDirectory(prefix='stock-atlas-backup-') as tmp:
 backup=pathlib.Path(tmp)
 for name in names:
  if (root/name).exists():shutil.copy2(root/name,backup/name)
 try:
  for command in [[sys.executable,'scripts/collect.py'],[sys.executable,'scripts/enrich.py'],['node','scripts/check.mjs']]:subprocess.run(command,cwd=root,check=True)
 except BaseException:
  for name in names:
   if (backup/name).exists():shutil.copy2(backup/name,root/name)
  raise
print('Data updated locally. Commit the two JSON files to publish a new snapshot.')
