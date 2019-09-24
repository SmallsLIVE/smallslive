var datePickerFromDateSet;
var datePickerToDateSet;

function initializeArchiveDatePickers() {

  var triggerSearch = false;

  var datePickerFromVal = $datePickerFrom.val();
  if (datePickerFromVal && datePickerFromVal != startDate) {
    triggerSearch = true;
    startDate = datePickerFromVal;
  }
  var datePickerToVal = $datePickerTo.val();
  if (datePickerToVal && datePickerToVal != startDate) {
    triggerSearch = true;
    endDate = datePickerToVal;
  }

  $datePickerFrom.datepicker({
    format: "mm/dd/yyyy",
    autoclose: false,
    container: ".archive-datepicker.fixed:visible .custom-date-picker.from",
    showOnFocus: false,
    startDate: startDate,
    endDate: endDate
  });

  if (triggerSearch) {
    $datePickerFrom.datepicker("setValue", startDate);
  }

  $datePickerFrom.on("click", function() {
    var dropdown = $(
      ".archive-datepicker.fixed:visible .custom-date-picker.from .dropdown-menu"
    );
    if (dropdown[0] && dropdown[0].style.display === "block") {
    } else {
      $datePickerFrom.datepicker("show");
      $datePickerTo.datepicker("hide");
    }
    $datePickerFrom.addClass("active");
    $datePickerTo.removeClass("active");
  });

  $datePickerFrom.on("changeDate", function(newDate) {
    datePickerFromDate = newDate.date;
    datePickerFromDateSet = true;
    // Means any ajax results will not append to existing items.
    // For pagination use apply = false;
    initializeSearch();
    $datePickerTo.datepicker("setStartDate", datePickerFromDate);
    sendEventRequest(
      "Archived",
      datePickerFromDate,
      datePickerToDate,
      updateArchiveShows
    );
    if (!datePickerToDateSet) {
      $datePickerTo.click();
      $datePickerTo.focus();
    }
  });

  $datePickerTo.datepicker({
    format: "mm/dd/yyyy",
    autoclose: false,
    container: ".archive-datepicker.fixed:visible .custom-date-picker.to",
    showOnFocus: false,
    startDate: startDate,
    endDate: endDate
  });

  if (triggerSearch) {
    $datePickerTo.datepicker("setValue", endDate);
  }

  $datePickerTo.on("click", function() {
    var dropdown = $(
      ".archive-datepicker.fixed:visible .custom-date-picker.to .dropdown-menu"
    );
    if (dropdown[0] && dropdown[0].style.display === "block") {
    } else {
      $datePickerTo.datepicker("show");
      $datePickerFrom.datepicker("hide");
    }
    $datePickerTo.addClass("active");
    $datePickerFrom.removeClass("active");
  });

  $datePickerTo.on("changeDate", function(newDate) {
    // Means any ajax results will not append to existing items.
    // For pagination use apply = false;
    datePickerToDate = newDate.date;
    datePickerToDateSet = true;
    initializeSearch();
    sendEventRequest(
      "Archived",
      datePickerFromDate,
      datePickerToDate,
      updateArchiveShows
    );
    $datePickerFrom.datepicker("setEndDate", datePickerToDate);
    if (!datePickerFromDateSet) {
      $datePickerFrom.click();
      $datePickerFrom.focus();
    }
  });

  $datePickerFrom.click();
  $datePickerFrom.focus();

  $("#reset-search-datepicker").click(function() {
    resetSearch();
    sendEventRequest(
      "Archived",
      datePickerFromDate,
      datePickerToDate,
      updateArchiveShows
    );
  });

  if (triggerSearch) {
    sendEventRequest(
      "Archived",
      $datePickerFrom.datepicker("getDate"),
      $datePickerTo.datepicker("getDate"),
      updateArchiveShows
    );
  }
}

function resetDatePickers() {

  datePickerFromDateSet = null;
  datePickerToDateSet = null;
  $datePickerFrom.val("").datepicker("update");
  $datePickerTo.val("").datepicker("update");
  datePickerFromDate =
    defaultFromDate !== undefined ? new Date(defaultFromDate) : null;
  datePickerToDate =
    defaultToDate !== undefined ? new Date(defaultToDate) : null;
  $datePickerFrom.click();
  $datePickerFrom.focus();
}
