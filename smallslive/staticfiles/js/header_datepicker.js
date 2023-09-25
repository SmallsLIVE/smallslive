/* Bootstrap datepicker for Schedule page */
var date = new Date();
var startDate = new Date(date.getFullYear(), date.getMonth(), 1);
var endDate = new Date(date.getFullYear(), date.getMonth() + 1, 0);


var $datePicker = $('#header__date-picker input');
$datePicker.datepicker({
    format: 'DD, m/d/yyyy',
    orientation: "top auto",
    autoclose: true,
    datesDisabled: window.disabledDates
});

$datePicker.datepicker("setDate", date);

$datePicker.on('changeDate', function(d){
    var date = d.date.getMonth()+1 + '/' + d.date.getDate() + '/' + d.date.getFullYear();
    var $carousel = $('#upcoming-carousel');
    $.get('/events/event_carousel_ajax/?template=home&date=' + date, function (data) {
        var template = data.content;
        var $eventTimes = $(template).find('.event-details__timeslot');
        $('.event-select__slots').empty();
        $eventTimes.each(function(index) {
            var slot = '<li data-slickPosition="' + index + '"';
            if (index === 0) {
                slot += ' class="active"';
            }
            slot += '>' + $(this).text() + '</li>';
            $('.event-select__slots').append(slot);
        });
        $carousel.slick("unslick");
        $carousel.replaceWith(template);
        $('#upcoming-carousel').slick({
            dots: false,
            slidesToShow: 1,
            slidesToScroll: 1,
            arrows: false
        });
        FillDivImg();
        CarouselSlideHeight();
    });
});