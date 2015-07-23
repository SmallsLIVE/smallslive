/* Bootstrap datepicker for Metrics */

var $datePicker = $('#metric-graph__date-picker input');
$datePicker.datepicker({
    format: 'MM // yyyy',
    minViewMode: "months",
    orientation: "top auto",
    startDate: "08/01/2015",
    autoclose: true
});
$datePicker.on('changeMonth', function(d){
    console.log("changed date");
});