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

$('#schedule__date-picker input').datepicker({
    format: 'MM // yyyy',
    minViewMode: "months",
    orientation: "top auto",
    autoclose: true,
});

$('#schedule__date-picker input').datepicker("setDate", new Date());


/* Header search autocomplete */

$.widget( "custom.catcomplete", $.ui.autocomplete, {
    _create: function() {
      this._super();
      this.widget().menu( "option", "items", "> :not(.ui-autocomplete-category)" );
    },
    _renderMenu: function( ul, items ) {
      var that = this,
        currentCategory = "";
      $.each( items, function( index, item ) {
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
    }
  });

$(function() {
    var searchData = [
      { label: "Accordion", category: "Instruments" },
      { label: "Alto Sax", category: "Instruments" },
      { label: "Banjo", category: "Instruments" },
      { label: "Baritone Sax", category: "Instruments" },
      { label: "Bass", category: "Instruments" },
      { label: "Bassoon", category: "Instruments" },
      { label: "Cello", category: "Instruments" },
      { label: "Clarinet", category: "Instruments" },
      { label: "Composer", category: "Instruments" },
      { label: "Conductor", category: "Instruments" },
      { label: "Dancer", category: "Instruments" },
      { label: "DJ", category: "Instruments" },
      { label: "Drums", category: "Instruments" },
      { label: "Female Vocalist", category: "Instruments" },
      { label: "Flute", category: "Instruments" },
      { label: "French Horn", category: "Instruments" },
      { label: "Guitar", category: "Instruments" },
      { label: "Harp", category: "Instruments" },
      { label: "Jazz Orchestra", category: "Instruments" },
      { label: "Leader", category: "Instruments" },
      { label: "Lute", category: "Instruments" },
      { label: "Male Vocalist", category: "Instruments" },
      { label: "MC", category: "Instruments" },
      { label: "Oboe", category: "Instruments" },
      { label: "Orchestra", category: "Instruments" },
      { label: "Organ", category: "Instruments" },
      { label: "Percussion", category: "Instruments" },
      { label: "Piano", category: "Instruments" },
      { label: "Poet", category: "Instruments" },
      { label: "Soprano Sax", category: "Instruments" },
      { label: "String Quartet", category: "Instruments" },
      { label: "Tap Dancer", category: "Instruments" },
      { label: "Tenor Sax", category: "Instruments" },
      { label: "Trombone", category: "Instruments" },
      { label: "Trumpet", category: "Instruments" },
      { label: "Vibraphone", category: "Instruments" },
      { label: "Viola", category: "Instruments" },
      { label: "Violin", category: "Instruments" },
      { label: "Vocalist", category: "Instruments" },
      { label: "Whistle", category: "Instruments" },
      { label: "Nasar Abadey", category: "Artists" },
      { label: "Carlos Abadie", category: "Artists" },
      { label: "Rez Abbasi", category: "Artists" },
      { label: "Brian Adler", category: "Artists" },
      { label: "Cyrille Aimee", category: "Artists" },
      { label: "Melissa Aldana", category: "Artists" },
      { label: "Aaron Alexander", category: "Artists" }
    ];

    $( "#header--search" ).catcomplete({
      delay: 0,
      source: searchData
    });
  });