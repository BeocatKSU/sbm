function parse_boot_config_list(response) {
        $('#boot_config_list').empty();
        if (typeof(response) != "object") {
                response = [response];
        } 
        response.sort();
        for(var i = 0; i < response.length; i++) {
                $('#boot_config_list').append($('<button type="button">').append(response[i]).addClass("boot_config list-group-item"));
        }
        $('.boot_config').on('click', function() {
                set_boot_config($(this).text());
                load_boot_config($(this).text());
        });
}
function parse_machine_list(response) {
        $('#machine_list').empty();
        if (typeof(response) != "object") {
                response = [response];
        } 
        response.sort();
        for(var i = 0; i < response.length; i++) {
                $('#machine_list').append($('<button type="button">').append(response[i]).addClass("machine_config list-group-item"));
        }
        $('.machine_config').on('click', function() {
                load_machine($(this).text());
        });
}
function parse_variable_list(response) {
        $('#variable_list').empty();
        if (typeof(response) != "object") {
                response = [response];
        } 
        response.sort();
        for(var i = 0; i < response.length; i++) {
                $('#variable_list').append($('<button type="button">').append(response[i]).addClass("variable list-group-item"));
        }
        $('.variable').on('click', function() {
                load_variable($(this).text());
        });
}
function parse_boot_config_response(response) {
        $('#config').val(response['config']);
        $('#config').attr('rows', response['config'].split(/\r\n|\r|\n/).length + 5);
        $('#title').val(response['title']);
}
function parse_machine_response(response) {
        $('#hostname').val(response['hostname']);
        $('#default_boot').val(response['default_boot']);
        $('#alternate_boot').val(response['alternate_boot']);
        $('#switch_type').val(response['switch_type']);
        $('#time_between').val(response['time_between']);
        if(response['switch_type'] == 'timed') {
                $("#time_between_div").show();
        } else {
                $("#time_between_div").hide();
        }
}
function parse_variable_response(response) {
        $('#value').val(response['value']);
        $('#value').attr('rows', response['value'].split(/\r\n|\r|\n/).length + 5);
        $('#key').val(response['key']);
}
function log_ajax_err(xhr, resp, text) {
        console.log(xhr, resp, text);
        response = xhr.responseJSON['err'];
        $('#modal-2 .modal-body').empty();
        $('#modal-2 .modal-body').append($('<textarea readonly class="form-control">').append(response));
        $('#modal-2 .modal-body textarea').attr('rows', response.split(/\r\n|\r|\n/).length + 3);
        $('#modal-2 .modal-title').text("" + xhr.status + ': ' + xhr.statusText);
        $('#modal-2').modal('show');
}
function get_boot_configs() {
        $.ajax({
                url: '/api/v1/boot_config/',
                type: 'GET',
                success: parse_boot_config_list,
                error: log_ajax_err
        })
}
function get_machines() {
        $.ajax({
                url: '/api/v1/machine/',
                type: 'GET',
                success: parse_machine_list,
                error: log_ajax_err
        })
}
function get_variables() {
        $.ajax({
                url: '/api/v1/variable/',
                type: 'GET',
                success: parse_variable_list,
                error: log_ajax_err
        })
}
function load_boot_config(title) {
        $.ajax({
                url: '/api/v1/boot_config/' + title + '/',
                type: 'GET',
                success: parse_boot_config_response,
                error: log_ajax_err
        })
}
function load_machine(hostname) {
        $.ajax({
                url: '/api/v1/machine/' + hostname + '/',
                type: 'GET',
                success: parse_machine_response,
                error: log_ajax_err
        })
}
function load_variable(key) {
        $.ajax({
                url: '/api/v1/variable/' + key + '/',
                type: 'GET',
                success: parse_variable_response,
                error: log_ajax_err
        })
}
function set_boot_config(title) {
        if ($("#default_boot").val() == "") {
                $("#default_boot").val(title);
        }
        if ($("#alternate_boot").val() == "") {
                $("#alternate_boot").val(title);
        }
}
function test_dialog(response) {
        $('#modal-1 .modal-body').empty();
        $('#modal-1 .modal-body').append($('<textarea readonly class="form-control">').append(response));
        $('#modal-1 .modal-body textarea').attr('rows', response.split(/\r\n|\r|\n/).length + 3);
        $('#modal-1').modal('show');
}
function serialize_form(form) {
        form = form.serializeArray();
        var data = {};
        for (var i = 0; i < form.length; i++) {
                data[form[i].name] = form[i].value;
        }
        return JSON.stringify(data);
}
