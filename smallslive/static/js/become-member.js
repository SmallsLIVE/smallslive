$(document).ready(function () {
  if (typeof window.completeSubpage === "undefined"){
    window.completeSubpage = "";
  }

  currentStep = 'Intro';

  var selectedData = {
    type: '',
    amount: 0
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


  $(document).on('change', '.gift-content select', function () {
    /* Add a border to the display selection on dropdown change.
     */
    var $that = $(this);
    var val = $that.val();
    var $confirmSelectionButton = $('#confirmSelectionButton');
    $confirmSelectionButton.prop('disabled', val == 'none');

    if (val == 'none') {
      setSelected('', 0);
      $itemForm = null;
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
        } else if (data && data.error) {
          // go back to previous step
          $("#backButton").click();
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

  

  var buttons = $('#supporterSteps > *');
  var monthlyButtons = $("#monthlyPledge > button");
  var yearlyButtons = $("#yearlyPledge > button");
  var giftsButtons = $('.select-gift');

  var resetButtons = function () {
    [monthlyButtons, yearlyButtons, giftsButtons].forEach(function (buttons) {
      buttons.each(function (index, el) {
        $(el).removeClass("active");
      });
    })
  };

  $(document).on('change', 'input[name="payment_method"]', function(event) {
    event.stopPropagation();
    event.preventDefault();
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
    var pledgeAmount = selectedData.amount;
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
    $('#hiddenAmountInput').val(pledgeAmount);
    $('#hiddenTypeInput').val(pledgeType);
  };

  var resetCustom = function () {
    yearlyCustom = $("#yearlyCustom");
    monthlyCustom = $("#monthlyCustom");
    $(yearlyCustom).val('');
    $(yearlyCustom).removeClass('active');
    $(monthlyCustom).val('');
    $(monthlyCustom).removeClass('active');
  };




  var setSelected = function (type, amount) {
    selectedData.type = type;
    selectedData.amount = amount;
    if (amount) {
      if (amount > 0) {
        updatePaymentInfo();
      } else {
        resetCustom();
      }
    }

    checkConfirmButton()
  };
  $(document).on('click',  '#monthlyPledge > button', function () {
    $(this).on('click', function () {
      $("#monthlyPledge > button").removeClass("active");
      $(this).addClass("active");
      $('#confirmSelectionButton').prop('disabled', false);
      var amount = $(this).val()
      resetButtons();
      resetCustom();
      $(this).addClass("active");
      setSelected('month', amount);
      var $selectionConfirmationDialog = $('#selectionConfirmationDialog');
      $selectionConfirmationDialog.find('.title').text('become a supporter');
      $selectionConfirmationDialog.find('.subtitle').text('Monthly pledge');
      $selectionConfirmationDialog.find('.text').html('Thank you for choosing to help jazz music and musicians all over the world. You\'ve selected a monthly pledge of <span class="smalls-color">$'+amount+'.</span> Monthly pldeges are billed automatically and can be cancelled at any time in your Account Settings. You will recieve access to our audio/video library for as long as you are a Supporting SmallsLIVE');
      $selectionConfirmationDialog.find('.gift-content');
      $selectionConfirmationDialog.modal('show');

    })
  });

  
  $(document).on('click',  '#yearlyPledge > button', function () {
    $(this).on('click', function () {
      $("#yearlyPledge > button").removeClass("active");
      $(this).addClass("active");
      $('#confirmSelectionButton').prop('disabled', false);
      var amount = $(this).val()
      resetButtons();
      resetCustom();
      setSelected('year', amount);
      var $selectionConfirmationDialog = $('#selectionConfirmationDialog');
      $selectionConfirmationDialog.modal('show');
      $selectionConfirmationDialog.find('.title').text('become a supporter');
      $selectionConfirmationDialog.find('.subtitle').text('One time donation');
      $selectionConfirmationDialog.find('.text').html('Thank you for choosing to help jazz music and musicians all over the world. You\'ve selected a one time donation of <span class="smalls-color">$'+amount+'.</span> You will receive access to our Audio/Video Archive for the remainder of the tax year. Onetime donations are tax deductible.   ');
      $selectionConfirmationDialog.find('.gift-content');

    })
  });

  var oneTimePayment = $("#oneTimePayment").find("input")[0];
  var monthlyCustom = $("#monthlyCustom");
  var yearlyCustom = $("#yearlyCustom");


  $(monthlyCustom).on('focusout', function(){
    resetCustom()
  })

  $(yearlyCustom).on('focusout', function(){
    resetCustom()
  })

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

  $(document).on('keyup',  '#monthlyCustom', function (event) {
    monthlyCustom = $("#monthlyCustom");
    yearlyCustom = $("#yearlyCustom");
    var value = $(monthlyCustom).val();
    if (value && isPositiveInteger(value)) {
      resetButtons();
      $(yearlyCustom).val('');
      setSelected('month', value);
      $(monthlyCustom).addClass('active');
      $(yearlyCustom).removeClass('active');
      if (event.keyCode == 13) {
        var amount = $(this).val();
        if(amount > 9){
          resetButtons();
          resetCustom();
          setSelected('year', amount);
          var $selectionConfirmationDialog = $('#selectionConfirmationDialog');
          $selectionConfirmationDialog.modal('show');
          $selectionConfirmationDialog.find('.title').text('become a supporter');
          $selectionConfirmationDialog.find('.subtitle').text('Monthly pledge');
          $selectionConfirmationDialog.find('.text').html('Thank you for choosing to help jazz music and musicians all over the world. You\'ve selected a one time donation of <span class="smalls-color">$'+amount+'.</span> You will receive access to our Audio/Video Archive for the remainder of the tax year. Onetime donations are tax deductible.   ');
          $selectionConfirmationDialog.find('.gift-content');
        }
      }
    } else {
      setSelected('', 0);
      $(monthlyCustom).removeClass('active');
    }
  });

  $(document).on('keyup',  '#yearlyCustom', function (event) {
    monthlyCustom = $("#monthlyCustom");
    yearlyCustom = $("#yearlyCustom");
    var value = $(yearlyCustom).val();
    if (value && isPositiveInteger(value)) {
      resetButtons();
      $(monthlyCustom).val('');
      setSelected('year', value);
      $(yearlyCustom).addClass('active');
      $(monthlyCustom).removeClass('active');
      if (event.keyCode == 13) {
        var amount = $(this).val();
        if(amount > 99){
          resetButtons();
          resetCustom();
          setSelected('year', amount);
          var $selectionConfirmationDialog = $('#selectionConfirmationDialog');
          $selectionConfirmationDialog.modal('show');
          $selectionConfirmationDialog.find('.title').text('become a supporter');
          $selectionConfirmationDialog.find('.subtitle').text('One time donation');
          $selectionConfirmationDialog.find('.text').html('Thank you for choosing to help jazz music and musicians all over the world. You\'ve selected a one time donation of <span class="smalls-color">$'+amount+'.</span> You will receive access to our Audio/Video Archive for the remainder of the tax year. Onetime donations are tax deductible.   ');
          $selectionConfirmationDialog.find('.gift-content');
        }
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
    var $content = $('#selectionConfirmationDialog').find('#giftContent');
    $itemForm = $(this).parent().parent().parent().find('form');
    var $item = $(this).parent().parent().find('.modal-content').clone();
    var $selectionConfirmationDialog = $('#selectionConfirmationDialog');
    $selectionConfirmationDialog.find('.title').text($(this).text());
    $selectionConfirmationDialog.find('.subtitle').text('Gift Tier: ' + $(this).attr("data-type") );
    let price =  $(this).children('.price-tag').text();
    $selectionConfirmationDialog.find('.text').html('You have selected a one time, gift tier donation of <span class="smalls-color">'+price+'</span> You will receive access to ou Audio/Video Archive for the remainder of the tax year. One tima, gift-tier donations are partially tax deductible.<br> Please select your size below.');
    var $giftContent = $selectionConfirmationDialog.find('.gift-content');
    $giftContent.html($item);
    $item.removeClass('hidden');
    $selectionConfirmationDialog.find('.select').addClass('white-border-select');
    replaceWhiteSelects($giftContent[0]);
    var $select = $selectionConfirmationDialog.find('.select-items');
    var $confirmSelectionButton = $('#confirmSelectionButton');
    $confirmSelectionButton.prop('disabled', $select.length == 1);
    $selectionConfirmationDialog.modal('show');

  });

  function giftSelected(selection) {
    if ($itemForm) {
      var $input = $itemForm.find('input[name="child_id"]');
      $input.val(selection);
      setSelected('gift',  0)
    }
    $('#confirmButton').prop('disabled', false);
    $('#confirmButton').click();
  }

  var $selectionConfirmationDialog = $('#selectionConfirmationDialog');
  var $selectionConfirmationCloseButton = $selectionConfirmationDialog.find('.close-button');

  $(document).on('click',  '#confirmSelectionButton', function () {
    $('#confirmButton').show();
    $('#selectionConfirmationDialog').modal('hide');
    var $variantSelect = $selectionConfirmationDialog.find('select');
    if ($variantSelect.length != 0) {
      giftSelected($variantSelect.val());
    } else {
      giftSelected($("#single-product").val())
    }
  });
  $('#cancelSelectionButton').click(function () {
    resetButtons();
    $selectionConfirmationDialog.modal('hide');
  });
  $('.close-action').click(function () {
    $selectionConfirmationDialog.modal('hide');
    resetButtons();
  });
  $selectionConfirmationDialog.on('hidden.bs.modal', function () {
    resetButtons();
    $selectionConfirmationDialog.find('.title').empty();
    $selectionConfirmationDialog.find('.subtitle').empty();
    $selectionConfirmationDialog.find('.text').empty();
    $selectionConfirmationDialog.find('.gift-content').empty();
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
        selectedData.type === 'month' && selectedData.amount >= 10 ||
        selectedData.type === 'year' && selectedData.amount >= 100 ||
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
      $("#backButton").hide();
    } else {
      $("#backButton").show();
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

  function buttonsSizeOrder() {
    var upperButtonWidth = 0;
    $( '.select-gift' ).each(function( index ) {
      if(index > 0){
        $( this ).css('width', upperButtonWidth );
      }
      upperButtonWidth = $( this ).css('width');
      upperButtonWidth = upperButtonWidth.substring(0, upperButtonWidth.length -2);
      upperButtonWidth = parseInt(upperButtonWidth) + 100
      upperButtonWidth = upperButtonWidth + 'px'
      
    });

  }

  buttonsSizeOrder();

  $(document).on('click', '#confirmButton', function (event) {
    console.log(currentStep)
    var $that = $(this);

    if (selectedData.type == 'gift') {
      event.preventDefault();
      event.stopPropagation();
    }

    if(currentStep == 'Intro'){
      $(this).hide();
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
        $('#sentHint').show();
        if (errors) {
          $('#sentHint').hide();
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

 
  $(document).on('click', '#backButton', function () {
    if(currentStep == 'PaymentInfo'){
      $('#confirmButton').hide();
    }
 
    if(currentStep == 'SelectType'){
      $('#confirmButton').show();
    }
    if(currentStep == 'Shipping'){
      $('#confirmButton').hide();
    }
    
    if(currentStep == 'SelectType'){
      $('#confirmButton').show();
    }
    if (currentStep === 'Intro') return;
    $('#confirmButton').text('Confirm');



    showPanel(getPreviousStep());
    var $currentButton = $('.step-button.active');
    $currentButton.removeClass('active');
    $currentButton.prev().addClass('active');
  });

  checkConfirmButton();
});


