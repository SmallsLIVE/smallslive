/* Bootstrap datepicker for Metrics */

var $datePicker = $('#metric-graph__date-picker input');
$datePicker.datepicker({
    format: 'MM // yyyy',
    minViewMode: "months",
    orientation: "top auto",
    autoclose: true
});
$datePicker.on('changeMonth', function(d){
    console.log("changed date");
});