'use strict';

function es(str) {
    return str.replace('/', '\\/').replace('+', '\\+');
}

function fill_paper($element, doi) {
    if (localStorage.getItem(doi) != null) {
        $element.html(localStorage[doi]);
    } else {
        $element.html('<i class="fa fa-spinner fa-spin fa-2x fa-fw margin-bottom"></i>');
        $.ajax({
            url: 'https://doi.org/' + doi,
            headers: {'Accept': 'text/x-bibliography;style=apa'},
            type: 'GET',
            success: function (result) {
                result = result.replace(/doi:(.*)/, '<a href="https://doi.org/$1">doi:$1</a>');
                localStorage[doi] = result;
                $element.html(result);
            },
            error: function (e) {
                $element.html(`<a href="https://doi.org/${doi}">${doi}</a>`);
            }
        });
    }
}


function hide_parameters_publication(val) {
    $('#parameters_paper').prop('hidden', val);
    $('#parameters_paper_label').prop('hidden', val);
}


function init_index() {
    /* Allow submit only if file is selected */
    const $input = $('#file_input');
    const $submit = $('#upload');

    $submit.prop('disabled', true);

    $input.on('change', function () {
        if ($input.val()) {
            $submit.prop('disabled', false);
        } else {
            $submit.prop('disabled', true);
        }
    });

    $submit.on('click', function () {
        if ($input[0].files[0].size > 10 * 1024 * 1024) {
            alert('Cannot upload file larger than 10 MB');
            $submit.prop('disabled', true);
        } else {
            $submit.html('<i class="fa fa-spinner fa-spin fa-fw margin-bottom"></i> Uploading...');
            $submit.prop('disabled', true);
            $('#type').val('upload');
            $('form').submit();
        }
    });
}


function init_computation() {
    const $m_select = $('#method_selection');
    const $m_group2d = $('#optgroup2D');
    const $m_group3d = $('#optgroup3D');
    const $p_select = $('#parameters_selection');

    /* Set available methods */
    $.each(method_data, function (key, method) {
        if (suitable_methods.includes(method.name)) {
            const str = `<option value="${method.name}">${method.name}</option>\n`;
            if (method.type === "2D")
                $m_group2d.append(str);
            else if (method.type === "3D")
                $m_group3d.append(str);
            else
                $m_select.append(str);
        }
    });

    /* Update parameter publication on change */
    $p_select.on('change', function () {
        const m_name = $('#method_selection option:selected').val();
        const p_name = $('#parameters_selection option:selected').text();

        const e = parameter_data[m_name].find(function (element) {
            return element.name === p_name;
        });

        /* Default parameters (not found in parameter_data) have no publication assigned */
        if (e === undefined) {
            hide_parameters_publication(true);
        } else {
            hide_parameters_publication(false);
            /* Some parameters have no publication */
            if (e.publication == null) {
                $('#parameters_paper').text('None');
            } else {
                fill_paper($('#parameters_paper'), e.publication);
            }
        }
    });

    /* Update method data on method select change */
    $m_select.on('change', function () {
        const m_name = $('#method_selection option:selected').val();
        const e = method_data.find(function (element) {
            return element.name === m_name;
        });

        $p_select.empty();
        if (e.has_parameters) {
            let p_options = '';
            $p_select.prop('disabled', false);
            if (parameter_data[m_name].length > 1) {
                $p_select.append('<option value="default">Select best (default)</option>');
            }
            $.each(parameter_data[m_name], function (key, parameter_set) {
                if (suitable_parameters[m_name].includes(parameter_set.filename)) {
                    p_options += `<option value="${parameter_set.filename}">${parameter_set.name}</option>\n`;
                }
            });
            $p_select.append(p_options);
            $p_select.trigger('change');
        } else {
            $p_select.prop('disabled', true);
            $p_select.append('<option value="NA">No parameters<option>');
            hide_parameters_publication(true);
        }

        $('#method_name').text(e.full_name);

        if (e.publication == null) {
            $('#method_paper').text('None');
        } else {
            fill_paper($('#method_paper'), e.publication);
        }
    });

    $m_select.trigger('change');

    const $submit = $('#calculate');
    $submit.on('click', function () {
        $submit.html('<i class="fa fa-spinner fa-spin fa-fw margin-bottom"></i> Computing...');
        $submit.prop('disabled', true);
        $('form').submit();
    });
}


function update_litemol_colors(min_color, max_color) {
    LiteMolChargesViewerEventQueue.send("lm-set-default-color-scheme", {
        minVal: min_color,
        maxVal: max_color,
        fallbackColor: {r: 0, g: 255, b: 0},
        minColor: {r: 255, g: 0, b: 0},
        maxColor: {r: 0, g: 0, b: 255},
        middleColor: {r: 255, g: 255, b: 255}
    });
}


function init_results() {
    const $select = $('#structure_select');
    $select.select2({width: 'auto', placeholder: 'Select a structure'});
    $select.on('select2:select', function (e) {
        let format = e.params.data.id.split(':')[0].split('.')[1].toUpperCase();
        if (format === 'ENT') {
            format = 'PDB';
        } else if (format === 'CIF') {
            format = 'mmCIF'
        }
        LiteMolChargesViewerEventQueue.send("lm-load-molecule", {
            structure_url: get_structure_url + `&s=${e.params.data.id}`,
            charges_url: get_charges_url + `&s=${e.params.data.id}`,
            structure_format: format,
            charges_format: 'TXT'
        });
    });

    let $min_value = $('#min_value');
    let $max_value = $('#max_value');

    $('#min_value, #max_value').on('input', function () {
        update_litemol_colors(parseFloat($('#min_value').val()), parseFloat($('#max_value').val()));
        $min_value.attr('max', $max_value.val());
        $max_value.attr('min', $min_value.val());
    });

    let $colors = $('input[name=colors]');
    $colors.on('change', function () {
        let coloring = $('input[name=colors]:checked').val();
        if (coloring === 'Relative') {
            update_litemol_colors(null, null);
            $min_value.prop('disabled', true);
            $max_value.prop('disabled', true);
        } else {
            $min_value.prop('disabled', false);
            $max_value.prop('disabled', false);
            $min_value.trigger('input');
        }
    });

    $colors.trigger('change');
}


$(function () {
    let page = window.location.pathname;
    if (page === '/') {
        init_index();
    } else if (page === '/computation') {
        init_computation();
    } else if (page === '/results') {
        init_results();
    }
});
