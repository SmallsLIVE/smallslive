
function renderCardAnimation(selector) {
  var selector = selector || "#formSupporter";

  var card = new Card({
    form: selector,
    formSelectors: {
      expiryInput: "#expiry-month, #expiry-year"
    },
    container: ".card-wrapper"
  });
}

function startStripePayment($form, action_url, completeSubpage) {
  console.log('Send Stripe API Request ->');
  var flowType = $mainContainer.find("#supporterSteps").data("flow");
      // Insert the token into the form so it gets submitted to the server
  // and submit
  $form.append(
    $('<input type="hidden" name="flow_type" />').val(flowType)
  );

  var productId = $mainContainer.find("#supporterSteps").data("product-id");
      // Insert the token into the form so it gets submitted to the server
  // and submit
  $form.append(
    $('<input type="hidden" name="product_id" />').val(productId)
  );

  var eventId = $mainContainer.find("#supporterSteps").data("event-id");
      // Insert the token into the form so it gets submitted to the server
  // and submit
  $form.append(
    $('<input type="hidden" name="event_id" />').val(eventId)
  );

  var eventSlug = $mainContainer.find("#supporterSteps").data("event-slug");
      // Insert the token into the form so it gets submitted to the server
  // and submit
  $form.append(
    $('<input type="hidden" name="event_slug" />').val(eventSlug)
  );

  var stripeResponseHandler = function(status, response) {
    if (response.error) {
      // Show the errors on the form
      // TODO Display payment errors
      $mainContainer.find("#form-general-error").text(response.error.message);
      $form
        .find(".submit-button")
        .prop("disabled", false)
        .removeClass("disabled");
      $mainContainer.find('#confirmButton').prop("disabled", false);
    } else {
      // token contains id, last4, and card type
      var token = response.id;
      $form.append($('<input type="hidden" name="stripe_token" />').val(token));
      $.ajax({
        type: "POST",
        url: action_url,
        data: $form.serialize(),
        success: function(data) {
          if (data.error) {
            $mainContainer.find("#form-general-error").text(data.error);
            $form
              .find(".submit-button")
              .prop("disabled", false)
              .removeClass("disabled");
            $('#confirmButton').prop("disabled", false);
            $mainContainer.find("#backButton").click();
            $mainContainer.find(".payment-errors").html(data.error);
            $mainContainer.find("#sentHint").hide();
          } else if (typeof completeSubpage !== "undefined" && completeSubpage) {
            window.notCompleteContainer.html("");
            var flowCompleteSubpage = window.subpages.get(completeSubpage);
            flowCompleteSubpage.load();
          } else {
            window.location = data.location;
          }
        },
        error: function() {}
      });
    }
  };
  if ($form.find("#payment-method").val() == "existing-credit-card") {
    $.ajax({
      type: "POST",
      url: action_url,
      data: $form.serialize(),
      success: function(data) {
        if (typeof completeSubpage !== "undefined" && completeSubpage) {
          window.notCompleteContainer.html("");
          var flowCompleteSubpage = window.subpages.get(completeSubpage);
          flowCompleteSubpage.load();
        } else {
          window.location = data.location;
        }
      },
      error: function() {}
    });
  } else {
    Stripe.card.createToken($form, stripeResponseHandler);
  }
}

function startPayPalPayment($form, action_url, completeSubpage) {

  var flowType = $mainContainer.find("#supporterSteps").data("flow");
      // Insert the token into the form so it gets submitted to the server
  // and submit
  $form.append(
    $('<input type="hidden" name="flow_type" />').val(flowType)
  );

  var productId = $mainContainer.find("#supporterSteps").data("product-id");
      // Insert the token into the form so it gets submitted to the server
  // and submit
  $form.append(
    $('<input type="hidden" name="product_id" />').val(productId)
  );

  var eventId = $mainContainer.find("#supporterSteps").data("event-id");
      // Insert the token into the form so it gets submitted to the server
  // and submit
  $form.append(
    $('<input type="hidden" name="event_id" />').val(eventId)
  );

  var eventSlug = $mainContainer.find("#supporterSteps").data("event-slug");
      // Insert the token into the form so it gets submitted to the server
  $form.append(
    $('<input type="hidden" name="event_slug" />').val(eventSlug)
  );

  $.ajax({
    type: "POST",
    url: action_url,
    data: $form.serialize(),
    success: function(data) {
      if (typeof completeSubpage !== "undefined" && completeSubpage) {
        //notCompleteContainer.html("")
        var flowCompleteSubpage = window.subpages.get(completeSubpage);
        flowCompleteSubpage.load();
      } else {
        window.location = data.payment_url;
      }
    },
    error: function(data) {
      console.log(data);
    }
  });
}

function startBitCoinPayment($form, action_url, completeSubpage) {

  var flowType = $mainContainer.find("#supporterSteps").data("flow");
  // Insert the token into the form so it gets submitted to the server
  // and submit
  $form.append(
    $('<input type="hidden" name="flow_type" />').val(flowType)
  );
  // Insert the token into the form so it gets submitted to the server
  // and submit
  var productId = $mainContainer.find("#supporterSteps").data("product-id");
  $form.append(
    $('<input type="hidden" name="product_id" />').val(productId)
  );

  var eventId = $mainContainer.find("#supporterSteps").data("event-id");
      // Insert the token into the form so it gets submitted to the server
  // and submit
  $form.append(
    $('<input type="hidden" name="event_id" />').val(eventId)
  );

  var eventSlug = $mainContainer.find("#supporterSteps").data("event-slug");
      // Insert the token into the form so it gets submitted to the server
  $form.append(
    $('<input type="hidden" name="event_slug" />').val(eventSlug)
  );

  $.ajax({
    type: "POST",
    url: action_url,
    data: $form.serialize(),
    success: function(data) {
      if (typeof completeSubpage !== "undefined" && completeSubpage) {
        //notCompleteContainer.html("")
        var flowCompleteSubpage = window.subpages.get(completeSubpage);
        flowCompleteSubpage.load();
      } else {
        window.location = data.location;
      }
    },
    error: function() {}
  });
}

function startCheckPayment($form, action_url, completeSubpage) {

  var flowType = $mainContainer.find("#supporterSteps").data("flow");
  // Insert the token into the form so it gets submitted to the server
  // and submit
  $form.append(
    $('<input type="hidden" name="flow_type" />').val(flowType)
  );
  // Insert the token into the form so it gets submitted to the server
  // and submit
  var productId = $mainContainer.find("#supporterSteps").data("product-id");
  $form.append(
    $('<input type="hidden" name="product_id" />').val(productId)
  );

  var eventId = $mainContainer.find("#supporterSteps").data("event-id");
      // Insert the token into the form so it gets submitted to the server
  // and submit
  $form.append(
    $('<input type="hidden" name="event_id" />').val(eventId)
  );

  var eventSlug = $mainContainer.find("#supporterSteps").data("event-slug");
      // Insert the token into the form so it gets submitted to the server
  $form.append(
    $('<input type="hidden" name="event_slug" />').val(eventSlug)
  );

  $.ajax({
    type: "POST",
    url: action_url,
    data: $form.serialize(),
    success: function(data) {
      if (typeof completeSubpage !== "undefined" && completeSubpage) {
        //notCompleteContainer.html("")
        var flowCompleteSubpage = window.subpages.get(completeSubpage);
        flowCompleteSubpage.load();
      } else {
        window.location = data.location;
      }
    },
    error: function() {}
  });
}
