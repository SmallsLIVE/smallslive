$(document).ready(function () {

  function getInitParams() {
    var $prev = $('div.today-left.prev');
    var $next = $('div.today-right.next');
    var margin = 20;
    var controlButtonWidth = ($prev[0] && $prev[0].clientWidth) ||
                             ($next[0] && $next[0].clientWidth);
    // variable declared in script section of template
    var startPosition = $('.tonight-events article.item.past').length;

    return {
      items: 3,
      stagePadding: controlButtonWidth + margin,
      margin: margin,
      startPosition: startPosition,
      slideBy: 3,
      dots: false,
      loop: false,
      rewind: false,
      responsive:{
        0:{
          items: 1,
          dots: false,
          margin:2,
          stagePadding: controlButtonWidth,
        },
        650:{
          items: 3,
          stagePadding: controlButtonWidth,
        },
        961:{
          items: 3
        }
      },
      onChanged: onChanged,
      onResized: onResized
    };
  }

  var owl = $('.upcoming-carousel').owlCarousel(getInitParams());

  function onResized(event) {
    owl.trigger('destroy.owl.carousel');
    owl = $('.upcoming-carousel').owlCarousel(getInitParams());
  }

  function onChanged(event) {

    if (event.item.count == 0) {
      return;
    }

    /* The carousel has to be positioned on a certain show depending on the current time.
    If there is only one show left, that's the only show that should appear on screen.
    The only way of doing this is having invisible items so it can be scrolled to the left
    that far. The problem is that we need only one hidden item on mobile, while we need
    two on desktop.
    On mobile, we can adjust by positioning the first placeholder item if the user
    tries to scroll too far to the right.
    */

    var placeholders = $(event.target).find('.item.placeholder').length;
    var items = event.item.count - placeholders;
    var item = event.item.index;
    var size = event.page.size;

    if (item == 0) {
      $('.today-left').hide();
    } else {
      $('.today-left').show();
    }

    if (items - item > size) {
      $('.today-right').show();
    } else {
      $('.today-right').hide();
    }

    if (!(typeof owl == "undefined")) {

      // Make sure that there is always at least one show visible on screen
      // by positioning on the first placeholder item.
      console.log("Current: ", event.item.index);
      console.log("items: ", items);
      if (event.item.index > items - 1) {
        owl.trigger('to.owl.carousel', items - 1);
      }
    }
  }

  $('.today-right').click(function() {
    owl.trigger('next.owl.carousel');
  })

  $('.today-left').click(function() {
    owl.trigger('prev.owl.carousel', [300]);
  })
});
