'use strict';


const spinner = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true" style="animation-duration: 1.5s">\
                    <span class="sr-only">Loading...</span>\
                </span>';
const icon_close = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill" viewBox="0 0 16 16">\
                        <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/>\
                    </svg>'

function fill_paper($element, publication_data, doi) {
    if (doi === null) {
        $element.html('None');
    } else if (doi in publication_data) {
        $element.html(publication_data[doi].replace(/doi:(.*)/, '<a href="https://doi.org/$1">doi:$1</a>'));
    } else {
        $element.html(`<a href="https://doi.org/${doi}">${doi}</a>`);
    }
}


function hide_parameters_publication(val) {
    $('#parameters_paper').prop('hidden', val);
    $('#parameters_paper_label').prop('hidden', val);
}


function disable_buttons() {
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach((button) => {
        button.setAttribute('disabled', true);
    });
}


function init_index() {
    /* Allow submit only if file is selected */
    const $input = $('#file_input');
    const $settings = $('#settings');
    const $charges = $('#charges');
    const $examples = $('button[name^="example"]');

    $settings.prop('disabled', true);
    $charges.prop('disabled', true);

    $input.on('change', function () {
        if ($input.val()) {
            $settings.prop('disabled', false);
            $charges.prop('disabled', false);
        } else {
            $settings.prop('disabled', true);
            $charges.prop('disabled', true);
        }
    });

    $examples.on('click', function () {
        disable_buttons();
        $(this).html(`${spinner} Computing...`);
        $('#example-name').val($(this).prop('name'));
        $('form').submit();
    });

    $settings.on('click', function (e) {
        if ($input[0].files[0].size > 10 * 1024 * 1024) {
            alert('Cannot upload file larger than 10 MB');
            e.preventDefault();
        } else {
            disable_buttons();
            $settings.html(`${spinner} Uploading...`);
            $('#type').val('settings');
            $('form').submit();
        }
    });

    $charges.on('click', function (e) {
        if ($input[0].files[0].size > 10 * 1024 * 1024) {
            alert('Cannot upload file larger than 10 MB');
            e.preventDefault();
        } else {
            disable_buttons();
            $charges.html(`${spinner} Computing...`);
            $('#type').val('charges');
            $('form').submit();
        }
    });

    /* Fix disabled buttons when user press Back button in browser (at least in Chrome) */
    $input.trigger('change');
}


function init_setup(publication_data) {
    const $m_select = $('#method_selection');
    const $m_group2d = $('#optgroup2D');
    const $m_group3d = $('#optgroup3D');
    const $p_select = $('#parameters_selection');

    /* Set available methods */
    for (const method of suitable_methods) {
        const data = method_data.find(m => m.internal_name === method);
        const str = `<option value="${data.internal_name}">${data.name}</option>\n`;
        if (data.type === "2D")
            $m_group2d.append(str);
        else if (data.type === "3D")
            $m_group3d.append(str);
        else
            $m_select.append(str);
    }

    /* Update parameter publication on change */
    $p_select.on('change', function () {
        const m_name = $('#method_selection option:selected').val();
        const p_name = $('#parameters_selection option:selected').text();

        const e = parameter_data[m_name].find(function (element) {
            return element.name === p_name;
        });

        fill_paper($('#parameters_paper'), publication_data, e.publication);
    });

    /* Update method data on method select change */
    $m_select.on('change', function () {
        const m_name = $('#method_selection option:selected').val();
        const e = method_data.find(function (element) {
            return element.internal_name === m_name;
        });

        $p_select.empty();
        if (e.has_parameters) {
            let p_options = '';
            $p_select.prop('disabled', false);
            for (const parameters of suitable_parameters[m_name]) {
                const parameter_set = parameter_data[m_name].find(p => p.filename === parameters);
                p_options += `<option value="${parameter_set.filename}">${parameter_set.name}</option>\n`;
            }

            $p_select.append(p_options);
            hide_parameters_publication(false);
            $p_select.trigger('change');
        } else {
            $p_select.prop('disabled', true);
            $p_select.append('<option value="NA">No parameters<option>');
            hide_parameters_publication(true);
        }

        $('#method_name').text(e.full_name);

        fill_paper($('#method_paper'), publication_data, e.publication);

        $('.selectpicker').selectpicker('refresh');
    });

    $m_select.trigger('change');

    // TODO: fix spinner not working
    const $submit = $('#calculate');
    $submit.on('click', function () {
        disable_buttons();
        $submit.html(`${spinner} Computing...`);
        $submit.prop('disabled', true);
        $('form').submit();
    });
}

let molstar;
let typeId = 1;

async function init_results() {
    molstar = await MolstarPartialCharges.create("root", {
        SbNcbrPartialCharges: true
    });
    mountControls();
    await load();
    // molstar must be first initialized
    await mountChargeSetControls();
    $('.selectpicker').selectpicker('refresh');
}

async function load() {
    const selection = document.getElementById('structure_select');
    const cartoon = document.getElementById("view_cartoon");
    const bas = document.getElementById("view_bas");
    const relative = document.getElementById("colors_relative");
    const reset_button = document.getElementById("reset_max_charge");
    if (!selection || !cartoon || !bas || !relative || !reset_button) {
        console.error("Controls not found");
        return;
    }
    const id = selection.value;
    const structure_url = `${get_structure_url}&s=${id}`;

    await molstar.load(structure_url, "mmcif", "ACC2");
    molstar.charges.setTypeId(typeId);

    if (molstar.type.isDefaultApplicable()) {
        cartoon.removeAttribute('disabled');
        cartoon.checked = true;
    } else {
        cartoon.setAttribute('disabled', true);
        bas.checked = true;
    }

    relative.setAttribute('checked', true);
    await updateColor();
    await updateView();

    reset_button.click();
}

function mountControls() {
    mountStructureControls();
    mountTypeControls();
    mountColorControls();
}

function mountStructureControls() {
    const selection = document.getElementById('structure_select');
    if (!selection) {
        console.error("Structure select not found");
        return;
    }
    selection.onchange = async () => await load();
}

async function mountChargeSetControls() {
    const select = document.getElementById('charge_set_select');
    const relative = document.getElementById("colors_relative");
    if (!select || !relative) {
        console.error("Charge set select not found");
        return;
    }
    const options = molstar.charges.getMethodNames();
    for (let i = 0; i < options.length; ++i) {
        const option = document.createElement('option');
        option.value = `${i + 1}`;
        option.innerText = options[i];
        option.selected = i + 1 === typeId;
        select.appendChild(option);
    }

    select.onchange = async () => {
        typeId = Number(select.value);
        molstar.charges.setTypeId(typeId);
        await updateColor();
        setMethodAndParametersName();
    }
    select.onchange();

    // const attributeChangedCallback = (mutationsList) => {
    //     mutationsList.forEach(async (mutation) => {
    //         if (mutation.type === 'attributes') {
    //             const typeId = document.querySelector('[id^=bs-select-2-].active').getAttribute('aria-posinset');
    //             if (typeId === undefined) {
    //                 console.error("Type id not found");
    //                 return;
    //             }
    //             molstar.charges.setTypeId(Number(typeId));
    //             await updateColor();
    //             setMethodAndParametersName();

    //             console.log('mutation', typeId);
    //         }
    //     });
    // };

    // const targetElement = document.querySelector('[aria-activedescendant^="bs-select-2-"]');
    // const observer = new MutationObserver(attributeChangedCallback);
    // const observerConfig = { attributes: true };
    // observer.observe(targetElement, observerConfig);
}

function setMethodAndParametersName() {
    const method_name = document.getElementById('method_name');
    const parameters_name = document.getElementById('parameters_name');
    const select = document.getElementById('charge_set_select');
    if (!method_name || !parameters_name || !select) {
        console.error("Method or parameters name not found");
        return;
    }

    const selected_option = select.options[select.selectedIndex];
    method_name.innerText = `Method: ${selected_option.innerText.split('/')[0]}`;
    parameters_name.innerText = `Parameters: ${selected_option.innerText.split('/')[1]}`;
}

function mountTypeControls() {
    const cartoon = document.getElementById("view_cartoon");
    const surface = document.getElementById("view_surface");
    const bas = document.getElementById("view_bas");
    if (!cartoon || !surface || !bas) {
        console.error("Type controls not found");
        return;
    }
    cartoon.onclick = async () => await molstar.type.default();
    surface.onclick = async () => await molstar.type.surface();
    bas.onclick = async () => await molstar.type.ballAndStick();
}

function mountColorControls() {
    const structure = document.getElementById("colors_structure");
    const relative = document.getElementById("colors_relative");
    const absolute = document.getElementById("colors_absolute");
    const range = document.getElementById("max_value");
    const reset = document.getElementById("reset_max_charge");
    if (!structure || !relative || !absolute || !range || !reset) {
        console.error("Color controls not found");
        return;
    }
    structure.onclick = async () => await updateDefaultColor();
    relative.onclick = async () => await updateRelativeColor();
    absolute.onclick = async () => await updateAbsoluteColor();
    range.oninput = async () => await updateRange();
    reset.onclick = async () => await resetRange();
}

async function updateDefaultColor() {
    const input = document.getElementById("max_value");
    if (!input) {
        console.error("Max value input not found");
        return;
    }
    input.setAttribute("disabled", "true");
    await molstar.color.default();
}

async function updateRelativeColor() {
    const input = document.getElementById("max_value");
    if (!input) {
        console.error("Max value input not found");
        return;
    }
    input.setAttribute("disabled", "true");
    await molstar.color.relative();
}

async function updateAbsoluteColor() {
    const input = document.getElementById("max_value");
    if (!input) {
        console.error("Max value input not found");
        return;
    }
    input.removeAttribute("disabled");
    await updateRange();
}

async function updateRange() {
    const input = document.getElementById("max_value");
    if (!input) {
        console.error("Max value input not found");
        return;
    }
    const value = Number(input.value);
    const min = Number(input.min);
    if (isNaN(value)) return;
    if (value < min) input.value = min;
    await molstar.color.absolute(input.value);
}

async function resetRange() {
    const input = document.getElementById("max_value");
    if (!input) {
        console.error("Max value input not found");
        return;
    }
    const maxCharge = molstar.charges.getMaxCharge();
    input.value = maxCharge;
    if (!input.hasAttribute("disabled")) {
        await updateRange();
    }
}

function mountAddCalculationControls() {
    const method_selection = document.getElementById('method_selection');
    const parameters_selection = document.getElementById('parameters_selection');
    const button = document.getElementById('add_to_calculation');
    const list = document.getElementById('calculation_list');

    if (!method_selection || !parameters_selection || !button || !list) {
        console.error('Missing elements');
        return;
    }

    button.onclick = () => {
        const method = method_selection.value;
        const parameters = parameters_selection.value;
        const name = method_selection.options[method_selection.selectedIndex].text;
        const parameters_name = parameters_selection.options[parameters_selection.selectedIndex].text;

        if (checkUniqueList(list, method, parameters)) {
            list.appendChild(createListItem(name, parameters_name, method, parameters));
        }
        updateComputeButton();
    }
}

function updateComputeButton() {
    const list = document.getElementById('calculation_list');
    if (!list) {
        console.error('Missing elements');
        return;
    }
    if (isListEmpty(list)) {
        document.getElementById('calculate').setAttribute('disabled', 'true');
    } else {
        document.getElementById('calculate').removeAttribute('disabled');
    }
}

function isListEmpty(list) {
    return list.children.length === 0;
}

function checkUniqueList(list, method, parameters) {
    for (let i = 0; i < list.children.length; ++i) {
        const item = list.children[i];
        if (item.dataset.method === method && item.dataset.parameters === parameters) {
            return false;
        }
    }
    return true;
}

function checkListCount(list) {
    return list.children.length > 0;
}

function createListItem(method_name, parameters_name, method, parameters) {
    const item = document.createElement('div');
    item.classList.add('border', 'col-12', 'col-md-6', 'pr-3', 'list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');
    item.innerText = `${method_name} (${parameters_name})`;
    item.dataset.method = method;
    item.dataset.parameters = parameters;
    item.appendChild(createInput('calculation_item', method, parameters));
    item.appendChild(createRemoveButton());

    return item;
}

function createInput(name, method, parameters) {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = name;
    input.value = `${method} ${parameters}`;
    return input;
}

function createRemoveButton() {
    const button = document.createElement('button');
    button.classList.add('btn', 'btn-sm', 'p-0');
    button.type = 'button';
    const icon = document.createElement('span');
    icon.innerHTML = icon_close;
    button.appendChild(icon);

    button.onclick = () => {
        const item = button.parentElement;
        item.parentElement.removeChild(item);
        updateComputeButton();
    }

    return button;
}

async function setupExampleDefaults() {
    const surface = document.getElementById("view_surface");
    const structure_select = document.getElementById("structure_select");
    const relative = document.getElementById("colors_relative");

    if (!surface || !structure_select || !relative) {
        console.error("Missing elements");
        return;
    }

    if (example_name === 'example-receptor') {
        surface.checked = true;
        await updateView();
    } else if (example_name === 'example-phenols') {
        structure_select.value = 'PROPOFOL'
        $('.selectpicker').selectpicker('refresh')
        structure_select.onchange()
    }
}

async function updateColor() {
    const actionName = document.querySelector('#colors_structure:checked, #colors_absolute:checked, #colors_relative:checked').id
    if (!actionName) {
        console.error("Error getting color action name");
        return;
    }
    const actions = {
        'colors_relative': updateRelativeColor,
        'colors_absolute': updateAbsoluteColor,
        'colors_structure': async () => { },
    }
    await actions[actionName]()
}

async function updateView() {
    const actionName = document.querySelector('#view_cartoon:checked, #view_bas:checked, #view_surface:checked').id
    if (!actionName) {
        console.error("Error getting view action name");
        return;
    }
    const actions = {
        'view_cartoon': async () => await molstar.type.default(),
        'view_bas': async () => await molstar.type.ballAndStick(),
        'view_surface': async () => await molstar.type.surface(),
    }
    await actions[actionName]()
}

$(async function () {
    let page = window.location.pathname;
    if (page === '/') {
        init_index();
    } else if (page === '/setup') {
        $.getJSON('/static/publication_info.json', function (data) {
            init_setup(data);
        });
        mountAddCalculationControls();
    } else if (page === '/results') {
        await init_results();
        await setupExampleDefaults()
    }
});
