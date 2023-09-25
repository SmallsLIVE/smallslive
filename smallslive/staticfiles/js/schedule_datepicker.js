/* Bootstrap datepicker for Schedule page */

var $datePicker = $('#schedule__date-picker input');
$datePicker.datepicker({
    format: 'MM // yyyy',
    orientation: "top auto",
    autoclose: true
});
$datePicker.on('changeMonth', function(d){
    var month = d.date.getMonth() + 1;
    var year = d.date.getFullYear();
    window.location = '/events/calendar/' + year + '/' + month + '/';
});