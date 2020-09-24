import os
import subprocess
import magic
import shutil
from typing import Dict, IO
from werkzeug.utils import secure_filename


from .parser import parse_cif_from_string

ALLOWED_INPUT_EXTENSION = {'.sdf', '.mol2', '.pdb', '.cif'}


def check_extension(filename: str):
    basename, ext = os.path.splitext(filename)
    if ext.lower() not in ALLOWED_INPUT_EXTENSION:
        raise ValueError


def extract(tmp_dir: str, filename: str, fmt: str):
    shutil.unpack_archive(os.path.join(tmp_dir, filename), os.path.join(tmp_dir, 'input'), format=fmt)
    for filename in os.listdir(os.path.join(tmp_dir, 'input')):
        check_extension(filename)


def convert_to_mmcif(f: IO[str], fmt: str, filename: str) -> Dict[str, str]:
    input_arg = f'-i{fmt}'
    args = ['obabel', input_arg, '-ommcif']
    data = f.read()
    run = subprocess.run(args, input=data.encode('utf-8'), stdout=subprocess.PIPE)
    output = run.stdout.decode('utf-8')
    structures: Dict[str, str] = {}
    delimiter = '# --------------------------------------------------------------------------'
    for s in (s for s in output.split(delimiter) if s):
        structures.update(parse_cif_from_string(s, filename))

    return structures


def prepare_file(rq, tmp_dir):
    file = rq.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(tmp_dir, filename))

    filetype = magic.from_file(os.path.join(tmp_dir, filename), mime=True)
    success = True
    try:
        if filetype in ['text/plain', 'chemical/x-pdb']:
            check_extension(filename)
            shutil.copy(os.path.join(tmp_dir, filename), os.path.join(tmp_dir, 'input'))
        elif filetype == 'application/zip':
            extract(tmp_dir, filename, 'zip')
        elif filetype == 'application/x-gzip':
            extract(tmp_dir, filename, 'gztar')
        else:
            success = False
    except ValueError:
        success = False

    # Handle files from Windows
    for file in os.listdir(os.path.join(tmp_dir, 'input')):
        args = ['dos2unix', os.path.join(tmp_dir, 'input', file)]
        subprocess.run(args)

    return success
