var $forms = $('form');

$forms.each(function(index, form) {
   var inputs = $(form).find(':input');
    inputs.on('input change select', function() {
        var submitButton = $(form).find("input[type='submit']");
        submitButton.prop('disabled', false).removeClass('disabled');
    });
});

/* Settings payment div reveal Paypal js */
$(document).ready(function () {
    if ($('input[name=payout_method]:checked').val() === "Check") {
        $("#paypal-info").css("display", "none");
    }
    $(".radio-button").click(function(){
        if ($('input[name=payout_method]:checked').val() === "PayPal") {
            $("#paypal-info").slideDown("fast"); //Slide Down Effect
            $.cookie('showTop', 'expanded'); //Add cookie 'ShowTop'
        } else {
            $("#paypal-info").slideUp("fast");
            $.cookie('showTop', 'collapsed'); //Add cookie 'ShowTop'
        }
     });


    var $countrySelect = $('select[name=country]');
    if ($countrySelect.val() !== "US") {
        $("#taxpayer_id").css("display", "none");
    }

    $countrySelect.on('change', function(){
        if ($countrySelect.val() === "US") {
            $("#taxpayer_id").slideDown("fast"); //Slide Down Effect
        } else {
            $("#taxpayer_id").slideUp("fast");
        }
     });
});

