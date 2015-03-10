/* Solves issues with images filling div's. Adds a img.wide or img.tall class to img element. */

function makeImagesResponsive(selector) {
    $(selector).find('img').each(function () {
        var imgClass = (this.width / this.height > 1) ? 'wide' : 'tall';
        $(this).addClass(imgClass);
    });
}

$(window).load(function () {
    makeImagesResponsive('.container');
});

$(function() {
    // setTimeout() function will be fired after page is loaded
    // it will wait for 5 sec. and then will fire
    // $("#successMessage").hide() function
    setTimeout(function() {
        $(".alert-dismissible").hide(500)
    }, 3000);
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
                makeImagesResponsive(".container");
            });
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


/* Header search autocomplete */

$.widget( "custom.catcomplete", $.ui.autocomplete, {
    _create: function() {
      this._super();
      this.widget().menu( "option", "items", "> :not(.ui-autocomplete-category)" );
    },
    _renderMenu: function( ul, items ) {
        var that = this,
        currentCategory = "";
        console.log(items);

        $.each ( items[1], function( index, item ) {
            var li;
            if ( item.category != currentCategory ) {
                if ( currentCategory != "" && items[0][currentCategory] > 5 ) {
                    ul.append ( "<li class='ui-autocomplete-more-count'><a href='/search/" + currentCategory + "/?q=" + that.term + "'>+" + ( items[0][currentCategory] - 5 ) + " more</a></li>" );
                }
                currentCategory = item.category;
                ul.append ( "<li class='ui-autocomplete-category'><span class='name'>" + item.category + "</span><span class='results-count'>(" + items[0][currentCategory] + ")</span></li>" );
            }
            li = that._renderItemData( ul, item );
            if ( item.category ) {
              li.attr( "aria-label", item.category + " : " + item.label );
            }
        });
        if ( currentCategory != "" && items[0][currentCategory] > 5 ) {
                    ul.append ( "<li class='ui-autocomplete-more-count'><a href='/search/" + currentCategory + "/?q=" + that.term + "'>+" + ( items[0][currentCategory] - 5 ) + " more</a></li>" );
                }
    },
    _renderItem: function( ul, item ) {
        return $( "<li>" )
            .attr( "data-value", item.value )
            .append('<a href="' + item.url + '"><span class="name">' + item.label + '</span><span class="sublabel">' + item.sublabel + "</span></a>" )
            .appendTo( ul );
    }
  });

$(function() {
    $( ".search__input" ).catcomplete({
      delay: 500,
      source: '/search/autocomplete/',
      minLength: 3,
      appendTo: '#header-search-container'
    });
  });

/* Header search focus effect */
$(document).ready(function () {
    $('.search__input').on('blur', function(){
        $('.navigation__item').removeClass('search-active');
    }).on('focus', function(){
        $('.navigation__item').addClass('search-active');
    });
});
