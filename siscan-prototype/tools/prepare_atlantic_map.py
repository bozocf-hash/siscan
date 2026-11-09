"""Prepare a local copy of the original ATLANTICADOR editor, with SISCAN adapter."""
from pathlib import Path
import zipfile,sys,hashlib,json
def prepare(source,destination):
 destination=Path(destination);source=Path(source)
 with zipfile.ZipFile(source) as archive:
  for name in archive.namelist():
   prefix='atlanticador-main/frontend/'
   if name.startswith(prefix) and not name.endswith('/'):
    target=(destination/name[len(prefix):]).resolve()
    if not target.is_relative_to(destination.resolve()):raise ValueError('Invalid archive path')
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(archive.read(name))
 app=destination/'src/app.mjs'
 # Editor examples are not SISCAN adjudicated units and must not appear as forces.
 (destination/'src/demo.mjs').write_text('export const DEMO_FEATURES=[];\n',encoding='utf-8')
 app.write_text(app.read_text(encoding='utf-8')+"\nawait (await import('/atlantic-bridge.mjs')).install(map);\n",encoding='utf-8')
 (destination/'siscan-origin.json').write_text(json.dumps({'source_sha256':hashlib.file_digest(source.open('rb'),'sha256').hexdigest(),'adaptation':'original editor + SISCAN planning overlay; original archive preserved'}),encoding='utf-8')
if __name__=='__main__':prepare(sys.argv[1],sys.argv[2])
