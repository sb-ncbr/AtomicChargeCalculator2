from flask import render_template, flash, redirect, request, send_from_directory
from app import application

import tempfile

from app.method import method_data, parameter_data
from app.calculation import calculate


@application.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('no selected file')
            return redirect(request.url)
        if file:
            tmp_dir = tempfile.mkdtemp(prefix='compute_')
            file.save(f'{tmp_dir}/structure.sdf')
            method_name = request.form.get('method_select')
            parameters_name = request.form.get('parameters_select')
            res = calculate(method_name, parameters_name, f'{tmp_dir}/structure.sdf', f'{tmp_dir}/charges')
            if res.returncode:
                flash('Computation failed: ' + res.stderr.decode('utf-8'), 'error')
            else:
                return send_from_directory(f'{tmp_dir}', 'charges', as_attachment=True,
                                           attachment_filename=f'{method_name}_charges.txt')

    return render_template('index.html', methods=method_data, parameters=parameter_data)
