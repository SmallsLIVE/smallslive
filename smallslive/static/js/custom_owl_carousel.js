$(document).ready(function () {
  function getInitParams() {
    var $prev = $('div.today-left.prev');
    var $next = $('div.today-right.next');
    var margin = 20;
    var controlButtonWidth = ($prev[0] && $prev[0].clientWidth) ||
                             ($next[0] && $next[0].clientWidth);
    // variable declared in script section of template
    var startPosition = typeof events_finished == 'undefined' ? 0 : events_finished;

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
          dots: true
        },
        550:{
          items: 2,
          slideBy: 2
        },
        960:{
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
    var items = event.item.count;
    var item = event.item.index;
    var size = event.page.size;

    if (item  == items - size) {
      // end
      $('.today-right').hide();
      $('.today-left').show();
    } else if (item != items - size && item != 0) {
      // middle
      $('.today-right').show();
      $('.today-left').show();
    } else if (item  == 0) {
      // beginning
      $('.today-right').show();
      $('.today-left').hide();
    }
  }

  $('.today-right').click(function() {
    owl.trigger('next.owl.carousel');
  })

  $('.today-left').click(function() {
    owl.trigger('prev.owl.carousel', [300]);
  })
});

