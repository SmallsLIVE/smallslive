/* Solves issues with images filling div's. Adds a img.wide or img.tall class to img element. */

function makeImagesResponsive(selector) {
    $(selector).find('img').each(function () {
        var imgClass = (this.width / this.height > 1) ? 'wide' : 'tall';
        $(this).addClass(imgClass);
    })
}

$(window).load(function () {
    makeImagesResponsive('.container');
});

/* Adds swipe ability to Bootstrap event carousel */
$(document).ready(function () {
    $carousel = $("#upcoming-carousel");
    $carousel.swiperight(function () {
        $(this).carousel('prev');
    });
    $carousel.swipeleft(function () {
        $(this).carousel('next');
    });
});


/* Initialize Slick responsive carousel for Archive page */
$(document).ready(function () {
    $('.archive-carousel').slick({
        dots: true,
        slidesToShow: 4,
        slidesToScroll: 4,
        responsive: [
            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 3,
                    slidesToScroll: 3
                }
            },
            {
                breakpoint: 767,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 2
                }
            }
        ]
    });
});


/* Expanding details for schedule */
$(document).ready(function () {
    var active = 0;
    $(".day").click(function () {
        var position = $(this).data('position');
        $("#event-details-expanded").remove();
        $(".selected").removeClass('selected');
        if (position != active) {
            var that = this;
            var date = $(this).attr('data-date');

            $.get('/events/event_carousel_ajax/?date=' + date, function (data) {
                var template = data.content;

                $(that).addClass('selected');
                /* larger devices */
                var offset;
                if ($(window).width() > 768) {
                    offset = (4 - (position % 4)) % 4;
                }
                /* smaller devices */
                else {
                    offset = position % 2;
                }
                var new_position = position + offset;
                $('div[data-position=' + new_position + ']').after(template);
                active = position;
            })
        } else {
            active = 0;
        }
    });
});


/* Event data for the homepage */
$(document).ready(function () {
    var active = 0;
    $("body").on('change', '#homepage-date-select', function (d) {
        var date = $(this).val();
        var $carousel =
        $.get('/events/event_carousel_ajax/?template=home&date=' + date, function (data) {
                var template = data.content;
                $("#upcoming-events-fullsize").replaceWith(template);
                makeImagesResponsive('#upcoming-events-fullsize');
            });
    });
});

/* Bootstrap datepicker for Schedule page */

$datePicker = $('#schedule__date-picker input');
$datePicker.datepicker({
    format: 'MM // yyyy',
    minViewMode: "months",
    orientation: "top auto",
    autoclose: true
});
$datePicker.on('changeMonth', function(d){
    var month = d.date.getMonth() + 1;
    var year = d.date.getFullYear();
    window.location = '/events/schedule/' + year + '/' + month + '/';
});


/* Header search autocomplete */

$.widget( "custom.catcomplete", $.ui.autocomplete, {
    _create: function() {
      this._super();
      this.widget().menu( "option", "items", "> :not(.ui-autocomplete-category)" );
    },
    _renderMenu: function( ul, items ) {
        var that = this,
        currentCategory = "";
      $.each( items[0], function( index, item ) {
        var li;
        if ( item.category != currentCategory ) {
          ul.append( "<li class='ui-autocomplete-category'>" + item.category + "</li>" );
          currentCategory = item.category;
        }
        li = that._renderItemData( ul, item );
        if ( item.category ) {
          li.attr( "aria-label", item.category + " : " + item.label );
        }
      });
    },
    _renderItem: function( ul, item ) {
        return $( "<li>" )
            .attr( "data-value", item.value )
            .append('<a href="' + item.url + '">' + item.label + "</a>" )
            .appendTo( ul );
    }
  });

$(function() {
    $( "#header--search" ).catcomplete({
      delay: 500,
      source: '/events/search_autocomplete/'
    });
  });