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
  const alphabet = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z"
  ];
  buttons = {};
  alphabet.map(letter => {
    buttons[letter] = document.createElement("div");
    buttons[letter].setAttribute("tabindex", 0);
    $(buttons[letter])
      .addClass("white-border-button")
      .html(letter)
      .appendTo($("#a-z-search"))
      .click(() => {
        $("#a-z-search .white-border-button").css(
          "background-color",
          "#f0f0eb"
        );
        $(buttons[letter]).css("background-color", "#fff");
        if (searchTerm.trim() != "") {
          searchTerm = "";
          sendArtistRequest(() => {
            $("#artist-search").val($(buttons[letter]).text());
            $("#artist-search").change();
          });
        } else {
          $("#artist-search").val($(buttons[letter]).text());
          $("#artist-search").change();
        }
      })
      .keypress(e => {
        if (e.keyCode == 13) {
          $(buttons[letter]).click();
        }
      });
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
});
