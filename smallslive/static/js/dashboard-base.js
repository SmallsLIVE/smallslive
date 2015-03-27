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


/* Settings payment div reveal js */
$(document).ready(function () {
    $("#paypal-info").css("display","none");
    $(".radio-button").click(function(){
        if ($('input[name=payout_selection]:checked').val() == "Paypal") {
            $("#paypal-info").slideDown("fast"); //Slide Down Effect
            $.cookie('showTop', 'expanded'); //Add cookie 'ShowTop'
        }
        if ($('input[name=payout_selection]:checked').val() == "Check"){
            $("#paypal-info").slideUp("fast");
            $.cookie('showTop', 'collapsed'); //Add cookie 'ShowTop'
        }
     });
        var showTop = $.cookie('showTop');
        if (showTop == 'expanded') {
        $("#paypal-info").show("fast");
        $('input[name=payout_selection]:checked');
      } else {
        $("#paypal-info").hide("fast");
        $('input[name=payout_selection]:checked');
      }
})