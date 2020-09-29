'use strict';


const spinner = '<span class="spinner-border spinner-border-sm" role="status" ' +
    'aria-hidden="true" style="animation-duration: 1.5s"></span>';


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
    const $buttons = $('.btn');
    $buttons.each(function () {
        $(this).prop('disabled', true);
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

    const $submit = $('#calculate');
    $submit.on('click', function () {
        disable_buttons();
        $submit.html(`${spinner} Computing...`);
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

    let $min_value = $('#min_value');
    let $max_value = $('#max_value');

    $select.on('changed.bs.select', function () {
        const id = $select.val();
        $.ajax({
            url: get_format_url + `&s=${id}`,
            success: function (format) {
                LiteMolChargesViewerEventQueue.send("lm-load-molecule", {
                    structure_url: get_structure_url + `&s=${id}`,
                    charges_url: get_charges_url + `&s=${id}`,
                    structure_format: format,
                    charges_format: 'TXT'
                });
            }
        });

        if (chg_range.hasOwnProperty(id)) {
            $('input:radio[name=colors]').prop('disabled', false);
        } else {
            $('input:radio[name=colors][value="Structure"]').prop('checked', true);
            $('input:radio[name=colors]').prop('disabled', true);
            $min_value.val(0);
            $max_value.val(0);
        }

        if ($('input[name=colors]:checked').val() === 'Relative') {
            $min_value.val(-chg_range[id]);
            $max_value.val(chg_range[id]);
            $min_value.trigger('input');
        }
    });


    $('#min_value, #max_value').on('input', function () {
        update_litemol_colors(parseFloat($('#min_value').val()), parseFloat($('#max_value').val()));
        $min_value.attr('max', $max_value.val());
        $max_value.attr('min', $min_value.val());
    });

    let $colors = $('input[name=colors]');
    $colors.on('change', function () {
        let coloring = $('input[name=colors]:checked').val();
        if (coloring === 'Relative') {
            LiteMolChargesViewerEventQueue.send('lm-use-default-themes', {value: false});
            const id = $select.val();
            $min_value.val(-chg_range[id]);
            $max_value.val(chg_range[id]);

            update_litemol_colors(null, null);
            $min_value.prop('disabled', true);
            $max_value.prop('disabled', true);
        } else if (coloring === 'Absolute') {
            LiteMolChargesViewerEventQueue.send('lm-use-default-themes', {value: false});
            $min_value.prop('disabled', false);
            $max_value.prop('disabled', false);
            $min_value.trigger('input');
        } else {
            /* Coloring by elements */
            LiteMolChargesViewerEventQueue.send('lm-use-default-themes', {value: true});
        }
    });

    let $view = $('input[name=view]');
    $view.on('change', function () {
        let v = $('input[name=view]:checked').val();
        if (v === 'Cartoon') {
            LiteMolChargesViewerEventQueue.send('lm-switch-to-cartoons');
        } else if (v === 'Balls and sticks') {
            LiteMolChargesViewerEventQueue.send('lm-switch-to-bas');
        } else {
            /* Surface */
            LiteMolChargesViewerEventQueue.send('lm-switch-to-surface');
        }
    });

    $select.trigger('changed.bs.select');
    $colors.filter(':checked').trigger('change');


    /* Change the state of a radio button to reflect view LiteMol chooses when it loads a molecule */
    LiteMolChargesViewerEventQueue.subscribe("lm-visualization-mode-changed", (event_info) => {
        if (event_info.mode === 'balls-and-sticks') {
            $('input:radio[name=view][value="Balls and sticks"]').prop('checked', true);
        } else if (event_info.mode === 'cartoons') {
            $('input:radio[name=view][value="Cartoon"]').prop('checked', true);
        }
    });
}


$(function () {
    let page = window.location.pathname;
    if (page === '/') {
        init_index();
    } else if (page === '/setup') {
        $.getJSON('/static/publication_info.json', function (data) {
            init_setup(data);
        });
    } else if (page === '/results') {
        init_results();
    }
});
