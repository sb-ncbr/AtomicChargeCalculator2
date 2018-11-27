'use strict';

$(function() {
        /* Set the contents */
        var options = '';
        $.each(method_data, function(key, method) {
            options += '<option value=' + method.name + '>' + method.name +'</option>\n';
        })

        var $select = $('#methodselection');
        $select.append(options);

        /* Update data on select change */
        $('#methodselection').on('change', function() {
            var name = $('#methodselection option:selected').val();
            var e = method_data.find(function (element) {
                return element.name === name;
            })

            $('#description').text(e.description);
            $('#full_name').text(e.full_name);
            if(e.paper == null) {
                $('#paper').text('None');
            } else {
                $('#paper').html('<a href="https://doi.org/' + e.paper + '">' + e.paper + '</a>');
            }
        })

        $select.trigger('change');
});
