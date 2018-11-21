var scaling = 1.50;
//count
var currentSliderCount = 0;
var videoCount = $(".slider-container").children().length;
var showCount = 4;
var sliderCount = videoCount / showCount;
var controlsWidth = 40;
var scrollWidth = 0;

jQuery.expr.filters.offscreen = function(el) {
  var rect = el.getBoundingClientRect();
  return (
           (rect.x + rect.width) < 0
             || (rect.y + rect.height) < 0
             || (rect.x > window.innerWidth || rect.y > window.innerHeight)
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

function init(){

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

function controls(){

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

    $(document).on('click', 'div.slide-btn.next', function(){
        var $next = $(this);
        var $win = $(window);
        var vw = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
        var margin = vw * 0.0078;
        var frameWidth = vw - $next.width() * 2;
        var $row = $next.next();
        var left = - parseFloat($row.css('marginLeft')) + frameWidth;
        $row.animate({
            marginLeft: - left
        }, 400, function(){
            var $prev = $row.prev().prev();
            $prev.css('visibility', 'visible');
            $next.css('visibility', 'hidden');
            var $last = $row.find('article').last();
            if ($last.is(':offscreen')) {
                $next.css('visibility', 'visible');
            }
        });
    });

    $(document).on('click', 'div.slide-btn.prev', function(){
        var $prev = $(this);
        var $win = $(window);
        var $row = $prev.next().next();
        var $next = $prev.next();
        scrollWidth = 0;
        $row.animate({
            marginLeft: + scrollWidth
        }, 300, function(){
            $prev.css('visibility', 'hidden');
            $next.css('visibility', 'hidden');
            var $last = $row.find('article').last();
            console.log($last)
            if ($last.is(':offscreen')) {
                $next.css('visibility', 'visible');
            }
        });
    });
};