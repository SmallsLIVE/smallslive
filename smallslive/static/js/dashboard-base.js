/* Initialize Slick responsive carousel for Dashboard home page */
$(document).ready(function () {
    $('.featured-metrics').slick({
        dots: false,
        slidesToShow: 4,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 3000,
        responsive: [
            {
                breakpoint: 6000,
                settings: "unslick"
            },
            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 2
                }
            },
            {
                breakpoint: 767,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                }
            }
        ]
    });
});



/* Make private/published button change */
//$(document).ready(function () {
//    $(".event-media__control").click(function() {
//        if ($(this).hasClass("make-private")) {
//            $(this).removeClass("make-private");
//            $(this).addClass("publish");
//            $(this).closest('.event-media__single').find('.event-media__single__icon').switchClass( "published", "private", 500, "easeInOutQuad" );
//        }
//        else {
//            $(this).removeClass("publish");
//            $(this).addClass("make-private");
//            $(this).closest('.event-media__single').find('.event-media__single__icon').switchClass( "private", "published", 500, "easeInOutQuad" );
//        }
//    })
//})


/* Legal section sign button transition */
$(document).ready(function () {
    $(".legal-page__button").click(function() {
        if ($(this).hasClass("sign")) {
            $(this).removeClass("sign");
            $(this).addClass("signed");
        }
    })
})


// jQuery for page scrolling feature - requires jQuery Easing plugin
$(function() {
    $('a.page-scroll').bind('click', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: $($anchor.attr('href')).offset().top
        }, 1500, 'easeInOutExpo');
        event.preventDefault();
    });
});