var $mainContainer = $(document);

var selectedData = {
  flow: "",
  type: "",
  amount: 0
};

var setSelected = function(flow, type, amount, step) {

  /* flow: become a supporter or one time donation or event donation or product donation */
  /* type: store item with shipping  or store item digital or one time donation */

  selectedData.flow = flow;
  selectedData.type = type;
  selectedData.amount = amount;

  if (typeof step != "undefined") {
    currentStep = step;
  }

  if (amount) {
    if (amount > 0) {
      updatePaymentInfo();
    } else {
      resetCustom();
    }
  }
};

var currentStep = 0;

var getSteps = function() {
  /* flow and type determine the number of steps */
  /* Depending on the flow, there can be intro or not */
  /* Basically: become a supporter (monthly, one time, gift)
                one time donation (one time, gift)
                event support (one time)
                product support (catalog) (one time, gift)

     each one has different steps */

  var steps;

  if (
    selectedData.flow == "become_supporter" ||
    selectedData.flow == "one_time_donation"
  ) {
    if (selectedData.type == "store_physical") {
      steps = [
        "Intro",
        "SelectType",
        "Shipping",
        "Billing",
        "Preview",
        "ThankYou"
      ];
    } else if (selectedData.type == "year") {
      steps = ["Intro", "SelectType", "Preview", "ThankYou"];
    } else {
      steps = ["Intro", "SelectType", "Preview", "ThankYou"];
    }
  } else if (selectedData.flow == "catalog") {
    if (selectedData.type == "store_physical") {
      steps = ["SelectType", "Shipping", "Billing", "Preview", "ThankYou"];
    } else if (selectedData.type == "store_digital") {
      steps = ["SelectType", "Preview", "ThankYou"];
    } else {
      steps = ["SelectType", "Preview", "ThankYou"];
    }
  } else if (selectedData.flow == "event_sponsorship" || selectedData.flow == "donate_direct") {
    steps = ["SelectType", "Preview", "ThankYou"];
  } else if (selectedData.flow == "ticket_support") {
    steps = ["Basket", "Billing", "Preview", "ThankYou"];
  } else if (selectedData.flow == "gift_support") {
      steps = ["SelectType", "Billing", "Preview", "ThankYou"];
      if (selectedData.type == "store_physical") {
        steps = [
          "SelectType",
          "Shipping",
          "Billing",
          "Preview",
          "ThankYou"
        ];
      }
  }

  /* There needs to be one less dot than steps because the Thank You Page
  should not be counted */
  var $stepsDotsContainer = $mainContainer.find("#supporterSteps");
  if (steps.length - $stepsDotsContainer.find(".step-button").length != 1) {
    var html = "";
    for (i = 0; i < steps.length - 1; i++) {
      html += "<div class='step-button'></div>";
    }
    $stepsDotsContainer.html(html);
  }

  return steps;
};

var getPreviousStep = function() {
  var steps = getSteps();
  var index = steps.indexOf(currentStep);
  if (index == -1) {
    return steps[1];
  }
  return steps[index - 1];
};

var getNextStep = function() {
  var steps = getSteps();
  var index = steps.indexOf(currentStep);
  return steps[index + 1];
};

var monthlyButtons = $mainContainer.find("#monthlyPledge > button");
var yearlyButtons = $mainContainer.find("#yearlyPledge > button");
var giftsButtons = $mainContainer.find(".select-gift");

var resetButtons = function() {
  [monthlyButtons, yearlyButtons, giftsButtons].forEach(function(buttons) {
    buttons.each(function(index, el) {
      $(el).removeClass("active");
    });
  });
};

var activeStep = function(step) {
  var stepIndex = getSteps().indexOf(step);
  // getSteps might actually change html.
  var buttons = $mainContainer.find("#supporterSteps > *");
  $(buttons[stepIndex]).addClass("active");
  var currentStepIndex = getSteps().indexOf(currentStep);
  if (currentStepIndex > -1) {
    $(buttons[currentStepIndex]).removeClass("active");
  }
};

var showPanel = function(step) {
  var $previous = $mainContainer.find("#supporterStep" + currentStep);
  var $step = $mainContainer.find("#supporterStep" + step);

  $previous.addClass("hidden");
  $step.removeClass("hidden");
  activeStep(step);
  currentStep = step;

  var $billing = $mainContainer.find("#supporterStepBilling");
  $billing.removeClass("hidden");
  $("#yearlyCustom").val("");
  $(".custom-input label.hidden").removeClass("hidden");
  var hidden = $step.data("billing-hidden");
  if (hidden) {
    $billing.addClass(hidden);
  }

  checkConfirmButton();
};

var $itemForm;

var checks = {
    "#card-number":  {
      "length": { "default": 19, "amex": 17 } // 16 cc numbers + 3 white spaces
    },
    "#expiry-month":  {
      "length": { "default": 2 }
    },
    "#expiry-year":  {
      "length": { "default": 2 }
    },
    "#cvc":  {
      "length": { "default": 3, "amex": 4 }
    },
    /* TODO: Bankcard form. Remove for no
    "#ccv":  {
      "length": { "default": 3, "amex": 4 }
    }
    */
  };

function checkInput(selector,  value) {

  var $cardInput = $("#card-number");
  $input = $(selector);

  if ($cardInput.get(0) == $input.get(0)) {
    return $cardInput.hasClass("jp-card-valid");
  }

  // look for other check value than default
  var checkValue = null;
  var classes = $cardInput.attr("class");
  if (classes) {
    $.each(classes.split(" "), function (index, item) {
      if (value.length[item]) {
        checkValue = value.length[item];
      }
    });
  }
  if (!checkValue) {
    checkValue = value.length.default;
  }
  var length = 0;
  if ($input.val()) {
    length = $input.val().length;
  }

  return length === checkValue;
}

function checkCreditCardForm() {
  var check = true;

  // Bypassing check for now

  return true;

  $.each(checks, function(selector, value) {
    if (!checkInput(selector, value)) {
      if (selector == "#expiry-month") {
        if (parseInt($input.val()) < 13 && $input.val().trim() != "") {
          return;
        }
      }
      check = false;
      return;
    }
  });

  if (!check) {
    return false;
  }

  var $cardName = $("#name-on-card");
  if ($cardName.val().length === 0) {
    return false;
  }

  var $cardNumber = $("#card-number");
  if ($cardNumber.hasClass("jp-card-invalid")) {
    return false;
  }

  return true;
}

var checkConfirmButton = function() {
  var $confirmButton = $mainContainer.find("#confirmButton");
  var $becomeMemberButton = $mainContainer.find("#supportBecomeMemberButton");
  var $confirmEmailButton = $mainContainer.find("#supportConfirmEmailButton");

  if (currentStep === "SelectType") {
    $confirmButton.prop("disabled", false);
    $confirmButton.show();
  } else if (currentStep === 0) {
    $confirmButton.prop("disabled", false);
  } else {
    $confirmButton.prop("disabled", false);
  }

  if (currentStep === "Billing") {
    var method = $mainContainer.find("#payment-method").val();
    if (method == "credit-card") {
      var confirm = checkCreditCardForm();
      $confirmButton.prop("disabled", !confirm);
    } else {
      $confirmButton.prop("disabled", false);
    }
  } else {
    $confirmButton.text("Continue");
  }

  if (currentStep == "Preview") {
    $confirmButton.text("Confirm Payment");
  }

  if (currentStep == "Intro") {
    $mainContainer.find("#backButton").hide();
    $becomeMemberButton.show();
    $confirmEmailButton.show();
  } else {
    if (selectedData.flow == "donate_direct") {
      $mainContainer.find("#backButton").hide();
      $confirmEmailButton.show();
    } else {
      $mainContainer.find("#backButton").show();
    }
    $becomeMemberButton.hide();
    $confirmEmailButton.hide();
  }
};

var updatePaymentInfo = function() {
  var pledgeType = selectedData.type;
  var pledgeAmount = selectedData.amount;
  var $paymentSection = $mainContainer.find("#select-payment-row");

  if (pledgeType === "month") {
    $mainContainer
      .find("#pledge-type")
      .html(
        'You’ve  selected  to  pledge <span class="accent-color">$' +
          pledgeAmount +
          ".00 per month</span> . "
      );
    $mainContainer
      .find("#payment-type")
      .html(
        "Your  card  will  be  billed  monthly  until  you  choose  to  cancel."
      );
    // Show only recurring payment methods (credit cards).
    $paymentSection.find(".single").hide();
  } else {
    $mainContainer
      .find("#pledge-type")
      .html(
        'You’ve  selected  to  make  a  one  time  donation  of <span class="accent-color">$' +
          pledgeAmount +
          "</span> ."
      );
    $mainContainer
      .find("#payment-type")
      .html("Your  card  will  be  charged  in  this  amount.");
    // Show one-off payment methods
    $paymentSection.find(".single").show();
  }
  $paymentSection.show();
  $mainContainer.find("#hiddenAmountInput").val(pledgeAmount);
  $mainContainer.find("#hiddenTypeInput").val(pledgeType);
};

var resetCustom = function() {
  $yearlyCustom = $mainContainer.find("#yearlyCustom");
  $monthlyCustom = $mainContainer.find("#monthlyCustom");
  $yearlyCustom.val("");
  $yearlyCustom.removeClass("active");
  $monthlyCustom.val("");
  $monthlyCustom.removeClass("active");
  $mainContainer.find("#yearly-less").text("");
  $mainContainer.find("#monthly-less").text("");
  $mainContainer.find("#set-your-own-lbl").show();
};

var enablePaymentTypes = function (recurring) {
  $(".store__form__selection__option.payment_method").addClass("hidden");
  $(".store__form__selection__option.payment_method." + recurring).removeClass("hidden");
  var billingHidden = $(this).data("payment-options-hidden");
  var $billing = $mainContainer.find("#supporterStepBilling");
  $billing.removeClass("hidden");
  if (billingHidden) {
    $billing.addClass(billingHidden);
  }
}

var submitFormSuccess = function (data) {
   $('#content_inner').html(data.content_html);

    // Show any flash messages
    oscar.messages.clear();
    for (var level in data.messages) {
        for (var i=0; i<data.messages[level].length; i++) {
            oscar.messages[level](data.messages[level][i]);
        }
    }
    oscar.basket.is_form_being_submitted = false;
}

var submitBasketForm = function (event) {
    var payload = $('#basket_formset').serializeArray();
    $.post(oscar.basket.url, payload, submitFormSuccess, 'json');
    if (event) {
        event.preventDefault();
    }
}

var initBasketUi = function () {
    $("#content_inner").on('click', '.store-cart__quantity-control__button', function(e) {
      if (! $(this).attr('disabled')) {
        e.preventDefault();
        var $quantityInput = $(this).siblings('input[type=hidden]');
        var $quantityLabel = $(this).siblings('.store-cart__quantity-control__label');
        var quantity = parseInt($quantityInput.val(), 10);
        var behaviour = $(this).data('behaviour');
        if (behaviour === "increase") {
            quantity += 1;
            var max = parseInt($(this).data("max"));
            if (max === quantity) {
                $(this).attr('disabled', true).addClass('disabled');
                $("#content_inner .store-cart__quantity-control__button.control-decrease").attr("disabled", false).removeClass("disabled");
            }
        } else if (behaviour === "decrease") {
            quantity -= 1;
            $("#content_inner .store-cart__quantity-control__button.control-increase").attr("disabled", false).removeClass("disabled");
        }

        $quantityLabel.text(quantity);
        $quantityInput.val(quantity);
        submitBasketForm(e);
        if (quantity <= 1 && $(this).hasClass('control-decrease')) {
            $(this).attr('disabled', true).addClass('disabled');
        } else if (quantity >= 2 && $(this).hasClass('control-decrease')) {
            $(this).attr('disabled', false).removeClass('disabled');
        }
      }
    });
}

var showBasket = function (data) {
    $mainContainer.find("#supporterStepBasket").html(data);
    showPanel("Basket");
    replaceWhiteSelects(
      $mainContainer.find("#supporterStepBasket")[0]
    );
    initBasketUi();
}

var showShipping = function (data) {
  $mainContainer.find("#supporterStepShipping").html(data);
  showPanel("Shipping");
  replaceWhiteSelects(
    $mainContainer.find("#supporterStepShipping")[0]
  );
}

var showBilling = function (data) {
  if (data) {
    $mainContainer.find("#supporterStepBilling").html(data);
  }
  showPanel("Billing");
  replaceWhiteSelects(
    $mainContainer.find("#supporterStepBilling")[0]
  );
  renderCardAnimation("#payment-form");
  $("#payment-form").removeClass("hidden");

}

var checkout = function () {
  // TODO: fix hardcoded URL
  $.get("/checkout/", function (data) {
    // data.url  = 'shipping-address' and then 'shipping-method' if item is physical
    // otherwise go straight to billing.
    $.get(data.url, function(data) {
      if (data.url && data.url.indexOf("shipping-method") > -1) {
        $.get(data.url, function (data) {
          $.get(data.url, function (data) {
            $.get(data.url, function (data) {
              if (selectedData.flow == "ticket_support") {
                enablePaymentTypes("store");
                showBilling();
                $(".deferred").addClass("hidden");
              } else {
                showBilling(data);
                $(".deferred").addClass("hidden");
              }
            });
          });
        });
      } else if (data.url && data.url.indexOf("payment-method") > -1) {
        $.get(data.url, function (data) {
          $.get(data.url, function (data) {
            showBilling(data);
            $(".deferred").addClass("hidden");
          });
        });
      } else {
        showShipping(data);
      }
    });
  });
}

$(document).ready(function() {
  if (typeof window.completeSubpage === "undefined") {
    window.completeSubpage = "";
  }

  $(document).on("submit", ".add-to-basket", function(e) {
    e.preventDefault();

    $.ajax({
      url: $(this).attr("action"),
      type: $(this).attr("method"),
      data: $(this).serialize(),
      success: function(data) {
        checkout();
      },
      error: function(xhr, err) {
        console.log(err);
      }
    });

    return false;
  });

  $(document).on("click", ".select-supporter-type-toggle", function(event) {
    // toggle payment method buttons and forms visibility. Set input value.

    event.preventDefault();
    if ($(this).hasClass("active")) {
      return false;
    }

    var recurring = $(this).data("recurring");
    $(this).addClass("active");
    $(".select-supporter-type-toggle")
      .not(this)
      .removeClass("active");
    var supporterType = $(this).data("id");
    var selector = "." + supporterType + "-input.supporter-plan-input";

    $mainContainer.find(selector).removeClass("hidden");
    $mainContainer
      .find(".supporter-plan-input")
      .not(selector)
      .addClass("hidden");

    $("#payment-form").removeClass("hidden");
    $(".deferred").removeClass("hidden");

    enablePaymentTypes(recurring);

    return false;
  });

  $(document).on("submit", "#new_shipping_address", function() {
    $.ajax({
      url: $(this).attr("action"),
      type: $(this).attr("method"),
      data: $(this).serialize(),
      success: function(data) {
        if (data.url) {
          $.get(data.url, function(data) {
            $.get(data.url, function(data) {
              $.get(data.url, function(data) {
                showPanel("Billing");
                $(".deferred").addClass("hidden");
                $("#billing-information-wrapper").removeClass("hidden");
                enablePaymentTypes("store");
              });
            });
          });
        } else {
          $mainContainer.find("#supporterStepShipping").html(data);
          $mainContainer.find("#confirmButton").prop("disabled", false);
          replaceWhiteSelects($mainContainer.find("#supporterStepShipping")[0]);
        }
      },
      error: function(xhr, err) {
        console.log(err);
      }
    });

    return false;
  });

  $(document).on("submit", "#payment-form", function() {
    $.ajax({
      url: $(this).attr("action"),
      type: $(this).attr("method"),
      data: $(this).serialize(),
      success: function(data) {
        if (typeof data.success !== "undefined") {
          if (!data.success) {
            $mainContainer.find(".payment-errors").html(data.message);
          }
        } else {
          $mainContainer.find("#supporterStepPreview").html(data);
          showPanel("Preview");
          $mainContainer.find("#confirmButton").text("Confirm");
        }
      },
      error: function(xhr, err) {
        console.log(err);
      }
    });

    return false;
  });

  $(document).on("click", ".billing-address-toggle", function(event) {
    event.preventDefault();
    if ($(this).hasClass("active")) {
      return false;
    }
    $(this).addClass("active");
    $(".billing-address-toggle")
      .not(this)
      .removeClass("active");
    var $address = $mainContainer.find("#custom-billing-address");
    $address.toggleClass("hidden");

    return false;
  });

  $(document).on("click", ".payment-method-toggle", function(event) {
    // toggle payment method buttons and forms visibility. Set input value.

    event.preventDefault();
    if ($(this).hasClass("active")) {
      return false;
    }
    $(this).addClass("active");
    $(".payment-method-toggle")
      .not(this)
      .removeClass("active");
    var paymentMethod = $(this).data("id");
    var selector = "#" + paymentMethod + "-form.payment-method-form";

    $(selector).removeClass("hidden");
    $(".payment-method-form")
      .not(selector)
      .addClass("hidden");

    var showAmountHidden = $(this).data("show-amount");
    $(".donation-container").removeClass("hidden");
    if (showAmountHidden) {
        $(".donation-container").addClass(showAmountHidden);
    }

    var popup = $(this).data("show-popup");
    if (popup) {
        $("#" + popup).modal("show");
    }

    // Set new value to input - payment-method
    $("#payment-method").val(paymentMethod);
    checkConfirmButton();

    return false;
  });

  $(document).on("submit", "#place-order", function() {
    var flowType = $mainContainer.find("#supporterSteps").data("flow");
    $(this).append($('<input type="hidden" name="flow_type" />').val(flowType));
    var productId = $mainContainer.find("#supporterSteps").data("product-id");
    $(this).append(
      $('<input type="hidden" name="product_id" />').val(productId)
    );
    var eventId = $mainContainer.find("#supporterSteps").data("event-id");
    var eventSlug = $mainContainer.find("#supporterSteps").data("event-slug");
    $(this).append(
      $('<input type="hidden" name="event_id" />').val(eventId)
    );
    $(this).append(
      $('<input type="hidden" name="event_slug" />').val(eventSlug)
    );
    var artistId = $mainContainer.find("#supporterSteps").data("artist-id");
    $(this).append(
      $('<input type="hidden" name="artist_id" />').val(artistId)
    );

    $.ajax({
      url: $(this).attr("action"),
      type: $(this).attr("method"),
      data: $(this).serialize(),
      success: function(data) {
        if (data && data.payment_url) {
          window.location = data.payment_url;
        } else if (data && data.success_url) {
          window.location = data.success_url;
        } else if (data && data.error) {
          // go back to previous step
          $mainContainer.find("#backButton").click();
          $mainContainer.find(".payment-errors").html(data.error);
        } else {
          submitComplete();
        }
      },
      error: function(xhr, err) {
        console.log(err);
      }
    });

    return false;
  });

  function submitComplete() {
    var $supporterForm = $mainContainer.find("#formSupporter");
    $.ajax({
      type: "POST",
      url: $supporterForm.attr("action"),
      data: $supporterForm.serialize(),
      success: function(data) {
        if (typeof completeSubpage !== "undefined") {
          notCompleteContainer.html("");
          var flowCompleteSubpage = window.subpages.get(completeSubpage);
          flowCompleteSubpage.load();
        } else {
          window.location = data.location;
        }
      },
      error: function() {}
    });
  }

  $(document).on("change", 'input[name="payment_method"]', function(event) {
    event.stopPropagation();
    event.preventDefault();
    var $that = $(this);
    var option = $that.attr("id");
    if (option == "pay-credit-card") {
      $mainContainer.find("#credit-card-form").show();
      $mainContainer.find("#paypal-form").hide();
    } else if (option == "pay-paypal") {
      $mainContainer.find("#credit-card-form").hide();
      $mainContainer.find("#paypal-form").show();
    }
  });

  $(document).on("click", "#monthlyPledge > button", function() {
    $mainContainer.find("#monthlyPledge > button").removeClass("active");
    $(this).addClass("active");
    $mainContainer.find("#confirmSelectionButton").prop("disabled", false);
    var amount = $(this).val();
    resetButtons();
    resetCustom();
    $(this).addClass("active");
    setSelected(selectedData.flow, "month", amount);
    var $selectionConfirmationDialog = $mainContainer.find(
      "#supporterMonthlySelectionConfirmationDialog"
    );
    $selectionConfirmationDialog
      .find(".price")
      .text(amount);
    $selectionConfirmationDialog.modal("show");
  });

  $(document).on("click", "#yearlyPledge > button.donation", function() {
    $mainContainer.find("#yearlyPledge > button").removeClass("active");
    oneTimeSelected($(this));
  });

  function oneTimeSelected($element) {
    var dialogSelector = "#" + $element.closest(".pledge").data("dialog-type") + "OneTimeSelectionConfirmationDialog";
    var amount = $element.val();
    var $selectionConfirmationDialog = $mainContainer.find(dialogSelector);

    $element.addClass("active");
    $mainContainer.find("#confirmSelectionButton").prop("disabled", false);
    resetButtons();
    resetCustom();
    setSelected(selectedData.flow, "year", amount, "SelectType");
    $selectionConfirmationDialog.modal("show");
    $selectionConfirmationDialog
      .find(".price").text(amount);
  }

  $(document).on("click", "#confirmMonthlySelectionButton, #confirmOneTimeSelectionButton", function() {
    var $selectionConfirmationDialog = $(this).closest(".selectionConfirmationDialog");
    $selectionConfirmationDialog.modal("hide");
    var $confirmButton = $mainContainer.find("#confirmButton");
    $confirmButton.show();
    $confirmButton.prop("disabled", false);
    $confirmButton.click();
  });

  // Available when coming from Catalog/Support Artist
  $(document).on("click", "#supportPledge > button.donation", function() {
    $mainContainer.find("#supportPledge > button").removeClass("active");
    oneTimeSelected($(this));
  });

  /* Can't be click because button disappears on focus out from input */
  $(document).on("mousedown", ".confirm-custom", function () {
    if (selectedData.type == "month") {
      var $selectionConfirmationDialog = $mainContainer.find(
        "#supporterMonthlySelectionConfirmationDialog"
      );
      var value = $(this).data("value");
      $selectionConfirmationDialog.modal("show");
      $selectionConfirmationDialog.find(".title").text("become a supporter");
      $selectionConfirmationDialog.find(".subtitle").text("Monthly pledge");
      $selectionConfirmationDialog
        .find(".text")
        .html(
          "Thank you for choosing to help jazz music and musicians all over the world. You have selected a monthly pledge of $" +
            value +
            ". Monthly pledges are 100% tax deductible and are billed automatically. Monthly pledges may be cancelled at any time from your Account Settings. All donations grant access to the SmallsLIVE Archive."
        );
    } else {
      oneTimeSelected($(this));
    }
  });

  var oneTimePayment = $mainContainer.find("#oneTimePayment").find("input")[0];
  var monthlyCustom = $mainContainer.find("#monthlyCustom");
  var yearlyCustom = $mainContainer.find("#yearlyCustom");

  function isPositiveInteger(s) {
    return /^\+?[1-9][\d]*$/.test(s);
  }

  $(oneTimePayment).on("keyup", function(event) {
    var value = $(oneTimePayment).val();
    if (value && isPositiveInteger(value)) {
      resetButtons();
      setSelected(selectedData.flow, "one-time", value);
      $(oneTimePayment).addClass("active");
      if (event.keyCode == 13) {
        $mainContainer.find("#confirmButton").click();
      }
    }
  });

  $(document).on("keyup", "#monthlyCustom", function(event) {
    monthlyCustom = $("#monthlyCustom");
    yearlyCustom = $("#yearlyCustom");
    var value = $(monthlyCustom).val();
    var $errorLabel = $(this).closest(".button-row").find("label.accent-color");
    var $minLabel = $(this).parent().find("label");
    if (value >= 10) {
      $mainContainer.find("#set-your-own-lbl").hide();
      if (!$errorLabel.hasClass("hidden")) {
        $errorLabel.addClass("hidden");
      }
    } else {
      $mainContainer.find("#set-your-own-lbl").show();
      $errorLabel.removeClass("hidden");
    }
    if (value && isPositiveInteger(value)) {
      if (!$minLabel.hasClass("hidden")) {
        $minLabel.addClass("hidden");
      }
      resetButtons();
      $(yearlyCustom).val("");
      setSelected(selectedData.flow, "month", value);
      $(monthlyCustom).addClass("active");
      $(yearlyCustom).removeClass("active");
      if (event.keyCode == 13) {
        var amount = $(this).val();
        if (amount >= 10) {
          resetButtons();
          resetCustom();
          setSelected(selectedData.flow, "month", amount);
          var $selectionConfirmationDialog = $mainContainer.find(
            "#supporterMonthlySelectionConfirmationDialog"
          );
          $selectionConfirmationDialog.modal("show");
          $selectionConfirmationDialog
            .find(".price").text(amount);
        }
      }
    } else {
      $minLabel.removeClass("hidden");
      setSelected(selectedData.flow, "", 0);
      $(monthlyCustom).removeClass("active");
    }
  });

  $(document).on("keydown", "#yearlyCustom, #monthlyCustom", function (event) {
    if (event.which == 190) {
      return false;
    }
  });

  $(document).on("keyup", "#yearlyCustom", function(event) {
    console.log(event);

    $monthlyCustom = $mainContainer.find("#monthlyCustom");
    $yearlyCustom = $(this);
    var value = $yearlyCustom.val();
    var min = $yearlyCustom.data("min-donation");
    if (!min) {
        min = 10;
    } else {
        min = parseInt(min);
    }
    var $minErrorLabel = $(this).closest(".button-row").find("label.accent-color.min");
    var $maxErrorLabel = $(this).closest(".button-row").find("label.accent-color.max");
    var $minLabel = $(this).parent().find("label");
    if (value && isPositiveInteger(value)) {
      if (!$minLabel.hasClass("hidden")) {
        $minLabel.addClass("hidden");
      }
      resetButtons();
      $monthlyCustom.val("");
      setSelected(selectedData.flow, "year", value);
      $yearlyCustom.addClass("active");
      $monthlyCustom.removeClass("active");
      if (value >= min) {
        if (!$minErrorLabel.hasClass("hidden")) {
          $minErrorLabel.addClass("hidden");
        }
      } else {
        $minErrorLabel.removeClass("hidden");
      }
      if (value > 99999) {
        $maxErrorLabel.removeClass("hidden");
      } else {
        if (!$maxErrorLabel.hasClass("hidden")) {
          $maxErrorLabel.addClass("hidden");
        }
      }
    } else {
      $minLabel.removeClass("hidden");
      $yearlyCustom.removeClass("active");
      setSelected(selectedData.flow, "", 0);
    }
    checkConfirmButton();
  });

  // var submitForm = function () {
  //   sentHint.show();
  //   $supporterForm.trigger('submit');
  // };

  $(document).on("click", ".select-gift", function() {
    // fade other items and make this one active
    $(".select-gift").removeClass("active");
    $(this).addClass("active");
    $(".store-list-item .overlay").fadeIn();
    var $parent = $(this).parent();
    $parent.find(".overlay").fadeOut();
    // highlight dropdown if no option selected
    var $option = $parent.find(".same-as-selected");
    var $select = $parent.find(".select-selected");
    $(".select-selected").removeClass("alert");
    if ($option.length == 0 || $option.val() === "none") {
      $select.addClass("alert");
      $mainContainer.find("#confirmButton").prop("disabled", true);
    } else {
      $select.removeClass("alert");
      $mainContainer.find("#confirmButton").prop("disabled", false);
    }
    $itemForm = $(this)
      .parent()
      .parent()
      .parent()
      .find("form");
    var $item = $(this)
      .parent()
      .parent()
      .find(".modal-content")
      .clone();

    var dialogSelector = "#" + $(this).closest("#gift").data("dialog-type")  + "GiftSelectionConfirmationDialog";
    var $selectionConfirmationDialog = $mainContainer.find(dialogSelector);
    $selectionConfirmationDialog.find(".title").text($(this).find(".gift-title").text());
    var giftTier = $(this).attr("data-type");
    var giftDescription = $(this).attr("data-description");
    var hasVariants =
      $(this).data("variants") && $(this).data("variants") != "0";
    $selectionConfirmationDialog
      .find(".subtitle")
      .text($(this).find(".price-tag").text());
    var price = $(this)
      .children(".price-tag")
      .text();

    var cost = $(this).attr("data-cost");
    if (!cost) {
      var $variants = $(this).closest('.gifts-container').find('.variant-data');
      var cost = $variants.attr('data-cost');
    }

    var tax = 0;
    var priceInt = parseInt(price.substring(1).replace(/,/g, ""));
    if (cost && cost != "None" && cost != "0.00") {
      tax = "$" + (priceInt - parseInt(cost)).toFixed(2).toString();
    } else if (cost == "None" || cost == "0.00") {
      tax = "100%";
    }

    var hasLibraryAccess = $itemForm.data("has-library-access") === "True";
    var $content = $selectionConfirmationDialog.find(".text");
    $content.find(".price").text(price);
    $content.find(".tax").text(tax);
    $content.find(".gift-tier").text(giftTier);
    if (giftDescription) {
      $selectionConfirmationDialog.find(".description").html(giftDescription).show();
    } else {
      $selectionConfirmationDialog.find(".description").hide();
    }
    if (hasVariants) {
      $selectionConfirmationDialog.find(".variants").show();
    }  else {
      $selectionConfirmationDialog.find(".variants").hide();
    }
    if (hasLibraryAccess) {
      $("#library-notice").show();
    } else {
      $("#library-notice").hide();
    }
    var $giftContent = $selectionConfirmationDialog.find(".gift-content");
    $giftContent.html($item);
    $item.removeClass("hidden");
    $selectionConfirmationDialog
      .find(".select")
      .addClass("white-border-select");
    replaceWhiteSelects($giftContent[0]);
    var $select = $selectionConfirmationDialog.find(".select-items");
    var $confirmSelectionButton = $("#confirmGiftSelectionButton");
    $confirmSelectionButton.prop("disabled", $select.length == 1);
    $selectionConfirmationDialog.modal("show");
  });

  $(document).on("change", ".gift-content select", function() {
    /* Add a border to the display selection on dropdown change.
     */
    var $that = $(this);
    var val = $that.val();
    var $confirmSelectionButton = $mainContainer.find(
      "#confirmGiftSelectionButton"
    );
    $confirmSelectionButton.prop("disabled", val == "none");

    if (val == "none") {
      setSelected(selectedData.flow, "", 0);
      $itemForm = null;
    }
  });

  $(document).on("click", "#confirmGiftSelectionButton", function() {

    var $selectionConfirmationDialog = $(this).closest(".selectionConfirmationDialog");
    $selectionConfirmationDialog.modal("hide");
    $mainContainer.find("#confirmButton").show();

    var $variantSelect = $selectionConfirmationDialog.find("select");

    if ($itemForm) {
      var requiresShipping = $itemForm.data("requires-shipping") == "True";
      if ($variantSelect.length != 0) {
        giftSelected($variantSelect.val(), requiresShipping);
      } else {
        giftSelected(null, requiresShipping);
      }
    }
    $selectionConfirmationDialog.modal("hide");
    $mainContainer.find("#confirmButton").prop("disabled", false);
    $mainContainer.find("#confirmButton").click();
  });

  function giftSelected(selection, requiresShipping) {
    // Amount = passed to setSelected. It's irrelevant because
    // amount will be passed to the store backend through the form $itemForm
    var store = "store_digital";
    if (requiresShipping) {
      store = "store_physical";
    }
    setSelected(selectedData.flow, store, 0);
    if (selection) {
      var $input = $itemForm.find('input[name="child_id"]');
      $input.val(selection);
    }
  }

  var $selectionConfirmationDialog = $("#selectionConfirmationDialog");
  var $selectionConfirmationCloseButton = $selectionConfirmationDialog.find(
    ".close-button"
  );


  $(document).on("click", "#cancelSelectionButton", function() {
    resetButtons();
    $mainContainer.find("#selectionConfirmationDialog").modal("hide");
  });
  $(".close-action").click(function() {
    $selectionConfirmationDialog.modal("hide");
    resetButtons();
  });
  $selectionConfirmationDialog.on("hidden.bs.modal", function() {
    resetButtons();
    $selectionConfirmationDialog.find(".title").empty();
    $selectionConfirmationDialog.find(".subtitle").empty();
    $selectionConfirmationDialog.find(".text").empty();
    $selectionConfirmationDialog.find(".gift-content").empty();
  });

  var checksFlow = {
    "#card-number": 19, //4444 4444 4444 4444
    "#expiry-month": 2,
    "#expiry-year": 2,
    "#cvc": 3
  };

  $(document).on("keyup", "#payment-form input", function(e) {
    flowKind = $("#supporterSteps").data("flow");
    checkConfirmButton();

    if (e.which > 90 || e.which < 48) {
      return;
    }

    var id = "#" + $(this).attr("id");
    var keys = Object.keys(checksFlow);
    var pos = keys.indexOf(id);
    if (pos + 1 < keys.length && $(this).val().length == checksFlow[id]) {
      if (id == "#expiry-year") {
        $("#name-on-card").focus();
      } else {
        $(keys[pos + 1]).focus();
      }
    }
  });
  $(".store__form__input").on("keyup", function() {
    $(this).removeClass("error");
    $("#form-general-error").text("");
    checkConfirmButton();
  });

  function getPaymentInfoForm() {
    var $billing = $mainContainer.find("#supporterStepBilling");
    var url = $billing.data("payment-info-url");

    $.ajax({
      url: url,
      type: "get",
      success: function(data) {
        $billing.removeClass("hidden");
        updatePaymentInfo();
        renderCardAnimation("#payment-form");
        showPanel(getNextStep());
      },
      error: function(xhr, err) {
        console.log(err);
      }
    });
  }

  function processPayPalCreditCardPayment() {
    var $form = $mainContainer.find("#payment-form");

    $form.append(
      $('<input type="hidden" name="amount" />').val(selectedData.amount)
    );

    // Bankcard form has different input for year
    var expiryYear = $('#expiry-year-placeholder').val();
    expiryYear = "20" + expiryYear;
    $('#expiry-year').val(expiryYear);

    var $form = $('#payment-form');

    // Fix single digit
    if ($('#expiry-month').val() < 10 && !$('#expiry-month').val().startsWith('0')) {
      $('#expiry-month').val('0' + $('#expiry-month').val());
    }

    $.ajax({
      type: "POST",
      url: $form.attr("action"),
      data: $form.serialize(),
      success: function(data) {
        if (data.errors) {
          var errors = '';
          for (var key in data.errors) {
            errors += ' '  + data.errors[key];
          }
          $mainContainer.find("#sentHint").hide();
          $mainContainer
            .find("#form-general-error")
            .text("Please correct errors: " + errors);
          $("#backButton").click();
        } else {
          window.location = data.location;
        }
      },
      error: function() {
        $mainContainer.find("#sentHint").hide();
        $mainContainer
          .find("#form-general-error")
          .text("Unknown error please contact support");
        $("#backButton").click();
      }
    });
  }

  function processPaymentInfoStep() {
    var method = $mainContainer.find("#payment-method").val();
    if (method == "credit-card") {
      var $inputs = $(".supporter-card-data .form-control");
      var errors = false;
      $inputs.each(function() {
        if (!$(this).val()) {
          $(this).addClass("error");
          errors = true;
        }
      });
      $mainContainer.find("#sentHint").show();
      if (errors) {
        $mainContainer.find("#sentHint").hide();
        $mainContainer
          .find("#form-general-error")
          .text("Please correct errors above");
        $("#backButton").click();
      } else {
        startStripePayment(
          $mainContainer.find("#payment-form"),
          $mainContainer
            .find("#supporterStepBilling")
            .data("payment-info-complete-url"),
          completeSubpage
        );
      }
    } else if (method == "paypal") {
      startPayPalPayment(
        $mainContainer.find("#payment-form"),
        $mainContainer
          .find("#supporterStepBilling")
          .data("payment-info-complete-url"),
        completeSubpage
      );
    } else if (method == "bitcoin") {
      startBitCoinPayment(
        $mainContainer.find("#payment-form"),
        $mainContainer
          .find("#supporterStepBilling")
          .data("payment-info-pending-url"),
        completeSubpage
      );
    } else if (method == "check") {
      startCheckPayment(
        $mainContainer.find("#payment-form"),
        $mainContainer
          .find("#supporterStepBilling")
          .data("payment-info-pending-url"),
        completeSubpage
      );
    } else if (method == "existing-credit-card") {
      startStripePayment(
        $("#payment-form"),
        $mainContainer
          .find("#supporterStepBilling")
          .data("payment-info-complete-url"),
        completeSubpage
      );
    } else if (method == "paypal-credit-card") {
      processPayPalCreditCardPayment();
    }
  }

  function getBillingFormValues() {
    var $billingForm = $mainContainer.find("#custom-billing-address .address");
    var data = $billingForm.serialize();

    return  data;
  }

  function getDonationPreviewForm() {
    var $step = $mainContainer.find("#supporterStepPreview");
    var url = $step.data("donation-preview-url");
    url = url + "?type=" + selectedData.type + "&amount=" + selectedData.amount;
    url += "&payment_method=" + $("#payment-method").val();
    url += "&" + getBillingFormValues();
    var cardNumber = $("#card-number").val();
    if (cardNumber) {
      url += "&last=" + cardNumber.substr(cardNumber.length - 4);
    }
    $.ajax({
      url: url,
      type: "get",
      success: function(data) {
        $step.html(data);
        replaceWhiteSelects($("#supporterStepPreview")[0]);
        showPanel(getNextStep());
      },
      error: function(xhr, err) {
        console.log(err);
      }
    });
  }

  $(document).on("click", "#confirmButton", function(event) {

//    alert('as dfasdfasd');
    console.log(currentStep);

    var min = $(this).attr("data-min-donation");
    if (min) {
        min = parseInt(min);
    } else {
        min = 10;
    }

    if (currentStep === "SelectType") {
      // We're combining CC info and payment for One Time Donations
      var amount = selectedData.amount;
      var donationType = selectedData.type;
      if (amount < min && donationType != "store_physical" && donationType != "store_digital") {
        alert('Please enter amount greater than $' + min);
        return;
      }
    }

    var $that = $(this);
    $that.prop("disabled", true);

    if (selectedData.flow == "store") {
      event.preventDefault();
      event.stopPropagation();
    }

    if (currentStep == "Intro") {
      $(this).hide();
    }

    var storeItem = null;
    if (selectedData.type) {
      storeItem = selectedData.type.indexOf("store") === 0;
    }

    if (storeItem) {
      if (currentStep === "SelectType" || currentStep == "Basket") {
        if (currentStep == "Basket") {
            checkout();
        } else {
            $itemForm.submit();
        }
      } else if (currentStep === "Shipping") {
        $mainContainer.find("#new_shipping_address").submit();
      } else if (currentStep === "Billing") {
        $mainContainer.find("#payment-form").submit();
      } else if (currentStep === "Preview") {
        $mainContainer.find("#place-order").submit();
      }
    } else {
      if (currentStep == "Intro") {
        getPaymentInfoForm();
      } else if (currentStep === "SelectType") {
        // We're combining CC info and payment for One Time Donations
        getDonationPreviewForm();
      } else if (currentStep === "Billing") {
        getDonationPreviewForm();
      } else if (currentStep == "Preview") {
        processPaymentInfoStep();
      } else {
        showPanel(getNextStep());
      }
    }
  });

  $(document).on("click", "#backButton", function() {

    if (currentStep == "SelectType" &&
        (window.location.href.indexOf("event-support") > -1 ||
          window.location.href.indexOf("artist-support") > -1 ||
            window.location.href.indexOf("product-support") > -1 ||
              window.location.href.indexOf("event-sponsorship") > -1)) {
      window.history.back();
      return;
    }

    if (currentStep === "Intro") return;

    if (currentStep === "Billing") {
      if (currentStep === "Billing") {
        if (!$(".gift-input.supporter-plan-input").hasClass("hidden")) {
          $("#payment-form").addClass("hidden");
          $(".deferred").addClass("hidden");
        } else {
          $("#payment-form").removeClass("hidden");
          $(".deferred").addClass("hidden");

        }
      }
    }

    if (!getSteps().indexOf(currentStep) < 1) {
      showPanel(getPreviousStep());
    } else {
      var action = $(this).data("back-action");
      if (action) {
        eval(action)(selectedData.flow);
      }
    }

    if (currentStep === "SelectType") {
      setSelected(selectedData.flow, null, null)
      $itemForm = null;

      if($('.become-supporter-donate-select').length) {
        // Set selected amount on clicking the back button.
        var selectedType = $('.become-supporter-donate-select .select-items .same-as-selected').attr('value');
        if(selectedType == 'year') {
          setSelected(selectedData.flow, "year", 100);
        } else if(selectedType == 'month') {
          setSelected(selectedData.flow, "month", 10);
        }
      }
    } else {
      $mainContainer.find("#confirmButton").show();
    }

    $mainContainer.find("#confirmButton").text("Continue");

  });

  function hideFlow(flowType) {
    $(".album.big-player").removeClass("hidden");
    $("#my-downloads-product__support").addClass('hidden');
    $(".store-banner").removeClass("hidden");
    $(".white-line-bottom").removeClass("hidden");
    $(".newest-recordings-container.downloads").removeClass("hidden");
  }

  function goBack(flowType) {
    window.history.back();
  }

});
