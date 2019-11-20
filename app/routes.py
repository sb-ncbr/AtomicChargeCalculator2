from flask import render_template, flash, request, send_from_directory, redirect, url_for, Response, abort
from werkzeug.utils import secure_filename
from . import application, config
from typing import Dict, IO

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


def update_computation_results(method_name: str, parameters_name: str, tmp_dir: str, comp_id: str):
    charges, structures, formats, logs = calculate_charges(method_name, parameters_name, tmp_dir)
    request_data[comp_id].update({'method': method_name,
                                  'parameters': parameters_name,
                                  'structures': structures,
                                  'formats': formats,
                                  'charges': charges,
                                  'logs': logs})


def calculate_charges_default(methods, parameters, tmp_dir, comp_id):
    method_name = next(method['internal_name'] for method in method_data if method['internal_name'] in methods)

    if method_name in parameters:
        parameters_name = parameters[method_name][0]
    else:
        # This value should not be used as we later check whether the method needs parameters
        parameters_name = None

    update_computation_results(method_name, parameters_name, tmp_dir, comp_id)

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
    try:
        tmp_dir = request_data[comp_id]['tmpdir']
    except KeyError:
        abort(404)

    suitable_methods = request_data[comp_id]['suitable_methods']
    suitable_parameters = request_data[comp_id]['suitable_parameters']

    if request.method == 'POST':
        method_name = request.form.get('method_select')
        parameters_name = request.form.get('parameters_select')

        update_computation_results(method_name, parameters_name, tmp_dir, comp_id)

        return redirect(url_for('results', r=comp_id))

    return render_template('computation.html', methods=method_data, parameters=parameter_data,
                           publications=publication_data, suitable_methods=suitable_methods,
                           suitable_parameters=suitable_parameters)


def calculate_charges(method_name, parameters_name, tmp_dir):
    structures: Dict[str, str] = {}
    charges: Dict[str, str] = {}
    formats: Dict[str, str] = {}
    logs: Dict[str, str] = {}

    for file in os.listdir(os.path.join(tmp_dir, 'input')):
        res = calculate(method_name, parameters_name, os.path.join(tmp_dir, 'input', file),
                        os.path.join(tmp_dir, 'output'))

        stderr = res.stderr.decode('utf-8')

        with open(os.path.join(tmp_dir, 'logs', f'{file}.stdout'), 'w') as f_stdout:
            f_stdout.write(res.stdout.decode('utf-8'))

        with open(os.path.join(tmp_dir, 'logs', f'{file}.stderr'), 'w') as f_stderr:
            f_stderr.write(stderr)

        if stderr.strip():
            logs['stderr'] = stderr

        if res.returncode:
            flash('Computation failed. See logs for details.', 'error')

        _, ext = os.path.splitext(file)
        ext = ext.lower()

        tmp_structures: Dict[str, str] = {}
        with open(os.path.join(tmp_dir, 'input', file)) as f:
            if ext == '.sdf':
                if get_MOL_versions(os.path.join(tmp_dir, 'input', file)) == {'V2000'}:
                    tmp_structures.update(parse_sdf(f))
                    fmt = 'SDF'
                else:
                    tmp_structures.update(convert_to_mmcif(f, 'sdf', file))
                    fmt = 'mmCIF'
            elif ext == '.mol2':
                tmp_structures.update(convert_to_mmcif(f, 'mol2', file))
                fmt = 'mmCIF'
            elif ext == '.pdb':
                tmp_structures.update(parse_pdb(f))
                fmt = 'PDB'
            elif ext == '.cif':
                tmp_structures.update(parse_cif(f))
                fmt = 'mmCIF'
            else:
                raise RuntimeError(f'Not supported format: {ext}')

        for s in tmp_structures:
            formats[s] = fmt

        structures.update(tmp_structures)

        with open(os.path.join(tmp_dir, 'output', f'{file}.txt')) as f:
            charges.update(parse_txt(f))
    return charges, structures, formats, logs


@application.route('/results')
def results():
    comp_id = request.args.get('r')
    try:
        comp_data = request_data[comp_id]
    except KeyError:
        abort(404)

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

    logs = ''
    if 'stderr' in comp_data['logs']:
        logs = comp_data['logs']['stderr']
        flash('Some errors occured during the computation, see log for details.')

    return render_template('results.html', method_name=method_name, comp_id=comp_id, parameters_name=parameters_name,
                           structures=comp_data['structures'].keys(), chg_range=chg_range, logs=logs)


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

    return Response(comp_data['structures'][structure_id], mimetype='text/plain')


@application.route('/format')
def get_format():
    comp_id = request.args.get('r')
    structure_id = request.args.get('s')
    comp_data = request_data[comp_id]
    return Response(comp_data['formats'][structure_id], mimetype='text/plain')


@application.route('/charges')
def get_charges():
    comp_id = request.args.get('r')
    structure_id = request.args.get('s')
    comp_data = request_data[comp_id]
    try:
        return Response(comp_data['charges'][structure_id], mimetype='text/plain')
    except KeyError:
        print(f'Requested charges were not found for {structure_id}')
        return Response('---No charges---', mimetype='text/plain')


@application.route('/logs')
def get_logs():
    comp_id = request.args.get('r')
    comp_data = request_data[comp_id]

    return Response(comp_data['logs']['stderr'], mimetype='text/plain')


@application.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
