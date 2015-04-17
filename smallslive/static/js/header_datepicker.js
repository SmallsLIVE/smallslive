/* Bootstrap datepicker for Schedule page */

var $datePicker = $('#header__date-picker input');
$datePicker.datepicker({
    format: 'DD, mm/dd/yyyy',
    orientation: "top auto",
    autoclose: true
});

var date = new Date();
$datePicker.datepicker("setDate", date);

$datePicker.on('changeDate', function(d){
    var date = d.date.getMonth()+1 + '/' + d.date.getDate() + '/' + d.date.getFullYear();
    var $carousel =
    $.get('/events/event_carousel_ajax/?template=home&date=' + date, function (data) {
        var template = data.content;
        $("#upcoming-events-fullsize").replaceWith(template);
        $('.upcoming-carousel').unslick();
        $('.upcoming-carousel').slick({
            dots: false,
            slidesToShow: 1,
            slidesToScroll: 1,
            arrows: false
        })
    });
});