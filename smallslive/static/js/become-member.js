$(document).ready(function(){
  var monthlyQuantities = [10, 20, 50];
  var yearlyQuantities = [100, 500, 1000];

  var currentStep = 0;
  var backButton = $("#backButton");
  var confirmButton = $("#confirmButton");
  var sentHint = $('#sentHint');

  var selectedData = {
    type: '',
    quantity: 0
  };

  var panels = [1, 2, 3].map(function (index) {
    return $("#supporterStep" + index)
  });

  var buttons = $('#supporterSteps > *');
  var monthlyButtons = $("#monthlyPledge > button");

  var $supporterForm = $('#formSupporter');
  // $supporterForm.submit(getAjaxSubmitForForm(
  //   $supporterForm, [
  //     "type", "quantity", "card_name", "expiration_date", "credit_card_number",
  //     "credit_card_cvc"
  //   ]
  // ));

  var resetButtons = function () {
    [monthlyButtons, yearlyButtons].forEach(function (buttons) {
      buttons.each(function (index, el) {
        $(el).removeClass("active");
      });
    })
  };

  var updatePaymentInfo = function () {
    var pledgeType = selectedData.type;
    var pledgeAmount = selectedData.quantity;
    console.log(pledgeType)
    if (pledgeType === 'year') {
      $('#pledge-type').html('You’ve  selected  to  make  a  one  time  donation  of <span class="accent-color">$' + pledgeAmount +'</span> .');
      $('#payment-type').html('Your  card  will  be  charged  in  this  amount.');
    } else if (pledgeType === 'month') {
      $('#pledge-type').html('You’ve  selected  to  pledge <span class="accent-color">$' + pledgeAmount +'.00 per month</span> . ');
      $('#payment-type').html('Your  card  will  be  billed  monthly  until  you  choose  to  cancel.');
    } else {
      $('#pledge-type').html('You’ve  selected  to  make  a  one  time  donation  of <span class="accent-color">$' + pledgeAmount +'</span> .');
      $('#payment-type').html('Your  card  will  be  charged  in  this  amount.');
    }
    $('#hiddenQuantityInput').val(pledgeAmount);
    $('#hiddenTypeInput').val(pledgeType);
  };

  var resetCustom = function () {
    $(yearlyCustom).val('');
    $(yearlyCustom).removeClass('active');
    $(monthlyCustom).val('');
    $(monthlyCustom).removeClass('active');
  };

  var setSelected = function (type, quantity) {
    selectedData.type = type;
    selectedData.quantity = quantity;

    if (quantity > 0) {
      updatePaymentInfo();
    } else {
      resetCustom();
    }

    checkConfirmButton()
  };

  monthlyButtons.each(function (index, el) {
    $(el).on('click', function () {
      var quantity = monthlyQuantities[index];
      resetButtons();
      resetCustom();
      $(el).addClass("active");
      setSelected('month', quantity);
    })
  });

  var yearlyButtons = $("#yearlyPledge > button");
  yearlyButtons.each(function (index, el) {
    $(el).on('click', function () {
      var quantity = yearlyQuantities[index];
      resetButtons();
      resetCustom();
      $(el).addClass("active");
      setSelected('year', quantity);
    })
  });

  var oneTimePayment = $("#oneTimePayment").find("input")[0];
  var yearlyCustom = $("#yearlyPledge").find("input")[0];
  var monthlyCustom = $("#monthlyPledge").find("input")[0];
  var yearlyCustom = $("#yearlyPledge").find("input")[0];

  $(oneTimePayment).on('keyup', function (event) {
    var value = $(oneTimePayment).val();
    if (value) {
      console.log('has value!', value);
      resetButtons();
      setSelected('one-time', value);
      $(oneTimePayment).addClass('active');
    }
  });

  $(monthlyCustom).on('keyup', function (event) {
    var value = $(monthlyCustom).val();
    if (value) {
      console.log('has value!', value);
      resetButtons();
      $(yearlyCustom).val('');
      setSelected('month', value);
      $(monthlyCustom).addClass('active');
      $(yearlyCustom).removeClass('active');
    } else {
      setSelected('', 0);
      $(monthlyCustom).removeClass('active');
    }
  });

  $(yearlyCustom).on('keyup', function (event) {
    var value = $(yearlyCustom).val();
    if (value) {
      console.log('has value!', value);
      resetButtons();
      $(monthlyCustom).val('');
      setSelected('year', value);
      $(yearlyCustom).addClass('active');
      $(monthlyCustom).removeClass('active');
    } else {
      $(yearlyCustom).removeClass('active');
      setSelected('', 0);
    }
  });

  var activeStep = function (step) {
    $(buttons[step]).addClass('active');
    $(buttons[currentStep]).removeClass('active');
  };

  // var submitForm = function () {
  //   sentHint.show();
  //   $supporterForm.trigger('submit');
  // };

  var checkConfirmButton = function () {
    if (currentStep === 1) {
      if (
        selectedData.type === 'month' && selectedData.quantity >= 10 ||
        selectedData.type === 'year' && selectedData.quantity >= 100 ||
        selectedData.type === 'one-time'
      ) {
        $(confirmButton).prop('disabled', false);
      } else {
        $(confirmButton).prop('disabled', true);
      }
    } else if (currentStep === 0) {
      $(confirmButton).prop('disabled', false);
    } else {
      $(confirmButton).prop('disabled', false);
    }

    if (currentStep === 2) {
      $(confirmButton).text('Confirm Payment');
    } else if (currentStep === 0) {
      $(confirmButton).text('Continue');
    } else {
      $(confirmButton).text('Confirm');
    }

    if (currentStep === 0) {
      $(backButton).hide();
    } else {
      $(backButton).show();
    }
  };
  var showPanel = function (step) {
    panels[step].show();
    panels[currentStep].hide();
    activeStep(step);
    currentStep = step;
    checkConfirmButton();
  };

  $('.supporter-card-data .form-control').on('keyup', function() {
    $(this).removeClass('error');

    if ($('.supporter-card-data .form-control.error').length == 0) {
      $('#form-general-error').text('');
    }
  });

  confirmButton.on('click', function () {
    if (currentStep === panels.length - 1) {

      var $inputs = $('.supporter-card-data .form-control');
      var errors = false;
      $inputs.each(function () {
        if (!$(this).val()) {
          $(this).addClass('error');
          errors = true;
        }
      });

      if (errors) {
        $('#form-general-error').text('Please correct errors above');
      }

      // submitForm();
      // TODO Disable the submit button to prevent repeated clicks
      // $form.find('#confirmButton').prop('disabled', true).addClass('disabled');
      sentHint.show();
      startStripePayment($supporterForm);
    } else {
      showPanel(currentStep + 1);
    }
  });

  backButton.on('click', function () {
    if (currentStep === 0) return;
    showPanel(currentStep - 1);
  });

  checkConfirmButton();
});
