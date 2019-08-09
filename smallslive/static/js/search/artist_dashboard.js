
function initializeSearch() {

}

function initializeDashboardDatePickers() {

  var $datePickerFrom = $(".archive-datepicker.fixed:visible .custom-date-picker.from input");
  $datePickerFrom.datepicker({
    format: 'mm/dd/yyyy',
    autoclose: false,
    container: '.archive-datepicker.fixed:visible .custom-date-picker.from',
    showOnFocus: false
  });

  $datePickerFrom.on('changeDate', function (newDate) {
    $("#search-date-picker-to-dashboard input").click();
    $("#search-date-picker-to-dashboard input").focus();
  });

  $datePickerFrom.on('click', function () {
    var dropdown = $('#search-date-picker .dropdown-menu');
    if (dropdown[0] && dropdown[0].style.display === 'block') {
        $datePickerFrom.datepicker('hide');
    } else {
        $datePickerFrom.datepicker('show');
    }
  });

  //////////////////////

  var $datePickerTo = $(".archive-datepicker.fixed:visible .custom-date-picker.to input");
  $datePickerTo.datepicker({
      format: 'mm/dd/yyyy',
      autoclose: false,
      container: '.archive-datepicker.fixed:visible .custom-date-picker.to',
      showOnFocus: false
  });

  $datePickerTo.on("changeDate", function(newDate) {
    // Means any ajax results will not append to existing items.
    // For pagination use apply = false;

    var dateFrom = $datePickerFrom.datepicker("getDate");
    var dateTo = newDate.date;

    sendEventRequest(
      dateFrom,
      dateTo,
      updateShows
    );
    $datePickerFrom.datepicker("setEndDate", dateTo);

    $datePickerFrom.click();
    $datePickerFrom.focus();

  });

  $datePickerTo.on('click', function () {
      var dropdown = $('#dashboard-desktop-datepicker #search-date-picker .dropdown-menu');
      if (dropdown[0] && dropdown[0].style.display === 'block') {
          $datePickerTo.datepicker('hide');
      } else {
          $datePickerTo.datepicker('show');
      }
  });

  $datePickerFrom.click();
}


function sendEventRequest(dateFrom, dateTo, callback) {

  params = {
    'start_date_filter': dateFrom,
    'end_date_filter': dateTo
  }

  $.ajax({
      url: eventsUrl,
      data: params,
      dataType: 'json',
      success: function (data) {
        if (typeof callback === 'function') {
          callback(data);
        }
      }
  });

}

function updateShows(data) {
  $("#event-load-gif").hide();
  $('#artistEventsList').removeClass("artist-loading-gif");
  $('.concerts-footer').show();
  if (data.template) {
      if (currentPage > 1) {
          $("#artistEventsList").append(data.template)
      } else {
          $("#artistEventsList").html(data.template)
      }
  }
  if (data.total_results) {
    $("#number-of-shows-label").html(data.total_results);
  }
  if (data.first_event_date) {
    $("#date-from-label").html(data.first_event_date);
  }
  if (data.last_event_date) {
    $("#date-to-label").html(data.last_event_date);
  }
  if (data.total_pages) {
      totalPages = data.total_pages;
      if (currentPage >= totalPages) {
          $('#next-page-btn').hide();
          $('#load-more-btn').hide();
      } else {
          $('#next-page-btn').show()
      }
  }
}