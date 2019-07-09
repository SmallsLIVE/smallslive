var scaling = 1.50;
//count
var currentSliderCount = 0;
var videoCount = $(".slider-container").children().length;
var showCount = 4;
var sliderCount = videoCount / showCount;
var controlsWidth = 40;
var scrollWidth = 0;



function outOfBounds(viewPort) {
    var browserName = navigator.userAgent.toLowerCase(); 
    if (browserName.indexOf('safari') != -1) { 
        windowOrientation = (window.orientation, 90)
        switch (windowOrientation) {  
            case 0:  
                if( viewPort === "height" )
                    return window.innerWidth
                else if( viewPort === "width" )
                    return window.innerHeight
                break;
                
            case 180:  
                if( viewPort === "height" )
                    return window.innerWidth
                else if( viewPort === "width" )
                    return window.innerHeight
                break;
            
            case -90:  
                if( viewPort === "height" )
                    return window.innerHeight
                else if( viewPort === "width" )
                    return window.innerWidth
                break;
            
            case 90:                  
                if( viewPort === "height" )
                    return window.innerHeight
                else if( viewPort === "width" )
                    return window.innerWidth
                break; 
        }
    }else{
        if( viewPort === "height" )
            return window.innerHeight
        else if( viewPort === "width" )
            return window.innerWidth
    }
}
jQuery.expr.filters.offscreen = function(el) {
    var rect = el.getBoundingClientRect();
    return (
             (rect.x + rect.width) < 0
               || (rect.y + rect.height) < 0
               || (rect.top > outOfBounds("height") || rect.right > outOfBounds("width") )
           );
};

$(document).ready(function(){
    init();
    // controls
    controls();
});

var resizeTimeout;
$( window ).resize(function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(init, 300);
});

function init() {

    // reset slider to initial position
    var $rows = $('.event-row');
    $rows.each(function () {
        $(this).animate({
            marginLeft: 0
        }, 300, function(){

        });
    });

    var $win = $(window);
    var $prev = $('div.slide-btn.prev');
    var $next = $('div.slide-btn.next');

    $prev.each(function () {
        $(this).css('visibility', 'hidden');
    });

    $next.each(function () {
        $(this).css('visibility', 'hidden');
        var $last = $(this).next().find('article').last();
        if ($last.is(':offscreen')) {
            $(this).css('visibility', 'visible');
        }
    });
}

function controls() {

  var $win = $(window);
  var $prev = $('div.slide-btn.prev');
  var $next = $('div.slide-btn.next');

  $(document).on('click', 'div.slide-btn.next', function () {
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
          if ($last.is(':offscreen')) {
              $next.css('visibility', 'visible');
          } else {
            // retrieve more results
            // Rely on HTML indicating the name of a callback function
            var callback = $next.data('callback-name');
            if (callback && typeof window[callback] === "function") {
              window[callback]();
            }
          }
      });
  });

  $(document).on('click', 'div.slide-btn.prev', function(){
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
      }, 300, function(){
          $prev.css('visibility', 'hidden');
          $next.css('visibility', 'visible');
          var $first = $row.find('article').first();
          if ($first.is(':offscreen')) {
              $prev.css('visibility', 'visible');
          }
      });
  });
};