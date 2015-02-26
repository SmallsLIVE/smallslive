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
            $("input[name=login]").parent().addClass('has-error');
            $("#login-error").text(response.form_errors.login[0]);
            $("input[name=password]").parent().addClass('has-error');
        }
    });
    return false;

});
