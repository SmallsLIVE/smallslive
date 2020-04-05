
$(document).ready(function () {

  $(".datepicker-btn").on("click", toggleDisplay);

  function toggleDisplay(event) {

    var $container = $(this).prev('.datepicker-container');
    if ($container.data("shown")) {
      hide(event, $container);
    } else {
      display($container);
    }
  }

  function display($datePickerContainer) {
    $datePickerContainer.css({
      left: datePickerLeft,
      top: datePickerTop,
    });
    $datePickerContainer.css("display", "flex");
    $datePickerContainer.data("shown", true);

    var $datePickerInput = $datePickerContainer.find('input');
    $datePickerInput.click();
    let isCalendar =
      $(location)
      .attr("href")
      .split("/")
      .reverse()[1] || false;
    if (isCalendar == 'calendar') {
      $datePickerInput.prop("disabled", true);
    }
    $datePickerInput.focus();
  }

  function hide(event, $datePickerContainer) {
    var $target = $(event.target);
    if (
      $target.closest(".noclick").length == 0 &&
      !($target.hasClass("day") || $target.hasClass("year"))
    ) {
      if ($datePickerContainer) {
       $(document).unbind("click", hide);
       $datePickerContainer.hide().data("shown", false);
      }
    }
  }
});
