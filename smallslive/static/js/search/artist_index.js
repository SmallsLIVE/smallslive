$(document).ready(function() {
  var $filter = $("#most-popular-filter");

  var setMostPopular = function(value) {
    var mostPopularFilter = $("#most-popular-container").find(".event-row");
    $.get(popularQueryUrl + "?range=" + value, function(data) {
      mostPopularFilter.replaceWith(data.content);
    });
  };

  $filter.on("change", function() {
    setMostPopular($filter.val());
  });

  if (typeof popularFilterDefaultValue != "undefined") {
    $filter.val(popularFilterDefaultValue);
    $filter.trigger("change");
  }

  $(".scroll-left").css("visibility", "initial");

  $("#a-z-search .white-border-button").click(function (event) {
    event.preventDefault();
    $("#a-z-search .white-border-button").removeClass("active");
    $(this).addClass("active");
    $("a-z-search").attr("selected-value", $(this).text());
    $("#artist-search").val($(this).text());
    localStorage.setItem('search_artist', $(this).text());
    $("#artist-search").change();
  });

  $("#a-z-search .white-border-button").keypress(function (e) {
    if (e.which == 13) {
      $(this).click();
    }
  });

  /* Handle nav scrolling */
  function handleScrolling(direction) {
    const maxScrollLeft =
      $("#a-z-search").get(0).scrollWidth - $("#a-z-search").get(0).clientWidth;
    let scrollF = setInterval(function() {
      $("#a-z-search").scrollLeft(
        $("#a-z-search").scrollLeft() + direction * 30
      );
    }, 10);
    setTimeout(() => {
      clearInterval(scrollF);
    }, 120);
    let scrollS = setInterval(function() {
      $("#a-z-search").scrollLeft(
        $("#a-z-search").scrollLeft() + direction * 10
      );
    }, 80);
    setTimeout(() => {
      clearInterval(scrollS);
    }, 320);
    setTimeout(function() {
      if ($("#a-z-search").scrollLeft() == 0) {
        $(".scroll-right").css("visibility", "initial");
        $(".scroll-left").css("visibility", "hidden");
      } else if (Math.floor($("#a-z-search").scrollLeft()) == maxScrollLeft) {
        $(".scroll-right").css("visibility", "hidden");
        $(".scroll-left").css("visibility", "initial");
      } else {
        $(".scroll-left").css("visibility", "initial");
        $(".scroll-right").css("visibility", "initial");
      }
    }, 310);
  }

  /* Listen for window resize to see if arrows need to be hidden */
  $(function() {
    var $window = $(window);
    var width = $window.width();
    var height = $window.height();

    setInterval(function() {
      if (width != $window.width() || height != $window.height()) {
        width = $window.width();
        height = $window.height();

        handleScrolling(1);
      }
    }, 300);
  });

  $(".scroll-right").click(() => {
    handleScrolling(1);
  });

  $(".scroll-left").click(() => {
    handleScrolling(-1);
  });

  $(".instruments-container .close-button").on("click", function() {
    $(this)
      .closest(".instruments-container")
      .hide();
  });

  $(".musicians-result").on("click", function() {
    $(".musicians-result.active").removeClass("active");
    $(this).addClass("active");

    $(".search-container.pad-content > section").hide();
    var $section = $("#" + $(this).data("type"));
    $section.show();
    $section.find(".slide-btn.next").css("visibility", "visible");
  });

  $("#a-z-refresh").click(() => {
    artistSearchTerm = "";
    $("#artist-search").val("");
    $("#artist-search").change();
    $("#a-z-search .white-border-button").removeClass("active");
    $("#a-z-refresh").css("background-color", "#fff");
    $("a-z-search").removeAttr("selected-value");
  });
});

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
        artistPk = artistId;

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
