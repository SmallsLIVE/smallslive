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

$.fn.unslick = function() {
        var _ = this;
        return _.each(function(index, element) {

          if (element.slick) {
            element.slick.destroy();
          }

        });
    };


/* Expanding details for schedule */
$(document).ready(function () {
    var activeEventId = 0;
    $(".day__event-title").click(function () {
        if ($(this).hasClass("event-active")) {
            $(this).toggleClass("event-active");
            $(this).parents('.day').toggleClass("day-active");
        }
        else {
            $(".event-active").removeClass("event-active");
            $(this).addClass("event-active");
            $('.day-active').removeClass("day-active");
            $(this).parents('.day').addClass("day-active");
        }
        var position = $(this).parents('.day').data('position');
        var eventId = $(this).attr('data-event-id');
        $("#event-details-expanded").slideUp(300, 'easeInOutCubic');
        if (eventId !== activeEventId) {
            var that = this;
            $.get('/events/schedule_carousel_ajax/' + eventId + '/', function (data) {
                var template = data.content;

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
                var last_box_position = $("div[data-position]").last().data('position');
                // special case if the last row isn't full
                if (new_position > last_box_position) {
                    new_position = last_box_position;
                }
                $("#event-details-expanded").remove();
                $('div[data-position=' + new_position + ']').after(template);
                $('#event-details-expanded').hide().slideDown( 400, 'easeInOutCubic', function() {
                    $(this).scrollIntoView();
                } );
                activeEventId = eventId;
                FillDivImg();
            });
        } else {
            activeEventId = 0;
        }
    });
});