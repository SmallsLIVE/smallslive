var datePickerFromDateSet;
var datePickerToDateSet;

function initializeArchiveDatePickers() {

  $datePickerFrom.datepicker({
    format: "mm/dd/yyyy",
    autoclose: false,
    container: ".archive-datepicker.fixed .custom-date-picker.from",
    showOnFocus: false,
    startDate: startDate,
    endDate: endDate
  });

  $datePickerFrom.on("click", function() {
    var dropdown = $(
      ".archive-datepicker.fixed .custom-date-picker.from .dropdown-menu"
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

    if (!datePickerToDateSet) {
      $datePickerTo.click();
      $datePickerTo.focus();
    }

    // ignore actions if the apply button is visible.
    if  ($("#archive-datepicker-apply").visible()) {
      return;
    }

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

  });

  $datePickerTo.datepicker({
    format: "mm/dd/yyyy",
    autoclose: false,
    container: ".archive-datepicker.fixed .custom-date-picker.to",
    showOnFocus: false,
    startDate: startDate,
    endDate: endDate
  });

  $datePickerTo.on("click", function() {
    var dropdown = $(
      ".archive-datepicker.fixed .custom-date-picker.to .dropdown-menu"
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

    datePickerToDate = newDate.date;
    datePickerToDateSet = true;
    $datePickerFrom.datepicker("setEndDate", datePickerToDate);
    if (!datePickerFromDateSet) {
      $datePickerFrom.click();
      $datePickerFrom.focus();
    }

    /* No action  if the user will click apply */
    if  ($("#archive-datepicker-apply").visible()) {
      return;
    }

    // Means any ajax results will not append to existing items.
    // For pagination use apply = false;
    initializeSearch();
    sendEventRequest(
      "Archived",
      datePickerFromDate,
      datePickerToDate,
      updateArchiveShows
    );
  });

  $datePickerFrom.click();
}

function applySearch() {

  initializeSearch();
  sendEventRequest(
    "Archived",
    datePickerFromDate,
    datePickerToDate,
    updateArchiveShows
  );
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
