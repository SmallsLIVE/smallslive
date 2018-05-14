$(document).ready(function(){
  var monthlyQuantities = [10, 20, 50];
  var yearlyQuantities = [1000, 2000, 5000];

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
  $supporterForm.submit(getAjaxSubmitForForm(
    $supporterForm, [
      "type", "quantity", "card_name", "expiration_date", "credit_card_number",
      "credit_card_cvc"
    ]
  ));

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

    $('.supporterType').text(pledgeType);
    $('#supporterQuantity').text(pledgeAmount);

    $('#hiddenQuantityInput').val(pledgeAmount);
    $('#hiddenTypeInput').val(pledgeType);
  };

  var resetCustom = function () {
    $(yearlyCustom).val('');
    $(montlyCustom).val('');
  };

  var setSelected = function (type, quantity) {
    selectedData.type = type;
    selectedData.quantity = quantity;

    if (quantity > 0) {
      updatePaymentInfo();
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

  var montlyCustom = $("#monthlyPledge").find("input")[0];
  var yearlyCustom = $("#yearlyPledge").find("input")[0];
  $(montlyCustom).on('change', function (event) {
    var value = $(montlyCustom).val();
    if (value) {
      console.log('has value!', value);
      resetButtons();
      $(yearlyCustom).val('');
      setSelected('month', value);
    } else {
      setSelected('', 0);
    }
  });

  $(yearlyCustom).on('change', function (event) {
    var value = $(yearlyCustom).val();
    if (value) {
      resetButtons();
      $(montlyCustom).val('');
      setSelected('year', value);
    } else {
      setSelected('', 0);
    }
  });

  var activeStep = function (step) {
    $(buttons[step]).addClass('active');
    $(buttons[currentStep]).removeClass('active');
  };

  var submitForm = function () {
    sentHint.show();
    $supporterForm.trigger('submit');
  };

  var checkConfirmButton = function () {
    if (currentStep === 1) {
      if (selectedData.quantity > 0) {
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
    } else {
      $(confirmButton).text('Confirm');
    }
  };
  var showPanel = function (step) {
    panels[step].show();
    panels[currentStep].hide();
    activeStep(step);
    currentStep = step;
    checkConfirmButton();
  };

  confirmButton.on('click', function () {
    if (currentStep === panels.length - 1) {
      submitForm();
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
