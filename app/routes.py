from flask import render_template, flash, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from . import application, config

import tempfile
import magic
import uuid
import shutil
import os
import zipfile

from .method import method_data, parameter_data
from .chargefw2 import calculate, get_suitable_methods
from .parser import *

request_data = {}

ALLOWED_INPUT_EXTENSION = {'.sdf', '.mol2', '.pdb', '.cif'}


def extract(tmp_dir: str, filename: str, fmt: str):
    shutil.unpack_archive(os.path.join(tmp_dir, filename), os.path.join(tmp_dir, 'input'), format=fmt)
    for filename in os.listdir(os.path.join(tmp_dir, 'input')):
        basename, ext = os.path.splitext(filename)
        if ext not in ALLOWED_INPUT_EXTENSION:
            raise ValueError


@application.route('/', methods=['GET', 'POST'])
def main_site():
    if request.method == 'POST':
        tmp_dir = tempfile.mkdtemp(prefix='compute_')
        os.mkdir(os.path.join(tmp_dir, 'input'))
        os.mkdir(os.path.join(tmp_dir, 'output'))
        os.mkdir(os.path.join(tmp_dir, 'logs'))

        if request.form['type'] == 'upload':
            file = request.files['file']
            filename = secure_filename(file.filename)
            file.save(os.path.join(tmp_dir, filename))

            filetype = magic.from_file(os.path.join(tmp_dir, filename), mime=True)
            failed = False
            try:
                if filetype == 'text/plain':
                    shutil.copy(os.path.join(tmp_dir, filename), os.path.join(tmp_dir, 'input'))
                elif filetype == 'application/zip':
                    extract(tmp_dir, filename, 'zip')
                elif filetype == 'application/x-gzip':
                    extract(tmp_dir, filename, 'gztar')
                else:
                    failed = True
            except ValueError:
                failed = True

            if failed:
                flash('Invalid file provided. Supported types are common chemical formats: sdf, mol2, pdb, cif'
                      ' and zip or tar.gz of those.',
                      'error')
                return render_template('index.html')
        elif request.form['type'] == 'example':
            if 'example-small' in request.form:
                filename = 'set01.sdf'
            elif 'example-ligand' in request.form:
                filename = 'TRP.cif'
            elif 'example-protein' in request.form:
                filename = '3k0h_updated.cif'
            else:
                raise RuntimeError('Unknown example selected')
            shutil.copy(os.path.join(config.EXAMPLES_DIR, filename), os.path.join(tmp_dir, 'input', filename))
        else:
            raise RuntimeError('Bad type of input')

        comp_id = str(uuid.uuid1())

        methods, parameters = get_suitable_methods(tmp_dir)
        data = {'tmpdir': tmp_dir, 'suitable_methods': methods, 'suitable_parameters': parameters}

        request_data[comp_id] = data

        return redirect(url_for('computation', r=comp_id))

    return render_template('index.html')


@application.route('/computation', methods=['GET', 'POST'])
def computation():
    comp_id = request.args.get('r')
    tmp_dir = request_data[comp_id]['tmpdir']
    suitable_methods = request_data[comp_id]['suitable_methods']
    suitable_parameters = request_data[comp_id]['suitable_parameters']

    if request.method == 'POST':
        method_name = request.form.get('method_select')
        parameters_name = request.form.get('parameters_select')

        structures = {}
        charges = {}
        for file in os.listdir(os.path.join(tmp_dir, 'input')):
            res = calculate(method_name, parameters_name, os.path.join(tmp_dir, 'input', file),
                            os.path.join(tmp_dir, 'output'))

            with open(os.path.join(tmp_dir, 'logs', f'{file}.stdout'), 'w') as f_stdout:
                f_stdout.write(res.stdout.decode('utf-8'))

            with open(os.path.join(tmp_dir, 'logs', f'{file}.stderr'), 'w') as f_stderr:
                f_stderr.write(res.stderr.decode('utf-8'))

            if res.returncode:
                flash('Computation failed: ' + res.stderr.decode('utf-8'), 'error')

            _, ext = os.path.splitext(file)

            with open(os.path.join(tmp_dir, 'input', file)) as f:
                if ext == '.sdf':
                    structures.update(parse_sdf(f))
                elif ext == '.mol2':
                    structures.update(parse_mol2(f))
                elif ext == '.pdb' or ext == '.ent':
                    structures.update(parse_pdb(f))
                elif ext == '.cif':
                    structures.update(parse_cif(f))
                else:
                    raise RuntimeError(f'Not supported format: {ext}')

            with open(os.path.join(tmp_dir, 'output', f'{file}.txt')) as f:
                charges.update(parse_txt(f))

        request_data[comp_id] = {'tmpdir': tmp_dir, 'method': method_name, 'parameters': parameters_name,
                                 'structures': structures, 'charges': charges}

        return redirect(url_for('results', r=comp_id))

    return render_template('computation.html', methods=method_data, parameters=parameter_data,
                           suitable_methods=suitable_methods, suitable_parameters=suitable_parameters)


@application.route('/results')
def results():
    comp_id = request.args.get('r')
    comp_data = request_data[comp_id]

    return render_template('results.html', method_name=comp_data['method'], comp_id=comp_id, methods=method_data,
                           parameters_name=comp_data['parameters'], structures=comp_data['structures'].keys())


@application.route('/download')
def download_charges():
    comp_id = request.args.get('r')
    comp_data = request_data[comp_id]
    tmpdir = comp_data['tmpdir']
    method = comp_data['method']

    with zipfile.ZipFile(os.path.join(tmpdir, 'charges.zip'), 'w', compression=zipfile.ZIP_DEFLATED) as f:
        for file in os.listdir(os.path.join(tmpdir, 'output')):
            f.write(os.path.join(tmpdir, 'output', file), arcname=file)

    return send_from_directory(tmpdir, 'charges.zip', as_attachment=True, attachment_filename=f'{method}_charges.zip')


@application.route('/structure')
def get_structure():
    comp_id = request.args.get('r')
    structure_id = request.args.get('s')
    comp_data = request_data[comp_id]

    return comp_data['structures'][structure_id]


@application.route('/charges')
def get_charges():
    comp_id = request.args.get('r')
    structure_id = request.args.get('s')
    comp_data = request_data[comp_id]

    return comp_data['charges'][structure_id]
