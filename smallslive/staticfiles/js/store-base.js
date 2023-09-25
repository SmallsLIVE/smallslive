/* Initialize store landing page carousel */
$(document).ready(function () {
    $('#store-featured-music__carousel').slick({
        dots: false,
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: false,
        prevArrow: "store-featured-music__carousel__control__left",
        nextArrow: "store-featured-music__carousel__control__right"
    });

    $(".store-featured-music__carousel__indicators").on('click', 'li', function () {
        slideIndex = $(this).attr("data-slickPosition");
        console.log(this);
        var slider = $('#store-featured-music__carousel');
        slider[0].slick.slickGoTo(slideIndex);
        $(".store-featured-music__carousel__indicators li.active").toggleClass("active");
        $(this).toggleClass("active");
    });
})

$('#store-featured-music__carousel').on('afterChange', function(event, slick, currentSlide){
  $(".store-featured-music__carousel__indicator.active").toggleClass( "active" );
    var indicator = $(".store-featured-music__carousel__indicators li");
    $(indicator[currentSlide]).toggleClass( "active" );
});

$('#store-featured-music__carousel__control__left').click(function(){
  var slider = $('#store-featured-music__carousel');
  slider[0].slick.slickPrev();
})

$('#store-featured-music__carousel__control__right').click(function(){
  var slider = $('#store-featured-music__carousel');
  slider[0].slick.slickNext();
})


/* Initialize store single product image carousel */
$(document).ready(function () {

    $('#store-single__item__images__carousel').slick({
        dots: false,
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: false
    });

    $(".store-single__item__images__thumbnails").on('click', 'li', function () {
        slideIndex = $(this).attr("data-slickPosition");
        console.log(this);
        var slider = $('#store-single__item__images__carousel');
        slider[0].slick.slickGoTo(slideIndex);
        $(".store-single__item__images__thumbnails li.active").toggleClass("active");
        $(this).toggleClass("active");
    });
});

$('#store-single__item__images__carousel').on('afterChange', function(event, slick, currentSlide){
  $(".store-single__item__images__thumbnail.active").toggleClass( "active" );
    var indicator = $(".store-single__item__images__thumbnails li");
    $(indicator[currentSlide]).toggleClass( "active" );
});


$(document).ready(function () {
    $("#store-nav-cat-expand").click(function () {
        $(this).toggleClass("active");
        $("#store-nav-cat").slideToggle();
    });

    $("select.store-add-small__options").on("change", function(val) {
        var selectedPrice = $(this).find(":selected").data('price');
        $(this).closest('.store-list-item').find('.store-list-item__price').text(selectedPrice);
    });

    $("select.store-add-large__options").on("change", function(val) {
        var selectedPrice = $(this).find(":selected").data('price');
        $(this).closest('.store-featured-music__single').find('.store-featured-music__single__price').text(selectedPrice);
    })
});