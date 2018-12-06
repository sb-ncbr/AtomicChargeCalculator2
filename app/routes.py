from flask import render_template, flash, request, send_from_directory, redirect, url_for
from app import application

import tempfile
import magic
import uuid

from app.method import method_data, parameter_data
from app.calculation import calculate

request_data = {}


@application.route('/', methods=['GET', 'POST'])
def main_site():
    if request.method == 'POST':
        file = request.files['file']
        tmp_dir = tempfile.mkdtemp(prefix='compute_')
        file.save(f'{tmp_dir}/structure.sdf')
        filetype = magic.from_file(f'{tmp_dir}/structure.sdf')
        if magic.from_file(f'{tmp_dir}/structure.sdf') != 'ASCII text':
            flash(f'Invalid file type: {filetype}. Use only SDF.', 'error')
        else:
            comp_id = str(uuid.uuid1())
            method_name = request.form.get('method_select')
            parameters_name = request.form.get('parameters_select')
            res = calculate(method_name, parameters_name, f'{tmp_dir}/structure.sdf', f'{tmp_dir}/charges')
            if res.returncode:
                flash('Computation failed: ' + res.stderr.decode('utf-8'), 'error')
            else:
                output = res.stdout.decode('utf-8')
                request_data[comp_id] = {'tmpdir': tmp_dir, 'method_name': method_name, 'output': output}
                return redirect(url_for('results', r=comp_id))

    return render_template('index.html', methods=method_data, parameters=parameter_data)


@application.route('/results')
def results():
    comp_id = request.args.get('r')
    comp_data = request_data[comp_id]
    return render_template('calculation.html', method_name=comp_data["method_name"], comp_id=comp_id,
                           output=comp_data['output'])


@application.route('/download')
def download_charges():
    comp_id = request.args.get('r')
    comp_data = request_data[comp_id]
    return send_from_directory(f'{comp_data["tmpdir"]}', 'charges', as_attachment=True,
                               attachment_filename=f'{comp_data["method_name"]}_charges.txt')
