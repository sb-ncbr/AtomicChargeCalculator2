import os
import shutil
import tempfile
import uuid
from collections import defaultdict
from typing import Dict, List, Tuple

from flask import (Response, abort, flash, redirect, render_template, request,
                   send_file, url_for)
from gemmi import cif

from . import application
from .chargefw2 import calculate, get_suitable_methods
from .files import prepare_example, prepare_file
from .method import method_data, parameter_data
from .parser import parse_txt, sanitize_name

request_data = {}


def get_method_name(method_name: str) -> str:
    method_name = next(
        method["name"]
        for method in method_data
        if method["internal_name"] == method_name
    )
    return method_name


def get_parameters_name(method_name: str, parameters_filename: str) -> str:
    # return 'None' if method does not support parameters
    parameters_name = next((
        parameters["name"]
        for parameters in parameter_data[method_name]
        if parameters["filename"] == parameters_filename
    ), 'None')
    return parameters_name


def prepare_calculations(calculation_list: List[str]) -> Dict[str, List[str]]:
    calculations: Dict[str, List[str]] = defaultdict(list)

    for calculation in calculation_list:
        method, parameters = calculation.split(" ")
        calculations[method] += [parameters]

    return calculations


def calculate_charges_default(methods, parameters, tmp_dir: str, comp_id: str) -> None:
    # use first method from suitable methods
    method_name = next(
        method["internal_name"]
        for method in method_data
        if method["internal_name"] in methods
    )

    if method_name in parameters:
        parameters_name = parameters[method_name][0]
    else:
        # This value should not be used as we later check whether the method needs parameters
        parameters_name = None

    calculation = {method_name: [parameters_name]}
    calculate_charges(calculation, tmp_dir, comp_id)


def write_all_charges_to_mmcif_output(charges: Dict[str, Dict[Tuple[str, str], List[float]]], output_dir: str, output_filename: str) -> None:
    output_file_path = os.path.join(output_dir, f"{output_filename}.fw2.cif")
    document = cif.read_file(output_file_path)
    block = document.sole_block()

    sb_ncbr_partial_atomic_charges_meta_prefix = "_sb_ncbr_partial_atomic_charges_meta."
    sb_ncbr_partial_atomic_charges_prefix = "_sb_ncbr_partial_atomic_charges."
    sb_ncbr_partial_atomic_charges_meta_attributes = ["id", "type", "method"]
    sb_ncbr_partial_atomic_charges_attributes = [
        "type_id", "atom_id", "charge"]

    block.find_mmcif_category(
        sb_ncbr_partial_atomic_charges_meta_prefix).erase()
    block.find_mmcif_category(sb_ncbr_partial_atomic_charges_prefix).erase()

    metadata_loop = block.init_loop(
        sb_ncbr_partial_atomic_charges_meta_prefix, sb_ncbr_partial_atomic_charges_meta_attributes)

    for typeId, (method_internal_name, parameters_name) in enumerate(charges[output_filename]):
        method_name = get_method_name(method_internal_name)
        parameters_name = get_parameters_name(
            method_internal_name, parameters_name)
        metadata_loop.add_row([f"{typeId + 1}",
                               "'empirical'",
                               f"'{method_name}/{parameters_name}'"])

    charges_loop = block.init_loop(
        sb_ncbr_partial_atomic_charges_prefix, sb_ncbr_partial_atomic_charges_attributes)

    for typeId, (method_internal_name, parameters_name) in enumerate(charges[output_filename]):
        chgs = charges[output_filename][(
            method_internal_name, parameters_name)]
        for atomId, charge in enumerate(chgs):
            charges_loop.add_row([f"{typeId + 1}",
                                  f"{atomId + 1}",
                                  f"{charge: .4f}"])

    block.write_file(output_file_path)


def calculate_charges(calculations: Dict[str, List[str]], tmp_dir: str, comp_id: str):
    structures: Dict[str, str] = {}
    logs: Dict[str, str] = {}

    input_dir = os.path.join(tmp_dir, "input")
    output_dir = os.path.join(tmp_dir, "output")
    log_dir = os.path.join(tmp_dir, "logs")

    for extension in ["cif", "pqr", "txt", "mol2"]:
        os.makedirs(os.path.join(output_dir, extension), exist_ok=True)

    # calculate charges for each structure in input directory
    for input_filename in os.listdir(input_dir):
        charges: Dict[str, Dict[Tuple[str, str],
                                List[float]]] = defaultdict(dict)
        for method_name in calculations:
            for parameters_name in calculations[method_name]:
                input_file_path = os.path.join(input_dir, input_filename)

                # run chargefw2
                result = calculate(
                    method_name,
                    parameters_name,
                    input_file_path,
                    output_dir,
                )

                # save stdout and stderr to files
                stdout = result.stdout.decode("utf-8")
                stderr = result.stderr.decode("utf-8")
                with open(os.path.join(log_dir, f"{input_filename}.stdout"), "w") as f_stdout:
                    f_stdout.write(stdout)
                with open(os.path.join(log_dir, f"{input_filename}.stderr"), "w") as f_stderr:
                    f_stderr.write(stderr)

                # save logs
                if stderr.strip():
                    logs["stderr"] = stderr
                if result.returncode != 0:
                    flash("Computation failed. See logs for details.", "danger")

                # save charges
                with open(os.path.join(output_dir, f"{input_filename}.txt"), "r") as f:
                    for molecule_name, chgs in parse_txt(f).items():
                        molecule_name = molecule_name.split(":")[1].lower()
                        charges[molecule_name].update(
                            {(method_name, parameters_name): chgs})

                # rename output files to avoid overwriting them
                # and move output files to their respective directories
                for output_filename in os.listdir(output_dir):
                    extension = os.path.splitext(output_filename)[1][1:]
                    structure_name = os.path.splitext(input_filename)[0]
                    method = get_method_name(method_name)
                    parameters = get_parameters_name(
                        method_name, parameters_name)
                    if extension in ["txt", "pqr", "mol2"]:
                        os.rename(os.path.join(output_dir, output_filename),
                                  os.path.join(output_dir, extension, f"{structure_name}-{method}-{parameters}.{extension}"))
                    if extension in ["cif"]:
                        sanitized_output_filename = sanitize_name(output_filename.replace(".fw2.cif", "")).lower()
                        os.rename(os.path.join(output_dir, output_filename),
                                  os.path.join(output_dir, f"{sanitized_output_filename}.fw2.cif"))

        # save the mmCIF output file as a string
        # and move it to the cif directory
        for output_filename in list(charges):
            write_all_charges_to_mmcif_output(
                charges, output_dir, output_filename)
            with open(os.path.join(output_dir, f"{output_filename}.fw2.cif"), "r") as f:
                structures[output_filename.upper()] = f.read()
            os.rename(os.path.join(output_dir, f"{output_filename}.fw2.cif"),
                      os.path.join(output_dir, "cif", f"{output_filename}.fw2.cif"))

    # save results to request_data
    request_data[comp_id].update({
        "structures": structures,
        "logs": logs,
    })

    return structures, logs


@application.route("/", methods=["GET", "POST"])
def main_site():
    if request.method == "GET":
        return render_template("index.html")

    # POST

    # create temporary directories for computation
    tmp_dir = tempfile.mkdtemp(prefix="compute_")
    for d in ["input", "output", "logs"]:
        os.mkdir(os.path.join(tmp_dir, d))

    # prepare input files
    if request.form["type"] in ["settings", "charges"]:
        if not prepare_file(request, tmp_dir):
            message = "Invalid file provided. Supported types are common chemical formats: sdf, mol2, pdb, cif and zip or tar.gz of those."
            flash(message, "warning")
            return render_template("index.html")
    elif request.form["type"] == "example":
        prepare_example(request, tmp_dir)
    else:
        raise RuntimeError("Bad type of input")

    # prepare suitable methods and parameters
    comp_id = str(uuid.uuid1())
    try:
        methods, parameters = get_suitable_methods(tmp_dir)
    except RuntimeError as e:
        flash(f"Error: {e}", "danger")
        return render_template("index.html")

    request_data[comp_id] = {
        "tmpdir": tmp_dir,
        "suitable_methods": methods,
        "suitable_parameters": parameters,
    }

    # calculate charges with default method and parameters
    if request.form["type"] in ["charges", "example"]:
        calculate_charges_default(methods, parameters, tmp_dir, comp_id)
        return redirect(url_for("results", r=comp_id, example_name=request.form['example-name']))

    return redirect(url_for("setup", r=comp_id))


@application.route("/setup", methods=["GET", "POST"])
def setup():
    comp_id = request.args.get("r")
    try:
        comp_data = request_data[comp_id]
    except KeyError:
        abort(404)

    tmp_dir = comp_data["tmpdir"]
    suitable_methods = comp_data["suitable_methods"]
    suitable_parameters = comp_data["suitable_parameters"]

    if request.method == "GET":
        return render_template(
            "setup.html",
            methods=method_data,
            parameters=parameter_data,
            suitable_methods=suitable_methods,
            suitable_parameters=suitable_parameters,
        )

    calculation_list = request.form.getlist("calculation_item")
    calculations = prepare_calculations(calculation_list)

    calculate_charges(calculations, tmp_dir, comp_id)

    return redirect(url_for("results", r=comp_id))


@application.route("/results")
def results():
    comp_id = request.args.get("r")
    example_name = request.args.get("example_name")
    try:
        comp_data = request_data[comp_id]
    except KeyError:
        abort(404)

    logs = ""
    if "stderr" in comp_data["logs"]:
        logs = comp_data["logs"]["stderr"]
        flash("Some errors occured during the computation, see log for details.", "danger")

    return render_template(
        "results.html",
        comp_id=comp_id,
        example_name=example_name,
        structures=comp_data["structures"].keys(),
        logs=logs,
    )


@application.route("/download")
def download_charges():
    comp_id = request.args.get("r")
    comp_data = request_data[comp_id]
    tmpdir = comp_data["tmpdir"]

    shutil.make_archive(os.path.join(tmpdir, "charges"),
                        "zip", os.path.join(tmpdir, "output"))

    return send_file(
        f"{tmpdir}/charges.zip",
        as_attachment=True,
        download_name=f"charges.zip",
        max_age=0,
    )


@application.route("/structure")
def get_structure():
    comp_id = request.args.get("r")
    structure_id = request.args.get("s")
    comp_data = request_data[comp_id]

    return Response(comp_data["structures"][structure_id], mimetype="text/plain")


@application.route("/logs")
def get_logs():
    comp_id = request.args.get("r")
    comp_data = request_data[comp_id]

    return Response(comp_data["logs"]["stderr"], mimetype="text/plain")


@application.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404
