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
  bindScroll();
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

function bindScroll() {

  var initialX, x, left,down, newX, currentLeft, dragging, diff, loadMore;

  $("#artists .event-row").mousedown(function (e) {
    //e.preventDefault();
    //e.stopPropagation();
    down = true;
    x = e.pageX;
    initialX = x;
    currentLeft = parseFloat($(this).css("marginLeft"));
    console.log('currentLeft: ' + currentLeft);

    //return false;
  });

  $(document).on("click", "#artists .event-row a", function (e) {
    if (dragging) {
      e.preventDefault();
      dragging = false;
    }
  });

  $("body").mousemove(function (e) {
    if (down) {
      dragging = true;
      newX = e.pageX;
      diff = x - newX;
      console.log('diff: ' + diff);
      var $row = $("#artists .event-row");
      currentLeft = parseFloat($row.css("marginLeft"));
      paddingLeft = parseFloat($row.css("paddingLeft"));
      currentLeft -= diff;
      if (currentLeft < 0) {
        var $articles = $row.find('article');
        var maxMargin = $articles.length * $articles.outerWidth(true) + paddingLeft - $(window).width();
        maxMargin *= -1;
        if (currentLeft < maxMargin) {
          currentLeft = maxMargin;
          loadMore = true;
        } else {
          loadMore = false;
        }

        $row.css("marginLeft", currentLeft);
      }
      x = newX;
    }
  });

  $(window).mouseup(function (e) {

    if (down) {

      // Adjust slide to the edge
      var $row = $("#artists .event-row");
      var currentLeft = parseFloat($row.css("marginLeft"));
      var article = $("article.event-display")[0];
      var articleWidth = parseFloat(getComputedStyle(article).width);
      articleWidth += parseFloat(getComputedStyle(article).marginRight);
      var factor = Math.abs(currentLeft / articleWidth);
      if (factor > 0.1) {
        if (initialX - x > 0) {
          offset = 1;
        } else {
          offset = 0;
        }
        var items = Math.floor(factor) + offset;
        currentLeft = items * articleWidth * -1;
        $row.animate({marginLeft: currentLeft}, 300, function () {
          if (offset === 1) {
            $("div.slide-btn.slider.prev").css("visibility", "visible");
          }
        });
      }
      // Check for more artists the same way as if the next button had been clicked.
      if (loadMore) {
        var $next = $("div.slide-btn.slider.next");
        var callback = $next.data('callback-name');
        if (callback && typeof window[callback] === "function") {
          window[callback]();
        }
      }
    }
    down = false;

  });
}