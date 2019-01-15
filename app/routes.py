from flask import render_template, flash, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from app import application

import tempfile
import magic
import uuid
import shutil
import os
import re
import zipfile
import subprocess

from app.method import method_data, parameter_data
from app.calculation import calculate
from app.export_charges import prepare_mol2

request_data = {}


def convert_to_sdf(filename: str):
    basename, ext = os.path.splitext(filename)
    if ext == 'sdf':
        return
    args = ['obabel', filename, '-osdf', '-O', f'{basename}.sdf']
    run = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(' '.join(run.args))
    if 'Open Babel Error' in run.stderr.decode('utf-8'):
        raise ValueError


def extract(tmp_dir: str, filename: str, fmt: str):
    shutil.unpack_archive(os.path.join(tmp_dir, filename), os.path.join(tmp_dir, 'tmp'), format=fmt)
    with open(os.path.join(tmp_dir, 'structures.sdf'), 'w') as output:
        for filename in os.listdir(os.path.join(tmp_dir, 'tmp')):
            basename, ext = os.path.splitext(filename)
            convert_to_sdf(os.path.join(tmp_dir, 'tmp', filename))
            with open(os.path.join(tmp_dir, 'tmp', f'{basename}.sdf')) as f:
                shutil.copyfileobj(f, output)


@application.route('/', methods=['GET', 'POST'])
def main_site():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        tmp_dir = tempfile.mkdtemp(prefix='compute_')
        file.save(os.path.join(tmp_dir, filename))
        filetype = magic.from_file(os.path.join(tmp_dir, filename), mime=True)
        failed = False
        try:
            if filetype.startswith('text'):
                basename, ext = os.path.splitext(filename)
                convert_to_sdf(os.path.join(tmp_dir, filename))
                shutil.copyfile(os.path.join(tmp_dir, f'{basename}.sdf'), os.path.join(tmp_dir, 'structures.sdf'))
            elif filetype == 'application/zip':
                extract(tmp_dir, filename, 'zip')
            elif filetype == 'application/x-gzip':
                extract(tmp_dir, filename, 'gztar')
            else:
                failed = True
        except ValueError:
            failed = True

        if failed:
            flash('Invalid file provided. Supported types are common chemical formats like sdf, mol2, pdb'
                  ' and zip or tar.gz of those.',
                  'error')
            return render_template('index.html', methods=method_data, parameters=parameter_data)

        comp_id = str(uuid.uuid1())
        method_name = request.form.get('method_select')
        parameters_name = request.form.get('parameters_select')
        method_info = next((m for m in method_data if m['name'] == method_name))
        options = {}
        if 'options' in method_info:
            for option in method_info['options']:
                options[option['name']] = request.form.get(f'{method_name}-option-{option["name"]}')

        res = calculate(method_name, parameters_name, options, os.path.join(tmp_dir, 'structures.sdf'),
                        os.path.join(tmp_dir, 'charges'))

        with open(os.path.join(tmp_dir, 'computation.stdout'), 'w') as f:
            f.write(res.stdout.decode('utf-8'))

        with open(os.path.join(tmp_dir, 'computation.stderr'), 'w') as f:
                f.write(res.stderr.decode('utf-8'))

        if res.returncode:
            flash('Computation failed: ' + res.stderr.decode('utf-8'), 'error')
        else:
            output = res.stdout.decode('utf-8')
            request_data[comp_id] = {'tmpdir': tmp_dir, 'method': method_name, 'output': output,
                                     'parameters': parameters_name}
            return redirect(url_for('results', r=comp_id))

    return render_template('index.html', methods=method_data, parameters=parameter_data)


@application.route('/results')
def results():
    comp_id = request.args.get('r')
    comp_data = request_data[comp_id]
    m = re.search(r'Number of molecules: (.*?)\n', comp_data['output'])
    n_molecules = m.group(1)
    m = re.search(r'Computation took (.*?) seconds\n', comp_data['output'])
    time = m.group(1)

    info = False
    c = {}
    for line in comp_data['output'].split('\n'):
        if 'Number of molecules' in line:
            info = True
        elif line == '':
            break
        elif info:
            m = re.search(r'(.*?) plain \*: (\d+)', line)
            element = m.group(1)
            element_count = int(m.group(2))
            c[element] = element_count

    return render_template('calculation.html', method_name=comp_data['method'], comp_id=comp_id,
                           n_molecules=n_molecules, time=time, counts=c, methods=method_data, parameters=parameter_data,
                           parameters_name=comp_data['parameters'])


@application.route('/download')
def download_charges():
    comp_id = request.args.get('r')
    charges_format = request.args.getlist('format')
    comp_data = request_data[comp_id]
    tmpdir = comp_data['tmpdir']
    method = comp_data['method']
    parameters = comp_data['parameters']

    with zipfile.ZipFile(os.path.join(tmpdir, 'charges.zip'), 'w', compression=zipfile.ZIP_DEFLATED) as f:
        if 'plain' in charges_format:
            f.write(os.path.join(tmpdir, 'charges'), arcname='charges.txt')
        if 'mol2' in charges_format:
            prepare_mol2(tmpdir, method, parameters)
            f.write(os.path.join(tmpdir, 'charges.mol2'), arcname='charges.mol2')

    return send_from_directory(tmpdir, 'charges.zip', as_attachment=True, attachment_filename=f'{method}_charges.zip')
