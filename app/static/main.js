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
            error: function () {
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
    const $settings = $('#settings');
    const $charges = $('#charges');

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

    $settings.on('click', function () {
        $settings.prop('disabled', true);
        $charges.prop('disabled', true);
        if ($input[0].files[0].size > 10 * 1024 * 1024) {
            alert('Cannot upload file larger than 10 MB');
        } else {
            $settings.html('<i class="fa fa-spinner fa-spin fa-fw margin-bottom"></i> Uploading...');
            $('#type').val('settings');
            $('form').submit();
        }
    });

    $charges.on('click', function () {
        $settings.prop('disabled', true);
        $charges.prop('disabled', true);
        if ($input[0].files[0].size > 10 * 1024 * 1024) {
            alert('Cannot upload file larger than 10 MB');
        } else {
            $charges.html('<i class="fa fa-spinner fa-spin fa-fw margin-bottom"></i> Uploading...');
            $('#type').val('charges');
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
        if (suitable_methods.includes(method.internal_name)) {
            const str = `<option value="${method.internal_name}">${method.name}</option>\n`;
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

        fill_paper($('#parameters_paper'), e.publication);
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
    $select.select2({width: 'auto'});
    $select.on('select2:select', function () {
        const id = $select.select2('data')[0].id;
        let format = id.split(':')[0].split('.')[1].toUpperCase();
        if (format === 'ENT') {
            format = 'PDB';
        } else if (format === 'CIF') {
            format = 'mmCIF'
        } else if (format === 'MOL2') {
            /* We converted MOL2 to SDF as LiteMol can't handle it */
            format = 'SDF'
        }
        LiteMolChargesViewerEventQueue.send("lm-load-molecule", {
            structure_url: get_structure_url + `&s=${id}`,
            charges_url: get_charges_url + `&s=${id}`,
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
    $select.trigger('select2:select');
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
