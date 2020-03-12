searchBarTerm = "";

function sendSearchBarRequest() {
  $searchBar = $(".search-bar-autocomplete-container");
  $searchBar.css("display", "block");
  $.ajax({
    url: '/search/ajax/search-bar/',
    data: {
      'main_search': searchBarTerm
    },
    dataType: 'json',
    success: function (data) {
      $searchBar.removeClass("searching");
      if (data.template) {
        $searchBar.html(data.template);
      }
    }
  });
}

$(document).ready(function () {
    var delay = (function () {
        var timer = 0;
        return function (callback, ms, e) {
          var code = e.keyCode || e.which;
          clearTimeout(timer);
          // Do not trigger autocomplete if <enter> was pressed.
          if (code != 13) {
            timer = setTimeout(callback, ms);
          }
        };
    })();

    $("#desktop-search-bar, #search-bar").keyup(function (e) {
      $searchBar = $(".search-bar-autocomplete-container");
      $searchBar.html('');
      if (!$searchBar.hasClass("searching")) {
        $searchBar.addClass("searching");
      }
      delay(function () {
        searchBarTerm = $('#desktop-search-bar:visible, #search-bar input:visible').val();
        if (searchBarTerm.length > 1) {
          sendSearchBarRequest();
        }
        else {
          $searchBar.css("display", "none");
        }
      }, 1200, e);
    });

    $(".search-bar-autocomplete-container").on('focusout', function (e) {
      var lastResult = $('.search-result:last');

      // hide container after tabbing through the last search result
      if (e.target.innerText === lastResult[0].innerText) {
        setTimeout(function(){ $(".search-bar-autocomplete-container").css("display", "none"); }, 300);
      }
    });

    $("#desktop-search-bar").focusout(function (e) {
      var noResults = $('.no-result').length;

      // when search returns no results
      if (noResults == 6) {
        setTimeout(function(){ $(".search-bar-autocomplete-container").css("display", "none"); }, 300);
      }
    });
});

$(document).on('click', '.search-bar-more', function () {
    if ($('#search-bar input:visible').length) {
        $("#headerSearchForm").submit();
    } else {
        $(".search-input").submit();
    }
});

$(document).click(function(event) {
  $target = $(event.target);

  // hide search results when clicking outside its container
  if(!$target.closest('.search-bar-autocomplete-container').length &&
      $('.search-bar-autocomplete-container').is(":visible")) {
    setTimeout(function(){ $(".search-bar-autocomplete-container").css("display", "none"); }, 300);
  }
});
