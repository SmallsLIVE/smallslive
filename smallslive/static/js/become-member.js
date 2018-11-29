$(document).ready(function () {

  var monthlyQuantities = [10, 20, 50];
  var yearlyQuantities = [100, 500, 1000];

  var panels;
  var currentStep = 'Intro';
  var backButton = $("#backButton");
  var confirmButton = $("#confirmButton");
  var sentHint = $('#sentHint');

  var selectedData = {
    type: '',
    quantity: 0
  };

  var getSteps = function () {

    var steps = ['Intro', 'SelectType'];

    if (selectedData.type == 'gift') {
      steps = steps.concat(['Shipping', 'Billing', 'Preview']);
    } else {
      steps = steps.concat(['PaymentInfo']);
    }

    steps = steps.concat(['ThankYou']);

    return steps;
  }

  var getPreviousStep = function () {
    var steps = getSteps();
    var index = steps.indexOf(currentStep);
    return steps[index - 1];
  };

  var getNextStep = function () {
    var steps = getSteps();
    var index = steps.indexOf(currentStep);
    return steps[index + 1];
  }

  var activeStep = function (step) {
    $(buttons[step]).addClass('active');
    $(buttons[currentStep]).removeClass('active');
  };

  var showPanel = function (step) {

    var $previous = $(("#supporterStep" + currentStep));
    var $step = $(("#supporterStep" + step));

    $previous.hide();
    $step.show();
    activeStep(step);
    currentStep = step;
    checkConfirmButton();
  };

  var $itemForm;


  $(document).on('change', '.store-list-item select', function () {
    /* Add a border to the display selection on dropdown change.
     */
    var $that = $(this);
    var val = $that.val();
    var $elements  = $('.store-list-item select').not(this);

    if (val != 'none') {
      $that.closest('.store-list-item').find('.select-gift').click();
      $itemForm = $that.closest('form');
    } else {
      $that.next().addClass('alert');
      setSelected('', 0);
      $itemForm = null;
    }

  });

  $(document).on('change', '.store-add-small__options', function () {
    /* Add a border to the display selection on dropdown change.
     */
    var $that = $(this);
    var val = $that.val();

    if (val != 'none') {
      setSelected('gift', 1);
      $itemForm = $that.closest('form');
      $that.next().removeClass('alert');
    } else {
      setSelected('', 0);
      $itemForm = null;
      $that.next().addClass('alert');
    }

  });

  $(document).on('submit', '.add-to-basket', function () {

    function checkout() {
      $.get('/store/checkout', function(data) {
        $('#supporterStepShipping').html(data);
        showPanel('Shipping');
        replaceWhiteSelects($('#supporterStepShipping')[0]);
      });
    }

    $.ajax({
      url: $(this).attr('action'),
      type: $(this).attr('method'),
      data: $(this).serialize(),
      success: function( data ) {
        checkout();
      },
      error: function( xhr, err ) {
        console.log(err);
      }
    });

    return false;
  });


  $(document).on('submit', '#new_shipping_address', function () {

    $.ajax({
      url: $(this).attr('action'),
      type: $(this).attr('method'),
      data: $(this).serialize(),
      success: function( data ) {
        $('#supporterStepBilling').html(data);
        showPanel('Billing');
        replaceWhiteSelects($('#supporterStepBilling')[0]);
        renderCardAnimation('#payment-form');
      },
      error: function( xhr, err ) {
        console.log(err);
      }
    });

    return false;
  });

  $(document).on('submit', '#payment-form', function () {

    $.ajax({
      url: $(this).attr('action'),
      type: $(this).attr('method'),
      data: $(this).serialize(),
      success: function( data ) {
        $('#supporterStepPreview').html(data);
        showPanel('Preview');
        $('#confirmButton').text('Place Order');
      },
      error: function( xhr, err ) {
        console.log(err);
      }
    });

    return false;
  });

  $(document).on('click', '.billing-address-toggle', function (event) {
    event.preventDefault();
    if ($(this).hasClass('active')) {
      return false;
    }
    $(this).addClass('active');
    $('.billing-address-toggle').not(this).removeClass('active');
    var $address = $('#custom-billing-address');
    $address.toggleClass('hidden');

    return false;
  });

  $(document).on('click', '.payment-method-toggle', function (event) {
    // toggle payment method buttons and forms visibility. Set input value.

    event.preventDefault();
    if ($(this).hasClass('active')) {
      return false;
    }
    $(this).addClass('active');
    $('.payment-method-toggle').not(this).removeClass('active');
    var paymentMethod = $(this).data('id');
    var selector = '#' + paymentMethod + '-form.payment-method-form';

    $(selector).removeClass('hidden');
    $('.payment-method-form').not(selector).addClass('hidden');

    // Set new value to input - payment-method
    $('#payment-method').val(paymentMethod);
    checkConfirmButton();

    return false;
  });


  $(document).on('submit', '#place-order', function () {

    $.ajax({
      url: $(this).attr('action'),
      type: $(this).attr('method'),
      data: $(this).serialize(),
      success: function( data ) {
        if (data && data.payment_url) {
          window.location = data.payment_url;
        } else if (data && data.success_url) {
          window.location = data.success_url;
        } else {
          submitComplete();
        }
      },
      error: function( xhr, err ) {
        console.log(err);
      }
    });

    return false;
  });

  function submitComplete () {

    var $supporterForm = $('#formSupporter');
    $.ajax({
      type: "POST",
      url: $supporterForm.attr('action'),
      data: $supporterForm.serialize(),
      success: function (data) {
        if(typeof completeSubpage !== "undefined"){
          notCompleteContainer.html("")
          var flowCompleteSubpage = window.subpages.get(completeSubpage);
          flowCompleteSubpage.load();
        }
        else{
          window.location = data.location
        }
      },
      error: function () {
      }
    });
  }

  if (typeof completeSubpage == "undefined") {
    var completeSubpage;
  }

  var buttons = $('#supporterSteps > *');
  var monthlyButtons = $("#monthlyPledge > button");

  var resetButtons = function () {
    [monthlyButtons, yearlyButtons].forEach(function (buttons) {
      buttons.each(function (index, el) {
        $(el).removeClass("active");
      });
    })
  };

  $(document).on('change', 'input[name="payment_method"]', function(event) {
    var $that = $(this);
    var option  = $that.attr('id');
    if (option == 'pay-credit-card') {
      $('#credit-card-form').show();
      $('#paypal-form').hide();
    } else if (option  == 'pay-paypal') {
      $('#credit-card-form').hide();
      $('#paypal-form').show();
    }

  });

  var updatePaymentInfo = function () {
    var pledgeType = selectedData.type;
    var pledgeAmount = selectedData.quantity;
    if (pledgeType === 'year') {
      $('#pledge-type').html('You’ve  selected  to  make  a  one  time  donation  of <span class="accent-color">$' + pledgeAmount +'</span> .');
      $('#payment-type').html('Your  card  will  be  charged  in  this  amount.');
      $('#select-payment-row').show();
    } else if (pledgeType === 'month') {
      $('#pledge-type').html('You’ve  selected  to  pledge <span class="accent-color">$' + pledgeAmount +'.00 per month</span> . ');
      $('#payment-type').html('Your  card  will  be  billed  monthly  until  you  choose  to  cancel.');
      // Do not show select payment section.
      $('#select-payment-row').hide();
    } else {
      $('#pledge-type').html('You’ve  selected  to  make  a  one  time  donation  of <span class="accent-color">$' + pledgeAmount +'</span> .');
      $('#payment-type').html('Your  card  will  be  charged  in  this  amount.');
      $('#select-payment-row').show();
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

    if (quantity) {
      if (quantity > 0) {
        updatePaymentInfo();
      } else {
        resetCustom();
      }
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

  function isPositiveInteger(s) {
    return /^\+?[1-9][\d]*$/.test(s);
  }
  $(oneTimePayment).on('keyup', function (event) {
    var value = $(oneTimePayment).val();
    if (value && isPositiveInteger(value)) {
      resetButtons();
      setSelected('one-time', value);
      $(oneTimePayment).addClass('active');
      if (event.keyCode == 13) {
        $('#confirmButton').click();
      }
    }
  });

  $(monthlyCustom).on('keyup', function (event) {
    var value = $(monthlyCustom).val();
    if (value && isPositiveInteger(value)) {
      resetButtons();
      $(yearlyCustom).val('');
      setSelected('month', value);
      $(monthlyCustom).addClass('active');
      $(yearlyCustom).removeClass('active');
      if (event.keyCode == 13) {
        $('#confirmButton').click();
      }
    } else {
      setSelected('', 0);
      $(monthlyCustom).removeClass('active');
    }
  });

  $(yearlyCustom).on('keyup', function (event) {
    var value = $(yearlyCustom).val();
    if (value && isPositiveInteger(value)) {
      resetButtons();
      $(monthlyCustom).val('');
      setSelected('year', value);
      $(yearlyCustom).addClass('active');
      $(monthlyCustom).removeClass('active');
      if (event.keyCode == 13) {
        $('#confirmButton').click();
      }
    } else {
      $(yearlyCustom).removeClass('active');
      setSelected('', 0);
    }
  });

  // var submitForm = function () {
  //   sentHint.show();
  //   $supporterForm.trigger('submit');
  // };

  $(document).on('click',  '.select-gift', function () {
    // fade other items and make this one active
    $('.select-gift').removeClass('active');
    $(this).addClass('active');
    $('.store-list-item .overlay').fadeIn();
    var $parent = $(this).parent();
    $parent.find('.overlay').fadeOut();
    // highlight dropdown if no option selected
    var $option = $parent.find('.same-as-selected');
    var $select = $parent.find('.select-selected');
    $('.select-selected').removeClass('alert');
    if ($option.length == 0 || $option.val() === 'none') {
      $select.addClass('alert');
      $("#confirmButton").prop('disabled', true);
    } else {
      $select.removeClass('alert');
      $("#confirmButton").prop('disabled', false);
    }
  });

  var checks = {
    '#card-number':  19, //4444 4444 4444 4444
    '#expiry-month':  2,
    '#expiry-year':  2,
    '#cvc':  3,
  };

  $(document).on('keyup', '#payment-form input', function (e) {
    checkConfirmButton();

    if (e.which > 90 || e.which < 48) {
      return;
    }

    var id = '#' + $(this).attr('id');
    var keys = Object.keys(checks);
    var pos = keys.indexOf(id);
    if (pos + 1 < keys.length && $(this).val().length  == checks[id]) {
      if (id == '#expiry-year') {
        $('#name-on-card').focus();
      } else  {
        $(keys[pos + 1]).focus();
      }
    }
  });

  function checkInput(selector,  value) {
    $input = $(selector);
    return $input.val().length === value;
  }

  function checkCreditCardForm() {
    var check = true;
    $.each(checks, function(selector, value){
      if (!checkInput(selector, value)) {
        check = false;
        return;
      }
    });

    if (!check) {
      return false;
    }

    if ($('#name-on-card').val().length === 0) {
      return false;
    }

    return true;

  }

  var checkConfirmButton = function () {

    var $confirmButton = $('#confirmButton');

    if (currentStep === 'SelectType') {
      if (
        selectedData.type === 'month' && selectedData.quantity >= 10 ||
        selectedData.type === 'year' && selectedData.quantity >= 100 ||
        selectedData.type === 'one-time' ||
        selectedData.type === 'gift'
      ) {
        $confirmButton.prop('disabled', false);
      } else {
        $confirmButton.prop('disabled', true);
      }
    } else if (currentStep === 0) {
        $confirmButton.prop('disabled', false);
    } else {
        $confirmButton.prop('disabled', false);
    }

    if (currentStep === 'PaymentInfo'  && selectedData.type != 'gift') {
        var method = $('#payment-method').val();
        if (method == 'credit-card') {
          var confirm  = checkCreditCardForm();
          $confirmButton.prop('disabled', !confirm);
        } else {
          $confirmButton.prop('disabled', false);
        }
        $confirmButton.text('Confirm Payment');
    } else {
        $confirmButton.text('Continue');
    }

    if (currentStep === 'Intro') {
      $(backButton).hide();
    } else {
      $(backButton).show();
    }
  };

  $('.supporter-card-data .form-control').on('keyup', function() {
    $(this).removeClass('error');

    if ($('.supporter-card-data .form-control.error').length == 0) {
      $('#form-general-error').text('');
    }
  });

  function getPaymentInfoForm() {

    var $step = $('#supporterStepPaymentInfo');
    var url = $step.data('payment-info-url');

    $.ajax({
      url: url,
      type: 'get',
      success: function( data ) {
        $step.html(data);
        updatePaymentInfo();
        replaceWhiteSelects($('#supporterStepPaymentInfo')[0]);
        renderCardAnimation('#payment-form');
        showPanel(getNextStep());
      },
      error: function( xhr, err ) {
        console.log(err);
      }
    });

  }

  $(document).on('click', '#confirmButton', function (event) {

    var $that = $(this);

    if (selectedData.type == 'gift') {
      event.preventDefault();
      event.stopPropagation();
    }

    if (currentStep === 'PaymentInfo') {

      var method = $('#payment-method').val();
      if (method == 'credit-card') {
        var $inputs = $('.supporter-card-data .form-control');
        var errors = false;
        $inputs.each(function () {
          if (!$(this).val()) {
            $(this).addClass('error');
            errors = true;
          }
        });
        sentHint.show();
        if (errors) {
          sentHint.hide();
          $('#form-general-error').text('Please correct errors above');
        } else {
          $that.prop('disabled', true);
          startStripePayment($('#payment-form'),
            $('#supporterStepPaymentInfo').data('payment-info-complete-url'),
            completeSubpage);
        }
      } else if (method == 'paypal') {
        $that.prop('disabled', true);
        startPayPalPayment($('#payment-form'),
          $('#supporterStepPaymentInfo').data('payment-info-complete-url'),
          completeSubpage);
      }
    } else if (currentStep === 'SelectType'  && selectedData.type == 'gift') {
      $('.step-button').removeClass('hidden');
      $itemForm.submit();
    } else if (currentStep === 'Shipping'  && selectedData.type == 'gift') {
      $('#new_shipping_address').submit();
    } else if (currentStep === 'Billing'  && selectedData.type == 'gift') {
      $('#payment-form').submit();
    } else if (currentStep === 'Preview'  && selectedData.type == 'gift') {
      $('#place-order').submit();
    } else if (currentStep === 'SelectType' && selectedData.type != 'gift') {
      getPaymentInfoForm();
    } else {
      $('.step-button.gift').addClass('hidden');
      showPanel(getNextStep());
    }

    var $currentButton = $('.step-button.active');
    $currentButton.removeClass('active');
    $currentButton.next().addClass('active');

  });

  backButton.on('click', function () {
    if (currentStep === 'Intro') return;
    $('#confirmButton').text('Confirm');
    showPanel(getPreviousStep());
    var $currentButton = $('.step-button.active');
    $currentButton.removeClass('active');
    $currentButton.prev().addClass('active');
  });

  checkConfirmButton();
});


