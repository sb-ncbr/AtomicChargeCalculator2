import os
import shutil
import subprocess

import magic
from werkzeug.utils import secure_filename

from . import config

ALLOWED_INPUT_EXTENSION = [
    '.sdf',
    '.mol2',
    '.pdb', '.ent',
    '.cif'
]


def check_extension(filename: str):
    extension = os.path.splitext(filename)[1].lower()
    if extension not in ALLOWED_INPUT_EXTENSION:
        raise ValueError


def extract(tmp_dir: str, filename: str, fmt: str):
    shutil.unpack_archive(os.path.join(tmp_dir, filename),
                          os.path.join(tmp_dir, 'input'), format=fmt)
    for filename in os.listdir(os.path.join(tmp_dir, 'input')):
        check_extension(filename)


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


# alternative to dos2unix
def dos2unix(data):
    return "\n".join(data.split("\r\n"))


def prepare_example(rq, tmp_dir):
    example_filenames = {
        'example-receptor': 'receptor.pdb',
        'example-phenols': 'phenols.sdf',
        'example-bax-inactive': '1f16_updated.cif',
        'example-bax-activated': '2k7w_updated.cif'
    }

    filename = example_filenames.get(rq.form['example-name'])
    if filename is None:
        raise RuntimeError('Unknown example selected')

    shutil.copy(os.path.join(config.EXAMPLES_DIR, filename),
                os.path.join(tmp_dir, 'input', filename))
