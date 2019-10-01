from flask import render_template, flash, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from . import application, config

import tempfile
import magic
import uuid
import shutil
import os
import zipfile
import subprocess
from glob import glob

from .method import method_data, parameter_data, publication_data
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


def prepare_file(rq, tmp_dir):
    file = rq.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(tmp_dir, filename))

    filetype = magic.from_file(os.path.join(tmp_dir, filename), mime=True)
    success = True
    try:
        if filetype in ['text/plain', 'chemical/x-pdb']:
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


def prepare_example(rq, tmp_dir):
    if 'example-small' in rq.form:
        filename = 'set01.sdf'
    elif 'example-ligand' in rq.form:
        filename = 'cis-homoaconitate.sdf'
    elif 'example-bax-inactive' in rq.form:
        filename = '1f16_updated.cif'
    elif 'example-bax-activated' in rq.form:
        filename = '2k7w_updated.cif'
    else:
        raise RuntimeError('Unknown example selected')
    shutil.copy(os.path.join(config.EXAMPLES_DIR, filename), os.path.join(tmp_dir, 'input', filename))


def calculate_charges_default(methods, parameters, tmp_dir, comp_id):
    method_name = next(method['internal_name'] for method in method_data if method['internal_name'] in methods)

    if method_name in parameters:
        parameters_name = parameters[method_name][0]
    else:
        # This value should not be used as we later check whether the method needs parameters
        parameters_name = None

    charges, structures = calculate_charges(method_name, parameters_name, tmp_dir)
    request_data[comp_id].update(
        {'method': method_name, 'parameters': parameters_name, 'structures': structures, 'charges': charges})

    return redirect(url_for('results', r=comp_id))


@application.route('/', methods=['GET', 'POST'])
def main_site():
    if request.method == 'POST':
        tmp_dir = tempfile.mkdtemp(prefix='compute_')
        os.mkdir(os.path.join(tmp_dir, 'input'))
        os.mkdir(os.path.join(tmp_dir, 'output'))
        os.mkdir(os.path.join(tmp_dir, 'logs'))

        if request.form['type'] in ['settings', 'charges']:
            if not prepare_file(request, tmp_dir):
                flash('Invalid file provided. Supported types are common chemical formats: sdf, mol2, pdb, cif'
                      ' and zip or tar.gz of those.', 'error')
                return render_template('index.html')
        elif request.form['type'] == 'example':
            prepare_example(request, tmp_dir)
        else:
            raise RuntimeError('Bad type of input')

        comp_id = str(uuid.uuid1())
        try:
            methods, parameters = get_suitable_methods(tmp_dir)
        except RuntimeError as e:
            flash(f'Error: {e}', 'error')
            return render_template('index.html')

        request_data[comp_id] = {'tmpdir': tmp_dir, 'suitable_methods': methods, 'suitable_parameters': parameters}

        if request.form['type'] == 'charges':
            return calculate_charges_default(methods, parameters, tmp_dir, comp_id)
        else:
            return redirect(url_for('computation', r=comp_id))
    else:
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

        charges, structures = calculate_charges(method_name, parameters_name, tmp_dir)

        request_data[comp_id].update(
            {'method': method_name, 'parameters': parameters_name, 'structures': structures, 'charges': charges})

        return redirect(url_for('results', r=comp_id))

    return render_template('computation.html', methods=method_data, parameters=parameter_data,
                           publications=publication_data, suitable_methods=suitable_methods,
                           suitable_parameters=suitable_parameters)


def calculate_charges(method_name, parameters_name, tmp_dir):
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
                d = parse_sdf(f)
                # Convert to Mol V2000 if possible as LiteMol can't handle Mol V3000
                for name, struct in d.items():
                    version = struct.splitlines()[3][34:39]
                    if version == 'V2000':
                        # We are OK here
                        structures[name] = struct
                        continue
                    args = ['obabel', '-isdf', '-osdf']
                    run = subprocess.run(args, input=struct.encode('utf-8'), stdout=subprocess.PIPE)
                    structures[name] = run.stdout.decode('utf-8')
            elif ext == '.mol2':
                # Convert to Mol V2000 as LiteMol can't handle Mol V3000
                d = parse_mol2(f)
                for name, struct in d.items():
                    args = ['obabel', '-imol2', '-osdf']
                    run = subprocess.run(args, input=struct.encode('utf-8'), stdout=subprocess.PIPE)
                    structures[name] = run.stdout.decode('utf-8')
            elif ext == '.pdb' or ext == '.ent':
                structures.update(parse_pdb(f))
            elif ext == '.cif':
                structures.update(parse_cif(f))
            else:
                raise RuntimeError(f'Not supported format: {ext}')

        with open(os.path.join(tmp_dir, 'output', f'{file}.txt')) as f:
            charges.update(parse_txt(f))
    return charges, structures


@application.route('/results')
def results():
    comp_id = request.args.get('r')
    comp_data = request_data[comp_id]
    tmpdir = comp_data['tmpdir']
    filename = glob(os.path.join(tmpdir, 'logs', '*.stdout'))[0]
    parameters_name = 'None'
    with open(filename) as f:
        for line in f:
            if line.startswith('Parameters:'):
                _, parameters_name = line.split(' ', 1)
                break

    method_name = next(m for m in method_data if m['internal_name'] == comp_data['method'])['name']

    chg_range = {}
    for struct, charges in comp_data['charges'].items():
        chg_range[struct] = max(abs(float(chg)) for chg in charges.split()[1:])

    return render_template('results.html', method_name=method_name, comp_id=comp_id, parameters_name=parameters_name,
                           structures=comp_data['structures'].keys(), chg_range=chg_range)


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
