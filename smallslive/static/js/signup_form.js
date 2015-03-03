$loginForm = $('#form-login');

$loginForm.submit(function(e){
    e.preventDefault();
    $.ajax({
        type: "POST",
        url: '/accounts/login/',
        data: $loginForm.serialize(),
        success: function(data) {
            window.location = data.location;
        },
        error: function(jqXHR, textStatus, errorThrown) {
            var response = jqXHR.responseJSON;
            //$("#login-modal").html(jqXHR.responseJSON.html);
            if (response.form_errors.login) {
                $("input[name=login]").parent().addClass('has-error');
                $("#login-error").removeClass('hidden').text(response.form_errors.login[0]);
            }
            if (response.form_errors.password) {
                $("input[name=password]").parent().addClass('has-error');
                $("#password-error").removeClass('hidden').text(response.form_errors.password[0]);
            }
        }
    });
    return false;

});
