$(document).ready(function () {


  function getInitParams() {
    var $prev = $('div.catalog.prev');
    var $next = $('div.catalog.next');
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
          stagePadding: controlButtonWidth,
        },
        769:{
          items: 2,
          margin: 10,
          stagePadding: controlButtonWidth,
        },
        961:{
          items: 4,
        },
        1366: {
          items: 6
        }
      },
      onChanged: onChanged,
      onResized: onResized
    };
  }

  var owl = $('.catalog-carousel').owlCarousel(getInitParams());

  function onResized(event) {
    owl.trigger('destroy.owl.carousel');
    owl = $('.catalog-carousel').owlCarousel(getInitParams());
  }

  function onChanged(event) {

    if (event.item.count == 0) {
      return;
    }

    var items = event.item.count;
    var item = event.item.index;
    var size = event.page.size;

    if (item == 0) {
      $('.catalog.prev').hide();
    } else {
      $('.catalog.prev').show();
    }

    if (items - item > size) {
      $('.catalog.next').show();
    } else {
      $('.catalog.next').hide();
    }

  }

  $('.catalog.next').click(function() {
    owl.trigger('next.owl.carousel');
  })

  $('.catalog.prev').click(function() {
    owl.trigger('prev.owl.carousel', [300]);
  })
});
