"use strict";

var formatDate = function(d) {
  var formattedDate =
    ("0" + (d.getMonth() + 1)).slice(-2) +
    "/" +
    ("0" + d.getDate()).slice(-2) +
    "/" +
    d.getFullYear();

  return formattedDate;
};

var artistPageNum,
  artistMaxPageNum,
  archivedEventPageNum,
  archivedEventMaxPageNum,
  upcomingEventPageNum,
  upcomingEventMaxPageNum,
  venueFilter,
  eventFilter,
  archivedEventDateFrom,
  archivedEventDateTo,
  upcomingEventDateFrom,
  upcomingEventDateTo,
  apply,
  artistPk,
  is_upcoming,
  show_event_venue,
  is_mobile,
  show_event_setTime,
  toggleDatePicker,
  rightValue;

function incNumPages(mode) {
  if (mode == "Upcoming") {
    upcomingEventPageNum += 1;
  } else {
    archivedEventPageNum += 1;
  }
}

function viewPortLength(viewPort) {
  var browserName = navigator.userAgent.toLowerCase();
  if (browserName.indexOf("safari") != -1) {
    var windowOrientation = (window.orientation, 90);
    switch (windowOrientation) {
      case 0:
        if (viewPort === "height") return window.innerWidth;
        else if (viewPort === "width") return window.innerHeight;
        break;

      case 180:
        if (viewPort === "height") return window.innerWidth;
        else if (viewPort === "width") return window.innerHeight;
        break;

      case -90:
        if (viewPort === "height") return window.innerHeight;
        else if (viewPort === "width") return window.innerWidth;
        break;

      case 90:
        if (viewPort === "height") return window.innerHeight;
        else if (viewPort === "width") return window.innerWidth;
        break;
    }
  } else {
    if (viewPort === "height") return window.innerHeight;
    else if (viewPort === "width") return window.innerWidth;
  }
}

function showQuantityDisplay(element, addition, slider) {
  var paginatorValue = $(element).data("paginator-number");
  var maxValue = $(element).data("max-number");
  var leftValue = $(element).data("left-number");
  var rightValue = $(element).data("right-number");

  if (addition) {
    if (rightValue + paginatorValue > maxValue) {
      rightValue = maxValue;
      $(element).data("right-number", maxValue);
    } else {
      rightValue = rightValue + paginatorValue;
      $(element).data("right-number", rightValue);
    }
    if (slider) {
      leftValue = leftValue + paginatorValue;
      $(element).data("left-number", leftValue);
    } else {
      leftValue = 1;
      $(element).data("left-number", leftValue);
    }
  } else {
    leftValue = leftValue - paginatorValue;
    rightValue = rightValue - paginatorValue;
    $(element).data("left-number", leftValue);
    $(element).data("right-number", rightValue);
  }
  $(element).text(leftValue + "-" + rightValue);
}

function loadMoreArtistButton() {
  if (artistPageNum !== artistMaxPageNum) {
    artistPageNum += 1;
    $(".white-border-button.load-more-artist-button").hide();
    $(".mobile-artist-loading").show();
    sendArtistRequest(updateArtistsHtml);
  }
}

function searchMoreArtists() {
  /*
   Called from clicking on next button (on the last artist)
   Retrieves another batch of artists and adds to the slider.
  */
  artistPageNum++;
  sendArtistRequest(updateArtistsHtml);
}

function updateArtistsHtml(data, reset) {

  //If no artists returned, hide the next arrow
  if (data.showingResults === "NO RESULTS") {
    $("#artist-load-gif").css("display", "none");
    $("#artists  .slide-btn.next").css("visibility", "hidden");
  }

  moreArtists = true;

  if (data.template) {
    $(".mobile-artist-loading").hide();
    $("#artists .event-row").append(data.template);
    //If there are only enough artists for 1 AJAX request, hide the next arrow after navigating to last artist
    var $articles = $("#artists .event-row article");
    if ($articles.length == data.showingResults && $articles.last().visible()) {
      $("#artists .slide-btn.next").css("visibility", "hidden");
    } else if (data.showingResults != "NO RESULTS") {
      $("#artists .slide-btn.next").css("visibility", "visible");
    }

    if (reset) {
      $("#artists .event-row").css("marginLeft", "0");
      $("#artists .slide-btn.prev").css("visibility", "hidden");
    }
    $("#total-artist").html(data.showingResults);
  }
}


function toggleEventFilters(filters) {
  var $filter = $(".leader-filter-select");

  if (!filters.main_search && !filters.artist_search && !filters.instrument) {
    if (!$filter.hasClass("hidden")) {
      $filter.addClass("hidden");
    }
  } else {
    $filter.removeClass("hidden");
  }
}

function sendArtistRequest(callback, callbackParam) {
  callback = callback || function() {};

  var artistInstrument = $("#select-instrument-btn").data("instrument");
  var artistSearchTerm = $("#artist-search").val();
  var searchTerm = $("#desktop-search-bar").val();

  var filters = {
    main_search: searchTerm,
    artist_search: artistSearchTerm,
    instrument: artistInstrument,
    page: artistPageNum
  };

  toggleEventFilters(filters);

  $.ajax({
    url: "/search/ajax/artist/",
    data: filters,
    dataType: "json",
    success: function (data) {
      callback(data, callbackParam);
    },
    error: function(data) {
      $("#artist-load-gif").css("display", "none");
      $(".right_arrow").css("visibility", "hidden");
    }
  });
}

function sendEventRequest(mode, dateFrom, dateTo, callback) {
  var selector = "#shows" + mode + "Content";
  var utcDateFrom = null;
  var utcDateTo = null;

  var eventDateFrom;
  var eventDateTo;

  $("#event-load-gif").css("display", "block");
  if (eventFilter) {
    $("#search-result-articles").find("article").remove();
  }

  if (mode == "Upcoming") {
    eventDateFrom = dateFrom || upcomingEventDateFrom;
    eventDateTo = dateTo || upcomingEventDateTo;
    eventPageNum = upcomingEventPageNum;
  } else {
    eventDateFrom = dateFrom || archivedEventDateFrom;
    eventDateTo = dateTo || archivedEventDateTo;
    eventPageNum = archivedEventPageNum;
  }
  if (eventDateFrom) {
    utcDateFrom =
      eventDateFrom.getFullYear() +
      "/" +
      (eventDateFrom.getMonth() + 1) +
      "/" +
      eventDateFrom.getDate();
  }
  if (eventDateTo) {
    utcDateTo =
      eventDateTo.getFullYear() +
      "/" +
      (eventDateTo.getMonth() + 1) +
      "/" +
      eventDateTo.getDate();
  }

  var searchTerm = $("#desktop-search-bar").val();
  var eventOrderFilter = $("#events-filter").val();
  var leaderFilter = $("#leader-filter").val();

  var searchFilters = {
    main_search: searchTerm,
    page: eventPageNum,
    order: eventOrderFilter,
    leader: leaderFilter,
    date_from: utcDateFrom ? utcDateFrom : null,
    date_to: utcDateTo ? utcDateTo : null,
    artist_pk: artistPk ? artistPk : null,
    partial: true,
    show_event_venue: show_event_venue ? show_event_venue : null,
    show_event_setTime: show_event_setTime ? show_event_setTime : null,
    is_upcoming: is_upcoming ? is_upcoming : null
  };
  if (venueFilter) {
    searchFilters["venue"] = venueFilter;
  }

  var artistSearchTerm = $("#artist-search").val();
  if (artistSearchTerm) {
    searchFilters["artist_search"] = artistSearchTerm;
  }
  var artistInstrument = $("#select-instrument-btn").data("instrument");
  if (artistInstrument) {
    searchFilters["instrument"] = artistInstrument;
  }

  $.ajax({
    url: "/search/ajax/event/",
    data: searchFilters,
    dataType: "json",
    success: function(data) {
      if (callback) {
        callback(data);
      }
    }
  });
}

$(document).ready(function () {

  var instrument = getUrlParameter("instrument");
  var $instrumentBtn = $("#select-instrument-btn");
  if (instrument) {
    $instrumentBtn.text(instrument);
    $instrumentBtn.data("instrument", instrument);
  }
  artistPageNum = archivedEventPageNum = upcomingEventPageNum = 1;
  artistMaxPageNum = archivedEventMaxPageNum = upcomingEventMaxPageNum = 2;
  apply = false;
  eventFilter = false;

  $("#next-page-btn").click(function() {
    if (eventPageNum !== eventMaxPageNum) {
      eventPageNum += 1;
      sendEventRequest("");
    }
  });

  $("#events-filter").change(function() {
    eventFilter = true;
    venueFilter = "all";
    archivedEventPageNum = 1;
    localStorage.setItem("search_order", $(this).val());

    sendEventRequest(
      "Archived",
      datePickerFromDate,
      datePickerToDate,
      updateArchiveShows
    );
  });

  $("#leader-filter").change(function() {
    eventPageNum = 1;
    archivedEventPageNum = 1;
    eventFilter = true;
    localStorage.setItem("search_leader", $(this).val());

    sendEventRequest(
      "Archived",
      datePickerFromDate,
      datePickerToDate,
      updateArchiveShows
    );
  });

  $("#club-filter").change(function() {
    eventFilter = true;
    venueFilter = $(this).val();
    upcomingEventPageNum = 1;

    sendEventRequest("Upcoming");
  });

  $("#period-filter").change(function() {
    var eventDateFrom;
    var eventDateTo;

    eventFilter = true;

    if (datePickerFromDate) {
      var start = datePickerFromDate;
    } else {
      var start = new Date();
    }

    if ($(this).val() == "All Upcoming") {
      eventDateTo = null;
      eventDateFrom = new Date();
    } else if ($(this).val() == "One Day") {
      eventDateTo = new Date(start.getTime() + 1 * 24 * 60 * 60 * 1000);
      eventDateFrom = start;
    } else if ($(this).val() == "One Week") {
      eventDateTo = new Date(start.getTime() + 7 * 24 * 60 * 60 * 1000);
      eventDateFrom = start;
    } else if ($(this).val() == "One Month") {
      eventDateTo = new Date(start.getTime() + 31 * 24 * 60 * 60 * 1000);
      eventDateFrom = start;
    }

    if (eventDateTo) {
      $(".datepicker-btn").html(
        'From <span class="from accent-color"></span> to <span class="to accent-color"></span>'
      );
      $(".datepicker-btn span.from").text(eventDateFrom.toLocaleDateString());
      $(".datepicker-btn span.to").text(eventDateTo.toLocaleDateString());
    } else {
      $(".datepicker-btn").html("DATE");
    }
    if ($(".shows-calendar .datepicker-btn")) {
      $(".datepicker-btn").html("DATE");
      $("#calendar-date-range .title2").html(
        eventDateFrom.toLocaleDateString() +
          " - " +
          (eventDateTo != null ? eventDateTo.toLocaleDateString() : "")
      );
    }

    var mode = getCurrentMode($(this));
    if (mode == "Upcoming") {
      upcomingEventPageNum = 1;
      upcomingEventDateFrom = eventDateFrom;
      upcomingEventDateTo = eventDateTo;
    } else {
      archivedEventPageNum = 1;
      archivedEventDateFrom = eventDateFrom;
      archivedEventDateTo = eventDateTo;
    }
    sendEventRequest(mode);
  });

  var delay = (function() {
    var timer = 0;
    return function(callback, ms) {
      clearTimeout(timer);
      timer = setTimeout(callback, ms);
    };
  })();

  $("#artist-search").on("change", function() {
    delay(function() {
      artistPageNum = 1;
      eventPageNum = 1;
      archivedEventPageNum = 1;
      eventFilter = true;
      toggleDatePicker = true;
      $("#artists .event-row").html("");
      $("#artist-subheader").data("left-number", 1);
      $("#artist-subheader").data("right-number", 24);
      sendArtistRequest(updateArtistsHtml, true);
      sendEventRequest(
        "Archived",
        datePickerFromDate,
        datePickerToDate,
        updateArchiveShows,
      );
    }, 700);
  });

  $(".instrument-btn").click(function() {
    if (!$(".instruments-container").is(":visible")) {
      $(".instruments-container").css("display", "flex");
    } else {
      if (viewPortLength("width") < 1024) {
        $("body").removeClass("hidden-body");
      }
      $(".instruments-container").css("display", "none");
    }
  });

  $(document).on("click", function(event) {
    // Instruments Container was clicked.
    var onContainer = $(event.target).closest(".instruments-container").length;
    // Dropdown button was clicked.
    var onButton = $(event.target.closest(".instrument-btn")).length;
    var containerVisible = $(".instruments-container").is(":visible");
    if (containerVisible && !onButton && !onContainer) {
      $(".instruments-container").css("display", "none");
    }
  });

  $(".instruments-container .close-button").click(function() {
    if (viewPortLength("width") < 1024) {
      $("body").removeClass("hidden-body");
    }
  });

  $(".instrument").click(function() {

    if (viewPortLength("width") < 1024) {
      $("body").removeClass("hidden-body");
    }

    /* Store selected value in button data and session*/
    var instrument = $(this).data("instrument");

    $("#select-instrument-btn").data("instrument", instrument);
    $(".instrument-btn").text(instrument || "Instrument");
    $("#artists .event-row").html("");

    localStorage.setItem('search_instrument', instrument);

    eventPageNum = 1;
    archivedEventPageNum = 1;
    artistPageNum = 1;
    eventFilter = true;

    sendArtistRequest(updateArtistsHtml, true);
    toggleDatePicker = true;
    sendEventRequest(
      "Archived",
      datePickerFromDate,
      datePickerToDate,
      updateArchiveShows
    );
    $(".instruments-container").css("display", "none");
  });

  ////////////////

  $(".shows-filter-container .datepicker-btn").bind("click", toggleArchiveDatePickerDisplay);

  $(document).on("click", "#archive-datepicker-close", function () {
    toggleArchiveDatePickerDisplay();
  });

  $("#archive-datepicker-apply").click(function () {
    applySearch();
    toggleArchiveDatePickerDisplay();
  });

  function toggleArchiveDatePickerDisplay(event) {
    var $container  = $(".archive-datepicker.fixed");
    if (!$container.hasClass("active")) {
      $container.addClass("active");
      $datePickerFrom.click();
      $datePickerFrom.focus();
    } else {
      $container.removeClass("active");
    }
  }

  /////////////////////


  $("#apply-button").click(function() {
    var eventDateFrom = datePickerFromDate;
    var eventDateTo = datePickerToDate;

    if ($(this).hasClass("archived")) {
      var mode = "Archived";
      $("#load-more-archived-btn").hide();
      var selector = "#showsArchivedContent";
      archivedEventPageNum = 1;
      archivedEventDateFrom = eventDateFrom;
      archivedEventDateTo = eventDateTo;
    } else {
      var mode = "Upcoming";
      var selector = "#showsUpcomingContent";
      upcomingEventPageNum = 1;
      upcomingEventDateFrom = 1;
      upcomingEventDateTo = 1;
      $("#load-more-upcoming-btn").hide();
    }

    var $showsContainer = $("#search-result-articles");
    $showsContainer.html("");
    if ($(this).closest(".calendar").length > 0) {
      show_event_venue = true;
      show_event_setTime = true;
    }

    apply = true;
    toggleDisplay(this);
    $("#events").addClass("artist-loading-gif");
    sendEventRequest(mode, eventDateFrom, eventDateTo, updateArchiveShows);

    if (!eventDateTo || !eventDateFrom) {
      $(".datepicker-btn").html("DATE");
    }
    if (eventDateFrom) {
      var from =
        datePickerFromDate.getMonth() +
        1 +
        "/" +
        datePickerFromDate.getDate() +
        "/" +
        datePickerFromDate.getFullYear();
      from = '<span class="from accent-color">' + from + "</span>";
    } else {
      from = '<span class="from accent-color">-</span>';
    }

    if (eventDateTo) {
      var to =
        datePickerToDate.getMonth() +
        1 +
        "/" +
        datePickerToDate.getDate() +
        "/" +
        datePickerToDate.getFullYear();
      to = '<span class="to accent-color">' + to + "</span>";
    } else {
      to = '<span class="from accent-color">-</span>';
    }
  });


  var $datePickerCalendar = $("#search-date-picker-calendar input");
  $datePickerCalendar.datepicker({
    format: "mm/dd/yyyy",
    autoclose: true,
    container: "#search-date-picker-calendar",
    showOnFocus: false,
    startDate: defaultFromDate,
    endDate: defaultToDate
  });

  if (setFromDate) {
    $datePickerCalendar.datepicker("setDate", defaultFromDate);
    datePickerFromDate = new Date(defaultFromDate);
  }

  function getCurrentMode($element) {
    var $container = $element.closest(".search-tab-content");
    if ($container.hasClass("archived")) {
      return "Archived";
    } else {
      return "Upcoming";
    }
  }

  $datePickerCalendar.on("changeDate", function(newDate) {
    var mode = getCurrentMode($(this));

    datePickerFromDate = newDate.date;
    if (!datePickerToDate || datePickerFromDate > datePickerToDate) {
      datePickerToDate = datePickerFromDate;
      $datePickerTo.datepicker("setDate", datePickerToDate);
    }
    apply = true;
    if (mode == "Upcoming") {
      upcomingEventDateFrom = datePickerFromDate;
      upcomingEventPageNum = 1;
      var eventDateFrom = upcomingEventDateFrom;
    } else {
      archivedEventDateFrom = datePickerFromDate;
      archivedEventPageNum = 1;
      var eventDateFrom = archivedEventDateFrom;
    }
    var eventDateTo;
    var periodFilterElement = $("#period-filter");
    if (periodFilterElement) {
      if (periodFilterElement.val() == "All Upcoming") {
        eventDateTo = null;
        eventDateFrom = new Date();
      } else if (periodFilterElement.val() == "One Day") {
        eventDateTo = new Date(
          eventDateFrom.getTime() + 1 * 24 * 60 * 60 * 1000
        );
      } else if (periodFilterElement.val() == "One Week") {
        eventDateTo = new Date(
          eventDateFrom.getTime() + 7 * 24 * 60 * 60 * 1000
        );
      } else if (periodFilterElement.val() == "One Month") {
        eventDateTo = new Date(
          eventDateFrom.getTime() + 31 * 24 * 60 * 60 * 1000
        );
      }
      upcomingEventDateTo = eventDateTo;
    } else {
      eventDateTo = null;
    }

    $("#calendar-date-range .title2").html(
      eventDateFrom.toLocaleDateString() +
        " - " +
        (eventDateTo ? eventDateTo.toLocaleDateString() : "")
    );
    toggleDisplay(this);
    sendEventRequest(mode);
  });

  $datePickerCalendar.on("click", function() {
    var dropdown = $("#search-date-picker-calendar .dropdown-menu");
    if (dropdown[0] && dropdown[0].style.display === "block") {
      $datePickerCalendar.datepicker("hide");
    } else {
      $datePickerCalendar.datepicker("show");
    }
  });

  $(window).resize(function() {
    if (viewPortLength("width") < 1024 && is_mobile == false) {
      $("div[data-toggle-tab-target='archived-shows'")[0].click();
      is_mobile = true;
    }
    if (viewPortLength("width") >= 1024 && is_mobile == true) {
      if ($(".artist-search-profile-container").css("display") != "block") {
        $("#musicianContent").css("display", "block");
        $(".search-tab-content").show();
        $(
          '[data-toggle-tab-group="search-results"][data-toggle-tab="upcoming-shows"]'
        ).hide();
        is_mobile = false;
      }
    }
    let pages = rightValue / 6 / 4;
    pages -= 1;
    $("#artists").animate(
      {
        left: -88 * pages + "vw"
      },
      200,
      "linear",
      function() {
        toggleArrows();
      }
    );
  });

  triggerSearch();

});

$(document).on(
  "click",
  ".artist-search-profile-container.pad-content .close-button",
  function() {
    if (viewPortLength("width") < 1024) {
      $(
        ".search-tabs div[data-toggle-tab-target='archived-shows']"
      ).removeClass("active");
      $(".search-tabs div[data-toggle-tab-target='musicians']").addClass(
        "active"
      );
    }
  }
);

$(document).ready(function() {
  if (
    viewPortLength("width") < 1024 &&
    $("div[data-toggle-tab-target='archived-shows'").length != 0
  ) {
    //$("div[data-toggle-tab-target='archived-shows'")[0].click();
    //is_mobile = true;
  } else {
    is_mobile = false;
  }
  //$("body").removeClass("hidden-body");
});

$(document).ready(function() {
  artistPk = getUrlParameter("artist_pk");
  artistPk = artistPk ? artistPk : "";
  if (artistPk) {
    $(".search-tabs div[data-toggle-tab-target='archived-shows']").removeClass(
      "active"
    );
    $(".search-tabs div[data-toggle-tab-target='musicians']").addClass(
      "active"
    );
  }
});

$("#archive-date-picker").datepicker({
  onSelect: function(dateText, inst) {
    console.log("a");
  },
  format: "mm/dd/yyyy",
  container: "#archive-date-picker",
  startDate: defaultFromDate,
  endDate: defaultToDate
});
$("#archive-date-picker")
  .datepicker()
  .on("changeDate", function(ev) {
    var newStartingDate = $("#archive-date-picker").datepicker("getDate");
    var newStartingDateRefined =
      newStartingDate.getFullYear() +
      "-" +
      (newStartingDate.getMonth() + 1) +
      "-" +
      newStartingDate.getDate();
    $("#load-more-calendar").data("starting-date", newStartingDateRefined);
    getCalendarAjax(
      $("#load-more-calendar").data("starting-date"),
      12,
      true,
      $("#load-more-calendar").data("venue")
    );
  });

var eventPageNum;

function initializeSearch() {
  apply = true;
  eventPageNum = 1;
  archivedEventPageNum = eventPageNum;
}

function resetSearch() {
  initializeSearch();
  resetDatePickers();
}

function triggerSearch() {
  var triggerArtistSearch = false;
  var triggerEventSearch = false;

  var datePickerFromVal = $datePickerFrom.val();
  if (datePickerFromVal && datePickerFromVal != startDate) {
    triggerEventSearch = true;
    startDate = datePickerFromVal;
  }
  var datePickerToVal = $datePickerTo.val();
  if (datePickerToVal && datePickerToVal != startDate) {
    triggerEventSearch = true;
    endDate = datePickerToVal;
  }

  // detect if user has navigated here using the back button
  // apply filters if necessary
  var clearStorage = false
  if (!(window.performance && window.performance.navigation.type == window.performance.navigation.TYPE_BACK_FORWARD)) {
    if (document.location.search.indexOf("artist_pk=") === -1) {
      clearStorage = true;
    }
  }

  if (clearStorage) {
    clearStorage = localStorage.removeItem("search_instrument");
    clearStorage = localStorage.removeItem("search_artist");
    clearStorage = localStorage.removeItem("search_order");
    clearStorage = localStorage.removeItem("search_leader");
  }

  var instrument = localStorage.getItem("search_instrument");
  if (instrument && document.location.search.indexOf("artist_pk=") === -1) {
    $("#select-instrument-btn").data("instrument", instrument);
    $(".instrument-btn").text(instrument);
    triggerArtistSearch = true;
    triggerEventSearch = true;
  }

  var artistSearch = localStorage.getItem("search_artist");
  if (artistSearch && document.location.search.indexOf("artist_pk=") === -1) {
    $("a-z-search").attr("selected-value", artistSearch);
    $("#a-z-search .white-border-button:contains('" + artistSearch + "')").addClass("active");
    $("#artist-search").val(artistSearch);
    triggerArtistSearch = true;
    triggerEventSearch = true;
  }

  var order = localStorage.getItem("search_order");
  if (order && document.location.search.indexOf("artist_pk=") === -1) {
    $('#artist_archive_order_filter').val(order);
    triggerEventSearch = true;
  }

  var leader = localStorage.getItem("search_leader");
  if (leader && document.location.search.indexOf("artist_pk=") === -1) {
    $('#artist_archive_status_filter').val(leader);
    triggerEventSearch = true;
  }

  if (triggerArtistSearch) {
    toggleDatePicker = true;
    $("#artists .event-row").html("");
    artistPageNum = 1;
    sendArtistRequest(updateArtistsHtml, true);
  }

  if (triggerEventSearch) {
    datePickerFromDate = $datePickerFrom.datepicker("getDate");
    datePickerToDate = $datePickerTo.datepicker("getDate");
    eventFilter = true;
    eventPageNum = 1;
    archivedEventPageNum = 1;
    upcomingEventPageNum = 1;
    sendEventRequest(
      "Archived",
      datePickerFromDate,
      datePickerToDate,
      updateArchiveShows
    );
  }
}

function loadMoreEvents(mode) {
  if ($("main.calendar").length > 0) {
    show_event_venue = true;
    show_event_setTime = true;
  }
  incNumPages(mode);
  var selector = "#load-more-archived-btn";
  var $eventSubheader = $("#archived-event-subheader");
  if (mode == "Upcoming") {
    selector = "#load-more-upcoming-btn";
    $eventSubheader = $("#upcoming-event-subheader");
  }
  $(selector).hide();
  sendEventRequest(
    mode,
    datePickerFromDate,
    datePickerToDate,
    updateArchiveShows
  );

  showQuantityDisplay($eventSubheader, true, false);
}

function updateArchiveShows(data) {

  $("#event-load-gif").css("display", "none");

  if (data.numPages < eventPageNum) {
    moreEvents = false;
    return;
  }

  moreEvents = true;

  if (data.template) {

    if (eventPageNum === 1) {
      var $eventSubheader = $("#archived-event-subheader");
      if (typeof data.showingResults !== "number") {
        $eventSubheader.text("0-0");
      } else if (data.showingResults < 60) {
        $eventSubheader.text("1-" + data.showingResults);
      } else {
        $eventSubheader.text("1-60");
      }
      $eventSubheader.data("max-number", data.showingResults);
      $eventSubheader.data("left-number", 1);
      $eventSubheader.data("right-number", 60);
    }

    var selector = "#showsArchivedContent";

    var $showsContainer = $("#search-result-articles");
    $("#events").removeClass("artist-loading-gif");
    var $eventSubHeaderFooter = "#archived-event-subheader-footer";
    var $totals = $("#archived-event-totals");
    $totals.html(data.showingResults);

    if (apply || eventFilter) {
      apply = false;
      eventFilter = false;
      $showsContainer.find("article").remove();
      // Date Picker must be hidden if less than 30 results.
      // Exception: not if the user is filtering with the date picker itself.
      $(".archive-datepicker.fixed").removeClass("desktop-hidden");
      if (toggleDatePicker) {
        if (defaultFromDate === datePickerFromDate && defaultToDate === datePickerToDate) {
          if (data.showingResults < 30 || data.showingResults === "NO RESULTS") {
            $(".archive-datepicker.fixed").addClass("desktop-hidden");
          }
        }
      }
    }
    var $article = $(data.template);
    if (!$article.length) {
      $showsContainer.html(data.template);
    }
    $article.each(function(index) {
      $showsContainer.append($(this));
    });
    archivedEventMaxPageNum = data.numPages;

    $("#event-load-gif").css("display", "none");
    var selector = "#load-more-archived-btn";
    $(selector).toggle(data.numPages != eventPageNum);
    $("#number-of-shows-label").text(data.showingResults);

    $("#date-from-label").text(formatDate(datePickerFromDate));
    $("#date-to-label").text(formatDate(datePickerToDate));
  }
}

