var $mainContainer = $(document);

var selectedData = {
  flow: "",
  type: "",
  amount: 0
};

var setSelected = function(flow, type, amount, step) {
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
  var steps;

  if (
    selectedData.flow == "become_supporter" ||
    selectedData.flow == "one_time_donation"
  ) {
    if (selectedData.type == "store") {
      steps = [
        "Intro",
        "SelectType",
        "Shipping",
        "Billing",
        "Preview",
        "ThankYou"
      ];
    } else {
      steps = ["Intro", "SelectType", "PaymentInfo", "ThankYou"];
    }
  } else if (selectedData.flow == "catalog") {
    if (selectedData.type == "store") {
      steps = ["Shipping", "Billing", "Preview", "ThankYou"];
    } else {
      steps = ["SelectType", "PaymentInfo", "ThankYou"];
    }
  } else if (
    selectedData.flow == "event_support" ||
    selectedData.flow == "product_support"
  ) {
    steps = ["SelectType", "PaymentInfo", "ThankYou"];
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

var buttons = $mainContainer.find("#supporterSteps > *");
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
  $(buttons[step]).addClass("active");
  $(buttons[currentStep]).removeClass("active");
};

var showPanel = function(step) {
  var $previous = $mainContainer.find("#supporterStep" + currentStep);
  var $step = $mainContainer.find("#supporterStep" + step);

  $previous.hide();
  $step.show();
  activeStep(step);
  currentStep = step;

  checkConfirmButton();
};

var $itemForm;

function checkCreditCardForm() {
  var check = true;
  $.each(checks, function(selector, value) {
    if (!checkInput(selector, value)) {
      if (selector == "#expiry-month") {
        if (parseInt($input.val()) < 13 && $input.val().trim() != "") {
          return;
        }
      }
      console.log("No " + selector);
      check = false;
      return;
    }
  });

  if (!check) {
    return false;
  }

  if ($("#name-on-card").val().length === 0) {
    return false;
  }

  return true;
}

var checkConfirmButton = function() {
  var $confirmButton = $mainContainer.find("#confirmButton");

  if (currentStep === "SelectType") {
    if (
      (selectedData.type === "month" && selectedData.amount >= 10) ||
      (selectedData.type === "year" && selectedData.amount >= 100) ||
      (selectedData.flow !== "become_supporter" && selectedData.amount > 0)
    ) {
      $confirmButton.prop("disabled", false);
    } else {
      $confirmButton.prop("disabled", true);
    }
  } else if (currentStep === 0) {
    $confirmButton.prop("disabled", false);
  } else {
    $confirmButton.prop("disabled", false);
  }

  if (currentStep === "PaymentInfo") {
    var method = $mainContainer.find("#payment-method").val();
    if (method == "credit-card") {
      var confirm = checkCreditCardForm();
      $confirmButton.prop("disabled", !confirm);
    } else {
      $confirmButton.prop("disabled", false);
    }
    $confirmButton.text("Confirm Payment");
  } else {
    $confirmButton.text("Continue");
  }

  if (getSteps().indexOf(currentStep) < 1) {
    $mainContainer.find("#backButton").hide();
  } else {
    $mainContainer.find("#backButton").show();
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
  $mainContainer.find("#yearlyCustomConfirm").hide();
  $mainContainer.find("#monthlyCustomConfirm").hide();
};

$(document).ready(function() {
  if (typeof window.completeSubpage === "undefined") {
    window.completeSubpage = "";
  }

  $(document).on("change", ".gift-content select", function() {
    /* Add a border to the display selection on dropdown change.
     */
    var $that = $(this);
    var val = $that.val();
    var $confirmSelectionButton = $mainContainer.find(
      "#confirmSelectionButton"
    );
    $confirmSelectionButton.prop("disabled", val == "none");

    if (val == "none") {
      setSelected(selectedData.flow, "", 0);
      $itemForm = null;
    }
  });

  $(document).on("submit", ".add-to-basket", function(e) {
    e.preventDefault();

    function checkout() {
      // TODO: fix hardcoded URL
      $.get("/store/checkout/", function(data) {
        $.get(data.url, function(data) {
          if (data.url && data.url.indexOf("payment-method") > -1) {
            $.get(data.url, function(data) {
              $.get(data.url, function(data) {
                $mainContainer.find("#supporterStepBilling").html(data);
                showPanel("Billing");
                replaceWhiteSelects(
                  $mainContainer.find("#supporterStepBilling")[0]
                );
                renderCardAnimation("#payment-form");
              });
            });
          } else {
            $mainContainer.find("#supporterStepShipping").html(data);
            showPanel("Shipping");
            replaceWhiteSelects(
              $mainContainer.find("#supporterStepShipping")[0]
            );
          }
        });
      });
    }

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
    $(this).addClass("active");
    $(".select-supporter-type-toggle")
      .not(this)
      .removeClass("active");
    var supporterType = $(this).data("id");
    var selector = "#" + supporterType + "-input.supporter-plan-input";

    $mainContainer.find(selector).removeClass("hidden");
    $mainContainer
      .find(".supporter-plan-input")
      .not(selector)
      .addClass("hidden");

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
                $mainContainer.find("#supporterStepBilling").html(data);
                showPanel("Billing");
                replaceWhiteSelects(
                  $mainContainer.find("#supporterStepBilling")[0]
                );
                renderCardAnimation("#payment-form");
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
        $mainContainer.find("#supporterStepPreview").html(data);
        showPanel("Preview");
        $mainContainer.find("#confirmButton").text("Confirm");
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
      "#selectionConfirmationDialog"
    );
    $selectionConfirmationDialog.find(".title").text("become a supporter");
    $selectionConfirmationDialog.find(".subtitle").text("Monthly pledge");
    $selectionConfirmationDialog
      .find(".text")
      .html(
        "You have selected a monthly pledge of $" +
          amount +
          ". Monthly pledges are 100% tax deductible and are billed automatically. Monthly pledges may be cancelled at any time from your Account Settings. You will receive access to The SmallsLIVE Archive for as long as you are a Supporting Member of The SmallsLIVE Foundation."
      );
    $selectionConfirmationDialog.find(".gift-content");
    $selectionConfirmationDialog.modal("show");
  });

  function oneTimeSelected($element) {
    var amount = $element.val();
    var $selectionConfirmationDialog = $mainContainer.find(
      "#selectionConfirmationDialog"
    );

    $element.addClass("active");
    $mainContainer.find("#confirmSelectionButton").prop("disabled", false);
    resetButtons();
    resetCustom();
    setSelected(selectedData.flow, "year", amount, "SelectType");
    $selectionConfirmationDialog.modal("show");
    $selectionConfirmationDialog.find(".title").text("support artist");
    $selectionConfirmationDialog.find(".subtitle").text("One time donation");
    $selectionConfirmationDialog
      .find(".text")
      .html(
        "You have selected a One Time Donation of $" +
          amount +
          ". One Time Donations are 100% tax deductible. All tax documents are available from your Account Settings. You will receive access to The SmallsLIVE Archive for the remainder of the tax year."
      );
  }

  $(document).on("click", "#yearlyPledge > button", function() {
    $mainContainer.find("#yearlyPledge > button").removeClass("active");
    oneTimeSelected($(this));
    $selectionConfirmationDialog.find(".gift-content");
  });

  // Available when coming from Catalog/Support Artist
  $(document).on("click", "#supportPledge > button", function() {
    $mainContainer.find("#supportPledge > button").removeClass("active");
    oneTimeSelected($(this));
  });

  /* Can't be click because button disappears on focus out from input */
  $(document).on("mousedown", ".confirm-custom", function() {
    if (selectedData.type == "month") {
      var $selectionConfirmationDialog = $mainContainer.find(
        "#selectionConfirmationDialog"
      );
      $selectionConfirmationDialog.modal("show");
      $selectionConfirmationDialog.find(".title").text("become a supporter");
      $selectionConfirmationDialog.find(".subtitle").text("Monthly pledge");
      $selectionConfirmationDialog
        .find(".text")
        .html(
          "Thank you for choosing to help jazz music and musicians all over the world. You have selected a monthly pledge of $" +
            $value +
            ". Monthly pledges are 100% tax deductible and are billed automatically. Monthly pledges may be cancelled at any time from your Account Settings. You will receive access to The SmallsLIVE Archive for as long as you are a Supporting Member of The SmallsLIVE Foundation."
        );
    } else {
      oneTimeSelected($(this));
    }
  });

  var oneTimePayment = $mainContainer.find("#oneTimePayment").find("input")[0];
  var monthlyCustom = $mainContainer.find("#monthlyCustom");
  var yearlyCustom = $mainContainer.find("#yearlyCustom");

  $(document).on("focusout", ".custom-out", function() {
    resetCustom();
  });

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
    if (value > 9) {
      $mainContainer.find("#monthlyCustomConfirm").data("value", value);
      $mainContainer.find("#monthlyCustomConfirm").show();
    } else {
      $mainContainer.find("#monthlyCustomConfirm").data("value", "");
      $mainContainer.find("#monthlyCustomConfirm").hide();
    }
    if (value && isPositiveInteger(value)) {
      resetButtons();
      $(yearlyCustom).val("");
      setSelected(selectedData.flow, "month", value);
      $(monthlyCustom).addClass("active");
      $(yearlyCustom).removeClass("active");
      if (event.keyCode == 13) {
        var amount = $(this).val();
        if (amount > 9) {
          resetButtons();
          resetCustom();
          setSelected(selectedData.flow, "year", amount);
          var $selectionConfirmationDialog = $mainContainer.find(
            "#selectionConfirmationDialog"
          );
          $selectionConfirmationDialog.modal("show");
          $selectionConfirmationDialog
            .find(".title")
            .text("become a supporter");
          $selectionConfirmationDialog.find(".subtitle").text("Monthly pledge");
          $selectionConfirmationDialog
            .find(".text")
            .html(
              "You have selected a monthly pledge of $" +
                amount +
                ". Monthly pledges are 100% tax deductible and are billed automatically. Monthly pledges may be cancelled at any time from your Account Settings. You will receive access to The SmallsLIVE Archive for as long as you are a Supporting Member of The SmallsLIVE Foundation."
            );
          $selectionConfirmationDialog.find(".gift-content");
        } else {
          $("#monthly-less").text("The minimun monthly pledge is $10 dolars");
        }
      }
    } else {
      setSelected(selectedData.flow, "", 0);
      $(monthlyCustom).removeClass("active");
    }
  });

  $(document).on("keyup", "#yearlyCustom", function(event) {
    $monthlyCustom = $mainContainer.find("#monthlyCustom");
    $yearlyCustom = $(this);
    var value = $yearlyCustom.val();

    if (value && isPositiveInteger(value)) {
      resetButtons();
      $monthlyCustom.val("");
      setSelected(selectedData.flow, "year", value);
      $yearlyCustom.addClass("active");
      $monthlyCustom.removeClass("active");
      if (value >= 100 || selectedData.flow !== "become_supporter") {
        $mainContainer.find("#yearlyCustomConfirm").val(value);
        $mainContainer.find("#yearlyCustomConfirm").show();
      } else {
        $mainContainer.find("#yearlyCustomConfirm").val("");
        $mainContainer.find("#yearlyCustomConfirm").hide();
      }
      if (event.keyCode == 13) {
        if ($mainContainer.find("#yearlyCustomConfirm").val() != "") {
          oneTimeSelected($yearlyCustom);
        }
      }
    } else {
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
    var $selectionConfirmationDialog = $mainContainer.find(
      "#selectionConfirmationDialog"
    );
    $selectionConfirmationDialog.find(".title").text($(this).text());
    var giftTier = $(this).attr("data-type");
    var hasVariants =
      $(this).data("variants") && $(this).data("variants") != "0";
    $selectionConfirmationDialog
      .find(".subtitle")
      .text("Gift Tier: " + giftTier);
    let price = $(this)
      .children(".price-tag")
      .text();
    let cost = $(this).attr("data-cost");

    var tax = 0;
    var priceInt = parseInt(price.substring(1).replace(/,/g, ""));
    console.log("COST");
    console.log(cost);
    if (cost && cost != "None" && cost != "0.00") {
      tax = "$ " + (priceInt - parseInt(cost)).toFixed(2).toString();
    } else if (cost == "None" || cost == "0.00") {
      tax = "100%";
    }
    var content =
      'You have selected a one time donation of <span class="smalls-color">' +
      price +
      '</span>  of which <span class="smalls-color"> ' +
      tax +
      "</span> is tax deductible. You will receive access to The SmallsLIVE Archive for the remainder of the tax year. You have also chosen to receive a " +
      giftTier +
      " as a gift for your contribution.";
    if (hasVariants) {
      content = content + "<br> Please select an option below.";
    }
    $selectionConfirmationDialog.find(".text").html(content);

    var $giftContent = $selectionConfirmationDialog.find(".gift-content");
    $giftContent.html($item);
    $item.removeClass("hidden");
    $selectionConfirmationDialog
      .find(".select")
      .addClass("white-border-select");
    replaceWhiteSelects($giftContent[0]);
    var $select = $selectionConfirmationDialog.find(".select-items");
    var $confirmSelectionButton = $("#confirmSelectionButton");
    $confirmSelectionButton.prop("disabled", $select.length == 1);
    $selectionConfirmationDialog.modal("show");
  });

  function giftSelected(selection) {
    // Amount = passed to setSelected. It's irrelevant because
    // amount will be passed to the store backend through the form $itemForm
    setSelected(selectedData.flow, "store", 0);
    if (selection) {
      var $input = $itemForm.find('input[name="child_id"]');
      $input.val(selection);
    }
  }

  var $selectionConfirmationDialog = $("#selectionConfirmationDialog");
  var $selectionConfirmationCloseButton = $selectionConfirmationDialog.find(
    ".close-button"
  );

  $(document).on("click", "#confirmSelectionButton", function() {
    $mainContainer.find("#confirmButton").show();
    $mainContainer.find("#selectionConfirmationDialog").modal("hide");
    var $variantSelect = $selectionConfirmationDialog.find("select");

    if ($itemForm) {
      if ($variantSelect.length != 0) {
        giftSelected($variantSelect.val());
      } else {
        giftSelected();
      }
    }
    $mainContainer.find("#confirmButton").prop("disabled", false);
    $mainContainer.find("#confirmButton").click();
  });

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

  var checks = {
    "#card-number": 19, //4444 4444 4444 4444
    "#expiry-year": 2,
    "#cvc": 3,
    "#expiry-month": 2
  };
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

  function checkInput(selector, value) {
    $input = $(selector);
    return $input.val().length === value;
  }

  $(".supporter-card-data .form-control").on("keyup", function() {
    $(this).removeClass("error");

    if ($(".supporter-card-data .form-control.error").length == 0) {
      $("#form-general-error").text("");
    }
  });

  function getPaymentInfoForm() {
    var $step = $mainContainer.find("#supporterStepPaymentInfo");
    var url = $step.data("payment-info-url");

    $.ajax({
      url: url,
      type: "get",
      success: function(data) {
        $step.html(data);
        updatePaymentInfo();
        replaceWhiteSelects($("#supporterStepPaymentInfo")[0]);
        renderCardAnimation("#payment-form");
        showPanel(getNextStep());
      },
      error: function(xhr, err) {
        console.log(err);
      }
    });
  }

  function buttonsSizeOrder() {
    if (document.body.clientWidth > 768) {
      var upperButtonWidth = 0;
      $(".select-gift").each(function(index) {
        if (index > 0) {
          $(this).css("width", upperButtonWidth);
        }
        upperButtonWidth = $(this).css("width");
        upperButtonWidth = upperButtonWidth.substring(
          0,
          upperButtonWidth.length - 2
        );
        upperButtonWidth = parseInt(upperButtonWidth) + 100;
        upperButtonWidth = upperButtonWidth + "px";
      });
    }
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
      } else {
        startStripePayment(
          $mainContainer.find("#payment-form"),
          $mainContainer
            .find("#supporterStepPaymentInfo")
            .data("payment-info-complete-url"),
          completeSubpage
        );
      }
    } else if (method == "paypal") {
      startPayPalPayment(
        $mainContainer.find("#payment-form"),
        $mainContainer
          .find("#supporterStepPaymentInfo")
          .data("payment-info-complete-url"),
        completeSubpage
      );
    } else if (method == "bitcoin") {
      startBitCoinPayment(
        $mainContainer.find("#payment-form"),
        $mainContainer
          .find("#supporterStepPaymentInfo")
          .data("payment-info-pending-url"),
        completeSubpage
      );
    } else if (method == "check") {
      startCheckPayment(
        $mainContainer.find("#payment-form"),
        $mainContainer
          .find("#supporterStepPaymentInfo")
          .data("payment-info-pending-url"),
        completeSubpage
      );
    } else if (method == "existing-credit-card") {
      startStripePayment(
        $("#payment-form"),
        $mainContainer
          .find("#supporterStepPaymentInfo")
          .data("payment-info-complete-url"),
        completeSubpage
      );
    }
  }

  $(document).on("click", "#confirmButton", function(event) {
    var $that = $(this);
    $that.prop("disabled", true);

    if (selectedData.flow == "store") {
      event.preventDefault();
      event.stopPropagation();
    }

    if (currentStep == "Intro") {
      $(this).hide();
    }

    var storeItem = selectedData.type === "store";

    if (currentStep === "SelectType" && storeItem) {
      $(".step-button").removeClass("hidden");
      $itemForm.submit();
    } else if (currentStep === "PaymentInfo") {
      processPaymentInfoStep();
    } else if (currentStep === "Shipping" && storeItem) {
      $mainContainer.find("#new_shipping_address").submit();
    } else if (currentStep === "Billing" && storeItem) {
      $mainContainer.find("#payment-form").submit();
    } else if (currentStep === "Preview" && storeItem) {
      $mainContainer.find("#place-order").submit();
    } else if (currentStep === "SelectType" && selectedData.type != "store") {
      getPaymentInfoForm();
    } else {
      $mainContainer.find(".step-button.gift").addClass("hidden");
      showPanel(getNextStep());
    }

    var $currentButton = $(".step-button.active");
    $currentButton.removeClass("active");
    $currentButton.next().addClass("active");
  });

  $(document).on("click", "#backButton", function() {
    if (currentStep == "PaymentInfo") {
      $mainContainer.find("#confirmButton").hide();
    }

    if (currentStep == "Shipping") {
      $mainContainer.find("#confirmButton").hide();
    }

    if (currentStep == "SelectType") {
      $mainContainer.find("#confirmButton").show();
    }
    if (currentStep === "Intro") return;

    if (!getSteps().indexOf(currentStep) < 1) {
      showPanel(getPreviousStep());
    }

    $mainContainer.find("#confirmButton").text("Confirm");

    setSelected(selectedData.flow, selectedData.type, 0);
    $itemForm = null;
    var $currentButton = $(".step-button.active");
    $currentButton.removeClass("active");
    $currentButton.prev().addClass("active");
  });
});
