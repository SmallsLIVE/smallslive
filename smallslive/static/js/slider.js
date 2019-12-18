var scaling = 1.50;
//count
var currentSliderCount = 0;
var videoCount = $(".slider-container").children().length;
var showCount = 4;
var sliderCount = videoCount / showCount;
var controlsWidth = 40;
var scrollWidth = 0;
var isSlideAnimating = false;

$(document).ready(function() {
  /* This functionality applied to all sliders before we implemented owl carousel
  It applies now only to the artist strip since it can't be implemented with owl */
  initializeSlides();
});

var resizeTimeout;
$( window ).resize(function() {
  return
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function () {
      resetSlideScroll();
      initializeButtons();
    }, 300);
});

function resetSlideScroll() {
    // reset slider to initial position
  var $rows = $('.event-row');
  $rows.each(function () {
      $(this).animate({
          marginLeft: 0
      }, 300, function(){

      });
  });
}

function initializeButtons() {

  var $win = $(window);
  var $prev = $('div.slide-btn.slider.prev');
  var $next = $('div.slide-btn.slider.next');

  $prev.each(function () {
      $(this).css('visibility', 'hidden');
  });

  $next.each(function () {
      $(this).css('visibility', 'hidden');
      var $last = $(this).next().find('article').last();
      if (!$last.visible(false, false, 'horizontal')) {
          $(this).css('visibility', 'visible');
      }
  });
}

function initializeSlides() {
  resetSlideScroll();
  initializeButtons();
  bindSlideEvents();
}

function bindNextClick() {
  $(document).on('click', 'div.slide-btn.slider.next', function (event) {
    $(this).css('visibility', 'hidden');
    if (isSlideAnimating) {
      return false;
    }
    isSlideAnimating = true;
    var $next = $(this);
    var $row = $next.next();
    var $win = $(window);
    var vw = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    var padding = $row.innerWidth() - $row.width();
    var currentLeft = parseFloat($row.css("marginLeft"));
    var left = vw - currentLeft;
    $row.animate({
        marginLeft: -left + 2 * padding
    }, 400, function () {
        var $prev = $row.prev().prev();
        $prev.css('visibility', 'visible');
        $next.css('visibility', 'hidden');
        var $last = $row.find('article').last();
        if (!$last.visible()) {
            $next.css('visibility', 'visible');
            isSlideAnimating = false;
        } else {
          // retrieve more results
          // Rely on HTML indicating the name of a callback function
          var callback = $next.data('callback-name');
          if (callback && typeof window[callback] === "function") {
            window[callback]();
          }
          isSlideAnimating = false;
        }
    });
  });

}

function bindPrevClick() {
  $(document).on('click', 'div.slide-btn.slider.prev', function() {
    $(this).css('visibility', 'hidden');
    if (isSlideAnimating) {
      return false;
    }
    isSlideAnimating = true;
    var $prev = $(this);
    var $win = $(window);
    var $row = $prev.next().next();
    var $next = $prev.next();
    var vw = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    var padding = $row.innerWidth() - $row.width();
    var currentLeft = parseFloat($row.css("marginLeft"));
    var left = vw + currentLeft;
    $row.animate({
        marginLeft: left - 2 * padding
    }, 300, function () {
      $prev.css('visibility', 'hidden');
      $next.css('visibility', 'visible');
      isSlideAnimating = false;
      var $first = $row.find('article').first();
      if (!$first.visible()) {
          $prev.css('visibility', 'visible');
      }
    });
  });
}

function bindSlideEvents() {

  var $win = $(window);
  var $prev = $('div.slide-btn.slider.prev');
  var $next = $('div.slide-btn.slider.next');

  bindNextClick();
  bindPrevClick();
};