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
          dots: false
        },
        769:{
          items: 2,
          stagePadding: 60
        },
        961:{
          items: 3
        }
      },
      onChanged: onChanged,
      onResized: onResized
    };
  }

  var owl = $('.owl-carousel').owlCarousel(getInitParams())

  function onResized(event) {
    owl.trigger('destroy.owl.carousel');
    owl = $('.owl-carousel').owlCarousel(getInitParams());
  }

  function onChanged(event) {

    if (event.item.count == 0) {
      return;
    }

    //Count placeholder items
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

  }

  $('.today-right').click(function() {
    owl.trigger('next.owl.carousel');
  })

  $('.today-left').click(function() {
    owl.trigger('prev.owl.carousel', [300]);
  })
});
