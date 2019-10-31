
$(document).ready(function () {
  var pages = ["venues-location", "passes-tickets", "hours-policies", "foundation", "archive", "streaming", "catalog", "about-us"];

  $(window).scroll(function () {

    for (pageButton of pages){
      $("#" + pageButton + " a").css('color', 'black');
    }

    for (page of pages) {
      var element = document.querySelector('#' + page + '-tab');
      var position = element.getBoundingClientRect();
      // checking for partial visibility
      if(position.top < window.innerHeight && position.bottom >= 0) {
        $("#" + page + " a").css('color', 'red');
        return;
      }
    }

  });

  $('.white-border-button').click(function (e) {
    var id = $(this).attr('id');

    $('html, body').animate(
      {
        scrollTop: $("#" + id + "-tab").offset().top + 10
      },
      500,
      'linear'
    );
  });

  $('.expand').click(function (e) {
    $(e.target).parent().parent().parent().parent().toggleClass('closed');
    $(e.target).parent().parent().parent().toggleClass('closed');
    $(e.target).toggleClass('closed');
  });

  var hash = window.location.hash;
  var ids = hash.split("#");
  var filtered = ids.filter(function (el) {
    return el != "";
  });

  if (filtered.length == 1) {
    var id = filtered[0];
    if ($("#contact-and-info-index").visible()) {
      $("#" + id).click();
    } else {
      $("#mobile-" + id).click();
      $('html, body').animate(
        {
          scrollTop: $("#" + id + "-tab").offset().top - 100
        },
        500,
        'linear'
      );
    }
  }

})