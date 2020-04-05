function initializePopularCarousel() {

  function getInitParams() {
    var $prev = $('div.popular.prev');
    var $next = $('div.popular.next');
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

  var owl = $('.popular-carousel').owlCarousel(getInitParams());

  function onResized(event) {
    owl.trigger('destroy.owl.carousel');
    owl = $('.popular-carousel').owlCarousel(getInitParams());
  }

  function onChanged(event) {

    if (event.item.count == 0) {
      return;
    }

    var items = event.item.count;
    var item = event.item.index;
    var size = event.page.size;

    if (item == 0) {
      $('.popular.prev').hide();
    } else {
      $('.popular.prev').show();
    }

    if (items - item > size) {
      $('.popular.next').show();
    } else {
      $('.popular.next').hide();
    }

  }

  $('.popular.next').click(function() {
    owl.trigger('next.owl.carousel');
  })

  $('.popular.prev').click(function() {
    owl.trigger('prev.owl.carousel', [300]);
  })

};
