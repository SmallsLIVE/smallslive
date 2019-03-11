"use strict";

var searchTerm,
  artistSearchTerm,
  artistInstrument,
  artistPageNum,
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
  artist_pk,
  is_upcoming,
  show_event_venue,
  is_mobile,
  show_event_setTime;
var rightValue;

function incNumPages(mode) {
  if (mode == "Upcoming") {
    upcomingEventPageNum += 1;
  } else {
    archivedEventPageNum += 1;
  }
}

function fromYearClick() {
  $datePickerFrom = $("#search-date-picker-from input");
  $datePickerFrom.click();
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
    sendArtistRequest();
  }
}

$("#a-z-refresh").click(() => {
  searchTerm = "";
  artistSearchTerm = "";
  $("#artist-search").val("");
  $("#artist-search").change();
  $("#a-z-search .white-border-button").css("background-color", "#f0f0eb");
  $("#a-z-refresh").css("background-color", "#fff");
});

function sendArtistRequest(callback) {
  callback = callback || function() {};
  $.ajax({
    url: "/search/ajax/artist/",
    data: {
      main_search: searchTerm,
      artist_search: artistSearchTerm,
      instrument: artistInstrument,
      page: artistPageNum
    },
    dataType: "json",
    success: function(data) {
      if (data.template) {
        if (artistPageNum === 1) {
          if (typeof data.showingResults !== "number") {
            $("#artist-subheader").text("0-0");
          } else if (data.showingResults < 24) {
            $("#artist-subheader").text("1-" + data.showingResults);
          } else {
            $("#artist-subheader").text("1-24");
          }
        }
        $(".mobile-artist-loading").hide();
        $("#total-artist").html(data.showingResults);
        $("#artist-subheader").data("max-number", data.showingResults);
        $("#artists").append(data.template);
        artistMaxPageNum = data.numPages;
        if (artistPageNum === artistMaxPageNum) {
          $(".white-border-button.load-more-artist-button").hide();
        } else {
          if (viewPortLength("width") < 960) {
            $(".white-border-button.load-more-artist-button").show();
          }
        }
      }
      callback(data);
    },
    error: function(data) {
      $("#artist-load-gif").css("display", "none");
      $(".container-list-article").css("height", "auto");
      $(".right_arrow").css("visibility", "hidden");
    }
  });
}
$(window).resize(function() {
  if (viewPortLength("width") < 1024 && is_mobile == false) {
    $("div[data-toggle-tab-target='archived-shows'")[0].click();
    is_mobile = true;
  }
  if (viewPortLength("width") >= 1024 && is_mobile == true) {
    if ($(".artist-search-profile-container").css("display") != "block") {
      $("#musicianContent").css("display", "block");
      $(".search-tab-content").show();
      is_mobile = false;
    }
  }
  let pages = rightValue / 6 / 4;
  pages -= 1;
  console.log(pages);
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

function changePage(param) {
  eventPageNum = parseInt(param.getAttribute("data-page-number"));
  sendEventRequest("#showsArchivedContent");
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
  $("#event-load-gif").css("display", "block");
  sendEventRequest(mode);

  showQuantityDisplay($eventSubheader, true, false);
}

$(document).on("click", "#artists .artist-row", function() {
  var sendRequestCallback = function() {
    // eventFromDate = now
    sendEventRequest("Upcoming", new Date());
  };

  var artistId = $(this).data("id");
  $.ajax({
    url: "/search/ajax/artist-info/",
    data: {
      id: artistId
    },
    dataType: "json",
    success: function(data) {
      if (data.template) {
        window.history.pushState(
          {
            html: "a",
            pageTitle: "b"
          },
          "",
          "?artist_pk=" + artistId + "#"
        );
        $("#musicianContent").hide();
        $(".artist-search-profile-container").html(data.template);
        $(".artist-search-profile-container")[0].style.display = "block";
        $("#artist-subheader").text("");
        $(".artist-search-profile-container .close-button-parent").show();
        $(".search-tabs").addClass("hidden");
        $(
          '*[data-toggle-tab-group="search-results"][data-toggle-tab="archived-shows"]'
        ).show();

        archivedEventDateFrom = archivedEventDateTo = null;
        upcomingEventDateFrom = upcomingEventDateTo = null;
        artist_pk = artistId;

        // Trick to filter both upcoming and archived when viewing artist profile.
        apply = true;
        archivedEventPageNum = upcomingEventPageNum = 1;
        sendEventRequest("Archived", null, null, sendRequestCallback);
      }
    }
  });
});

function toggleArrows() {
  if ($(".artist-column").length) {
    var max = parseInt($("#total-artist").text());
    var range = $("#artist-subheader")
      .text()
      .split("-");
    var current = parseInt(range[1]);

    var style = $("#artists").css("left");
    var columnWidth = parseInt(
      $(".artist-column")
        .first()
        .css("width")
        .replace("px", "")
    );
    var left = style.replace("px", "");
    var pseudoPage = parseInt(-left / columnWidth);
    if (!smallsConfig.display.isMobile()) {
      pseudoPage /= 4;
    }

    var lastPseudoPage = $(".artist-column").length - 1;
    if (!smallsConfig.display.isMobile()) {
      lastPseudoPage = Math.floor(lastPseudoPage / 4);
    }
    $(".left_arrow").css("visibility", pseudoPage == 0 ? "hidden" : "visible");
    $(".right_arrow").css("visibility", current >= max ? "hidden" : "visible");
  }
}

if ($("#artists .artist-column").length) {
  toggleArrows();
}

function sendEventRequest(mode, dateFrom, dateTo, callback) {
  var selector = "#shows" + mode + "Content";
  var utcDateFrom = null;
  var utcDateTo = null;
  var eventPageNum;

  var eventDateFrom;
  var eventDateTo;

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
  var searchFilters = {
    main_search: searchTerm,
    page: eventPageNum,
    order: eventOrderFilter,
    date_from: utcDateFrom ? utcDateFrom : null,
    date_to: utcDateTo ? utcDateTo : null,
    artist_pk: artist_pk ? artist_pk : null,
    partial: true,
    show_event_venue: show_event_venue ? show_event_venue : null,
    show_event_setTime: show_event_setTime ? show_event_setTime : null,
    is_upcoming: is_upcoming ? is_upcoming : null
  };
  if (venueFilter) {
    searchFilters["venue"] = venueFilter;
  }
  $.ajax({
    url: "/search/ajax/event/",
    data: searchFilters,
    dataType: "json",
    success: function(data) {
      if (data.template) {
        if (eventPageNum === 1) {
          var $eventSubheader = $("#archived-event-subheader");
          if (mode == "Upcoming") {
            $eventSubheader = $("#upcoming-event-subheader");
          }
          if (typeof data.showingResults !== "number") {
            $eventSubheader.text("0-0");
          } else if (data.showingResults < 24) {
            $eventSubheader.text("1-" + data.showingResults);
          } else {
            $eventSubheader.text("1-24");
          }
          console.log(data.showingResults);
          $eventSubheader.data("max-number", data.showingResults);
          $eventSubheader.data("left-number", 1);
          $eventSubheader.data("right-number", 24);
        }

        var selector = "#showsArchivedContent";
        if (mode == "Upcoming") {
          selector = "#showsUpcomingContent";
        }
        var $showsContainer = $(selector + " .shows-container");
        $("#events").removeClass("artist-loading-gif");
        var $eventSubHeaderFooter = "#archived-event-subheader-footer";
        var $totals = $("#archived-event-totals");
        if (mode == "Upcoming") {
          $totals = $("#upcoming-event-totals");
        }
        $totals.html(data.showingResults);
        if (apply || eventFilter) {
          apply = false;
          eventFilter = false;
          $showsContainer.html("");
        }
        var article = $(data.template).find("article");
        if (!article.length) {
          $showsContainer.html(data.template);
        }
        article.each(function(index) {
          $showsContainer.append($(this));
        });
        if (mode == "Upcoming") {
          upcomingEventMaxPageNum = data.numPages;
        } else {
          archivedEventMaxPageNum = data.numPages;
        }

        $("#event-load-gif").css("display", "none");
        var selector = "#load-more-archived-btn";
        if (mode == "Upcoming") {
          selector = "#load-more-upcoming-btn";
        }
        $(selector).toggle(data.numPages != eventPageNum);
        if (callback) {
          callback();
        }
      }
    }
  });
}

$(document).ready(function() {
  var instrument = getUrlParameter("instrument");
  if (instrument) {
    $(".instrument-btn").text(instrument);
  }
  artistInstrument = instrument ? instrument : "";
  searchTerm = getUrlParameter("q");
  searchTerm = searchTerm ? searchTerm.replace(/\+/g, " ") : "";
  artistSearchTerm = "";
  artistPageNum = archivedEventPageNum = upcomingEventPageNum = 1;
  artistMaxPageNum = archivedEventMaxPageNum = upcomingEventMaxPageNum = 2;
  apply = false;
  eventFilter = false;
  var maxPseudopage = 4;

  $("[name='q']").val(searchTerm);
  $("#artist-search").val("");

  var queryBusy = false;
  var animationBusy = false;

  $(document).on("click", ".artist-arrow-search", function() {
    var $that = $(this);

    var artistSubheader = $("#artist-subheader");

    if (animationBusy || queryBusy) {
      return;
    }

    // Get column width
    var style = $("#artists").css("left");
    var columnWidth = parseInt(
      $(".artist-column")
        .first()
        .css("width")
        .replace("px", "")
    );
    if (!smallsConfig.display.isMobile()) {
      columnWidth *= 4;
    }
    var left = parseInt(style.replace("px", ""));
    var offset = (document.documentElement.clientWidth / 100) * 88;
    if ($that.hasClass("right_arrow")) {
      offset = offset * -1;
    }

    animationBusy = true;
    $("#artists").animate(
      {
        left: left + offset + "px"
      },
      200,
      "linear",
      function() {
        toggleArrows();
        animationBusy = false;
      }
    );

    if ($that.hasClass("left_arrow")) {
      showQuantityDisplay(artistSubheader, false, true);
    }

    if ($that.hasClass("right_arrow")) {
      var pseudoPage = parseInt(-left / columnWidth);
      showQuantityDisplay(artistSubheader, true, true);
      if (
        artistPageNum !== artistMaxPageNum &&
        maxPseudopage - pseudoPage <= 4
      ) {
        artistPageNum += 1;
        $that.addClass("loading");
        queryBusy = true;
        sendArtistRequest(function() {
          maxPseudopage += 4;
          queryBusy = false;
          $that.removeClass("loading");
        });
      }
    }
  });

  $("#next-page-btn").click(function() {
    if (eventPageNum !== eventMaxPageNum) {
      eventPageNum += 1;
      sendEventRequest("");
    }
  });

  $("#events-filter").change(function() {
    eventFilter = true;
    eventOrderFilter = $(this).val();
    venueFilter = "all";
    archivedEventPageNum = 1;

    sendEventRequest("Archived");
  });

  $("#club-filter").change(function() {
    eventFilter = true;
    venueFilter = $(this).val();
    upcomingEventPageNum = 1;

    sendEventRequest("Upcoming");
  });

  $("#period-filter, #refine-period-filter").change(function() {
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

    var $filter = $(this);
    if ($filter.attr("id").indexOf("refine") > -1) {
      $("#search-date-picker-from-refine input").datepicker(
        "update",
        eventDateFrom
      );
      $("#search-date-picker-to-refine input").datepicker(
        "update",
        eventDateTo
      );
    } else {
      $("#search-date-picker-from input").datepicker("update", eventDateFrom);
      $("#search-date-picker-to input").datepicker("update", eventDateTo);
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
      artistSearchTerm = $("#artist-search").val();
      $(".container-list-article").addClass("artist-loading-gif");
      $("#artists").html("");
      $("#artist-subheader").data("left-number", 1);
      $("#artist-subheader").data("right-number", 24);
      sendArtistRequest(function() {
        $(".container-list-article").removeClass("artist-loading-gif");
        $("#artists").css("left", 0);
        toggleArrows();
      });
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
    artistInstrument = $(this).data("instrument");
    $(".instrument-btn").text(artistInstrument || "Instrument");
    artistPageNum = 1;

    $(".container-list-article").addClass("artist-loading-gif");
    $("#artists").html("");

    sendArtistRequest(function() {
      $(".container-list-article").removeClass("artist-loading-gif");
      $("#artists").css("left", 0);
      toggleArrows();
    });
    $(".instruments-container").css("display", "none");
  });

  ////////////////

  $(".datepicker-btn").bind("click", toggleDisplay);

  function toggleDisplay(event) {
    if ($(".datepicker-container").data("shown")) hide(event);
    else display();
  }

  function display() {
    var $datePickerContainer = $(".datepicker-container");
    $datePickerContainer.css({
      left: datePickerLeft,
      top: datePickerTop
    });
    $datePickerContainer
      .css("display", "flex")
      .hide()
      .fadeIn(500, function() {
        $(document).bind("click", hide);
        $(".datepicker-container").data("shown", true);
      });

    var $datePickerInput = $(datePickerInputSelector);
    $datePickerInput.click();
    $datePickerInput.prop("disabled", true);
    $datePickerInput.focus();
  }

  function hide(event) {
    var $target = $(event.target);
    if (
      $target.closest(".noclick").length == 0 &&
      !($target.hasClass("day") || $target.hasClass("year"))
    ) {
      $(".datepicker-container").fadeOut(500, function() {
        $(document).unbind("click", hide);
        $(".datepicker-container").data("shown", false);
      });
    }
  }
  ///////

  /////////////////////

  var $datePickerFrom = $("#search-date-picker-from input");
  $datePickerFrom.datepicker({
    format: "mm/dd/yyyy",
    autoclose: true,
    container: "#search-date-picker-from",
    showOnFocus: false,
    startDate: defaultFromDate,
    endDate: defaultToDate
  });

  if (setFromDate) {
    $datePickerFrom.datepicker("setDate", defaultFromDate);
    datePickerFromDate = new Date(defaultFromDate);
  }
  var lastYearSelected =
    "Thu Sep 30 1000 00:00:00 GMT-0300 (Uruguay Standard Time)";
  lastYearSelected = new Date(lastYearSelected);

  $datePickerFrom.on("changeDate", function(newDate) {
    datePickerFromDate = newDate.date;

    if (datePickerFromDate.getFullYear() != lastYearSelected.getFullYear()) {
      lastYearSelected = datePickerFromDate;
      lastYearSelected = new Date(lastYearSelected);
      console.log(lastYearSelected);
    }
    if (!datePickerToDate || datePickerFromDate > datePickerToDate) {
      datePickerToDate = datePickerFromDate;
      $datePickerTo.datepicker("setDate", datePickerToDate);
    }
    //$('#events-filter').val('oldest');
    //$("[value='oldest']").click();
    $("#search-date-picker-to input").click();
    $("#search-date-picker-to input").focus();
  });

  $datePickerFrom.on("click", function() {
    var dropdown = $("#search-date-picker .dropdown-menu");
    if (dropdown[0] && dropdown[0].style.display === "block") {
      $datePickerFrom.datepicker("hide");
    } else {
      $datePickerFrom.datepicker("show");
    }
  });

  //////////////////////

  var $datePickerTo = $("#search-date-picker-to input");
  $datePickerTo.datepicker({
    format: "mm/dd/yyyy",
    autoclose: false,
    container: "#search-date-picker-to",
    showOnFocus: false,
    startDate: defaultFromDate,
    endDate: defaultToDate
  });

  if (setToDate) {
    $datePickerTo.datepicker("setDate", defaultToDate);
    datePickerToDate = new Date(defaultToDate);
  }

  $datePickerTo.on("changeDate", function(newDate) {
    datePickerToDate = newDate.date;
  });

  $datePickerTo.on("click", function() {
    var dropdown = $("#search-date-picker .dropdown-menu");
    if (dropdown[0] && dropdown[0].style.display === "block") {
      $datePickerTo.datepicker("hide");
    } else {
      $datePickerTo.datepicker("show");
    }
  });

  ///////////

  // If only one result -> go to artist
  var $artists = $(".artist-row");
  if ($artists.length == 1) {
    $artists.click();
  } else {
    $("#artists").removeClass("invisible");
  }

  $(document).on(
    "click",
    ".artist-search-profile-container .close-button",
    function() {
      // If only one artist, assume back to search means
      // actually resetting search
      var $artists = $(".artist-row");
      if ($artists.length == 1) {
        window.location.href = "/search";
      } else {
        $("#musicianContent").show();
        $(".artist-search-profile-container").hide();
        $(".artist-search-profile-resume .close-button").show();
        $(".search-tabs").removeClass("hidden");
        artist_pk = null;
        $("#artist-search").val("");
        searchTerm = "";
        apply = true;
        archivedEventPageNum = 1;
        $(
          '[data-toggle-tab-group="search-results"][data-toggle-tab-target]'
        ).show();
        if (viewPortLength("width") < 1024) {
          $('[data-toggle-tab-group="search-results"][data-toggle-tab]').hide();
        }
        $(
          '[data-toggle-tab-group="search-results"][data-toggle-tab="musicians"]'
        ).show();
        sendEventRequest("#showsArchivedContent");
      }
    }
  );

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

    var $showsContainer = $(selector + " .shows-container");
    $showsContainer.html("");
    if ($(this).closest(".calendar").length > 0) {
      show_event_venue = true;
      show_event_setTime = true;
    }

    apply = true;
    toggleDisplay(this);
    $("#events").addClass("artist-loading-gif");
    sendEventRequest(mode, eventDateFrom, eventDateTo);

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

  $(".datepicker-reset").click(function() {
    $("#search-date-picker-from input")
      .val("")
      .datepicker("update");
    $("#search-date-picker-to input")
      .val("")
      .datepicker("update");
    datePickerFromDate =
      defaultFromDate !== undefined ? new Date(defaultFromDate) : null;
    datePickerToDate =
      defaultToDate !== undefined ? new Date(defaultToDate) : null;
    $("#search-date-picker-from input").click();
    $("#search-date-picker-from input").focus();
  });

  var $datePickerFromRefine = $("#search-date-picker-from-refine input");
  $datePickerFromRefine
    .datepicker({
      format: "mm/dd/yyyy",
      autoclose: true,
      container: "#search-date-picker-from-refine",
      showOnFocus: false,
      startDate: new Date()
    })
    .datepicker("setDate", "now");

  $datePickerFromRefine.on("changeDate", function(newDate) {
    eventDateFrom = newDate.date;
    //$('#events-filter').val('oldest');
    //$("[value='oldest']").click();
    $("#search-date-picker-to-refine input").click();
    $("#search-date-picker-to-refine input").focus();
  });

  $datePickerFromRefine.on("click", function() {
    var dropdown = $("#search-date-picker .dropdown-menu");
    if (dropdown[0] && dropdown[0].style.display === "block") {
      $datePickerFromRefine.datepicker("hide");
    } else {
      $datePickerFromRefine.datepicker("show");
    }
  });

  //////////////////////

  var $datePickerToRefine = $("#search-date-picker-to-refine input");
  $datePickerToRefine.datepicker({
    format: "mm/dd/yyyy",
    autoclose: false,
    container: "#search-date-picker-to-refine",
    showOnFocus: false,
    startDate: new Date()
  });

  $datePickerToRefine.on("changeDate", function(newDate) {
    eventDateTo = newDate.date;

    from =
      eventDateFrom.getMonth() +
      1 +
      "/" +
      eventDateFrom.getDate() +
      "/" +
      eventDateFrom.getFullYear();
    from = '<span class="from accent-color">' + from + "</span>";
    to =
      eventDateTo.getMonth() +
      1 +
      "/" +
      eventDateTo.getDate() +
      "/" +
      eventDateTo.getFullYear();
    to = '<span class="to accent-color">' + to + "</span>";

    $(".datepicker-btn").html("From " + from + " to " + to);
  });

  $datePickerToRefine.on("click", function() {
    var dropdown = $("#search-date-picker .dropdown-menu");
    if (dropdown[0] && dropdown[0].style.display === "block") {
      $datePickerToRefine.datepicker("hide");
    } else {
      $datePickerToRefine.datepicker("show");
    }
  });

  $(".refine").click(function() {
    $(".refine-overlay").show();
  });

  $(".closebtn").click(function() {
    $(".refine-overlay").hide();
  });

  $(".refine-apply").click(function() {
    apply = true;
    eventPageNum = 1;
    $(".refine-overlay").hide();
    sendEventRequest("#showsArchivedContent");
  });

  $(".reset-all").click(function() {
    $("#search-date-picker-from-refine input")
      .val("")
      .datepicker("update");
    $("#search-date-picker-to-refine input")
      .val("")
      .datepicker("update");
    eventDateFrom = eventDateTo = null;
  });

  /////////////////////

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
      upcomingEventDateTo = null;
      upcomingEventPageNum = 1;
      var eventDateFrom = upcomingEventDateFrom;
    } else {
      archivedEventDateFrom = datePickerFromDate;
      archivedEventDateTo = null;
      archivedEventPageNum = 1;
      var eventDateFrom = archivedEventDateFrom;
    }
    $("#calendar-date-range .title2").html(
      eventDateFrom.toLocaleDateString() + " - "
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
});

$(document).on(
  "click",
  ".artist-search-profile-container.pad-content .close-button",
  function() {
    if (!artistInstrument) {
      searchTerm = "";
      $(".instrument[data-instrument='']").click();
    }
  }
);

$(document).ready(function() {
  if (
    viewPortLength("width") < 1024 &&
    $("div[data-toggle-tab-target='archived-shows'").length != 0
  ) {
    $("div[data-toggle-tab-target='archived-shows'")[0].click();
    is_mobile = true;
  } else {
    is_mobile = false;
  }
  $("body").removeClass("hidden-body");
});

var startingArtist;
$(document).ready(function() {
  startingArtist = getUrlParameter("artist_pk");
  startingArtist = startingArtist ? startingArtist : "";
  if (startingArtist) {
    $(".search-tabs div[data-toggle-tab-target='archived-shows']").removeClass(
      "active"
    );
    $(".search-tabs div[data-toggle-tab-target='musicians']").addClass(
      "active"
    );
  }
});
