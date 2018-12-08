from flask import render_template, flash, request, send_from_directory, redirect, url_for
from app import application

import tempfile
import magic
import uuid
import shutil
import os
import re

from app.method import method_data, parameter_data
from app.calculation import calculate

request_data = {}


def extract(tmp_dir, fmt):
    shutil.unpack_archive(os.path.join(tmp_dir, 'input'), os.path.join(tmp_dir, 'tmp'), format=fmt)
    with open(os.path.join(tmp_dir, 'structures.sdf'), 'w') as output:
        for filename in os.listdir(os.path.join(tmp_dir, 'tmp')):
            with open(os.path.join(tmp_dir, 'tmp', filename)) as f:
                shutil.copyfileobj(f, output)


@application.route('/', methods=['GET', 'POST'])
def main_site():
    if request.method == 'POST':
        file = request.files['file']
        tmp_dir = tempfile.mkdtemp(prefix='compute_')
        file.save(os.path.join(tmp_dir, 'input'))
        filetype = magic.from_file(os.path.join(tmp_dir, 'input'), mime=True)
        failed = False
        try:
            if filetype == 'text/plain':
                shutil.copyfile(os.path.join(tmp_dir, 'input'), os.path.join(tmp_dir, 'structures.sdf'))
            elif filetype == 'application/zip':
                extract(tmp_dir, 'zip')
            elif filetype == 'application/x-gzip':
                extract(tmp_dir, 'gztar')
            else:
                failed = True
        except ValueError:
            failed = True

        if failed:
            flash(f'Invalid file type: {filetype}. Use only sdf, zip or tar.gz only.', 'error')
            return render_template('index.html', methods=method_data, parameters=parameter_data)

        comp_id = str(uuid.uuid1())
        method_name = request.form.get('method_select')
        parameters_name = request.form.get('parameters_select')
        res = calculate(method_name, parameters_name, os.path.join(tmp_dir, 'structures.sdf'),
                        os.path.join(tmp_dir, 'charges'))
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
    m = re.search('Number of molecules: (.*?)\n', comp_data['output'])
    n_molecules = m.group(1)
    m = re.search('Computation took (.*?) seconds\n', comp_data['output'])
    time = m.group(1)

    info = False
    c = {}
    for line in comp_data['output'].split('\n'):
        if 'Number of molecules' in line:
            info = True
        elif line == '':
            break
        elif info:
            m = re.search('(.*?) plain \*: (\d+)', line)
            element = m.group(1)
            element_count = int(m.group(2))
            c[element] = element_count

    return render_template('calculation.html', method_name=comp_data['method'], comp_id=comp_id,
                           n_molecules=n_molecules, time=time, counts=c, methods=method_data, parameters=parameter_data,
                           parameters_name=comp_data['parameters'])


@application.route('/download')
def download_charges():
    comp_id = request.args.get('r')
    comp_data = request_data[comp_id]
    return send_from_directory(f'{comp_data["tmpdir"]}', 'charges', as_attachment=True,
                               attachment_filename=f'{comp_data["method_name"]}_charges.txt')
