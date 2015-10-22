$(document).ready(function () {
    $('.featured-metrics').slick({
        dots: false,
        slidesToShow: 4,
        slidesToScroll: 1,
        autoplay: false,
        autoplaySpeed: 8000,
        responsive: [
            {
                breakpoint: 6000,
                settings: {
                    slidesToShow: 4,
                    slidesToScroll: 4
                }
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

/* Legal section sign button transition */
$(document).ready(function () {
    $(".legal-page__button").click(function() {
        if ($(this).hasClass("sign")) {
            $(this).removeClass("sign");
            $(this).addClass("signed");
        }
    })
})

