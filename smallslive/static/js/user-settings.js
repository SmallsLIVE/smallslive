var $forms = $('form');

$forms.each(function(index, form) {
   var inputs = $(form).find(':input');
    inputs.on('input change select', function() {
        var submitButton = $(form).find("input[type='submit']");
        submitButton.prop('disabled', false).removeClass('disabled');
    });
});
