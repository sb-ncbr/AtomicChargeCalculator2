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
        const str = `<option value="${method.name}">${method.name}</option>\n`;
        if (method.type === "2D")
            $m_group2d.append(str);
        else if (method.type === "3D")
            $m_group3d.append(str);
        else
            $m_select.append(str);
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

        if (e.options) {
            $('#collapse-options').removeClass('show');
            $.each($('div[id^="options"]'), function (key, div) {
                let $div = $(div);
                $div.hide();
            });
            $(`#options-${es(m_name)}`).show();
            $('#method-options-row').show();
        } else {
            $('#method-options-row').hide();
        }

        $p_select.empty();
        if (e.has_parameters) {
            let p_options = '';
            $p_select.prop('disabled', false);
            if (parameter_data[m_name].length > 1) {
                $p_select.append('<option value="default">Select best (default)</option>');
            }
            $.each(parameter_data[m_name], function (key, parameter_set) {
                p_options += `<option value="${parameter_set.filename}">${parameter_set.name}</option>\n`;
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
}


$(function () {
    let page = window.location.pathname;
    if (page === '/') {
        init_index();
    } else if (page === '/computation') {
        init_computation();
    }
});
