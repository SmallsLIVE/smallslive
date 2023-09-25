function initializeRecentlyCarousel() {

  function getInitParams() {
    var $prev = $('div.recently.prev');
    var $next = $('div.recently.next');
    var margin = 10;
    var controlButtonWidth = ($prev[0] && $prev[0].clientWidth) ||
                             ($next[0] && $next[0].clientWidth);
    return {
      items: 3,
      stagePadding: margin + controlButtonWidth,
      margin: margin,
      startPosition: 0,
      slideBy: 3,
      dots: false,
      loop: false,
      rewind: false,
      responsive:{
        0:{
          items: 2,
          dots: false,
          margin:2,
        },
        769:{
          items: 2,
          margin: 10,
        },
        961:{
          items: 6,
        },
        1366: {
          items: 8,
        }
      },
      onChanged: onChanged,
      onResized: onResized
    };
  }

  var owl = $('.recently-carousel').owlCarousel(getInitParams());

  function onResized(event) {
    owl.trigger('destroy.owl.carousel');
    owl = $('.recently-carousel').owlCarousel(getInitParams());
  }

  function onChanged(event) {

    if (event.item.count == 0) {
      return;
    }

    var items = event.item.count;
    var item = event.item.index;
    var size = event.page.size;

    if (item == 0) {
      $('.recently.prev').hide();
    } else {
      $('.recently.prev').show();
    }

    if (items - item > size) {
      $('.recently.next').show();
    } else {
      $('.recently.next').hide();
    }

  }

  $('.recently.next').click(function() {
    owl.trigger('next.owl.carousel');
  })

  $('.recently.prev').click(function() {
    owl.trigger('prev.owl.carousel', [300]);
  })
}
