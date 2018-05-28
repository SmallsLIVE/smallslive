function getAjaxSubmitForForm(form, formFields) {
  return function ajaxSubmit(e) {
    e.preventDefault();
    formFields.forEach(function (fieldName) {
      form.find("#" + fieldName + "-error").addClass('hidden');
    });
    $.ajax({
      type: "POST",
      url: form.attr('action'),
      data: form.serialize(),
      success: function (data) {
        console.log('Data Location', data);
        if (data.location) {
          window.location = data.location;
        }
      },
      error: function (jqXHR, textStatus, errorThrown) {
        var response = jqXHR.responseJSON;
        formFields.forEach(function (fieldName) {
          if (response.form_errors[fieldName]) {
            $(form).find("input[name=" + fieldName + "]").parent().addClass('has-error');
            $(form).find("#" + fieldName + "-error")
              .removeClass('hidden')
              .text(response.form_errors[fieldName][0]);
          }
        });

        if (response.form_errors.__all__) {
          $(form).find("#all-errors").parent().addClass('has-error');
          $(form).find("#all-errors")
            .removeClass('hidden').text(response.form_errors.__all__[0]);
        }
      }
    });
    return false;
  }
}


function calculateWeeksBetween(date1, date2) {
  var ONE_WEEK = 1000 * 60 * 60 * 24 * 7;
  var date1_ms = date1.getTime();
  var date2_ms = date2.getTime();
  var difference_ms = Math.abs(date1_ms - date2_ms);
  var total_weeks = Math.floor(difference_ms / ONE_WEEK);

  if (date1_ms >= date1_ms) {
    return total_weeks
  } else {
    return -total_weeks
  }
}

