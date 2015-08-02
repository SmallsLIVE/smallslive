/* Bootstrap datepicker for Metrics */

var $datePicker = $('#metric-graph__date-picker input');
$datePicker.datepicker({
    format: 'MM // yyyy',
    minViewMode: "months",
    orientation: "top auto",
    startDate: new Date(2015, 7-1, 1),
    autoclose: true
});
$datePicker.on('changeMonth', function(d){
    var countsURL = "http://localhost:9000/event_counts/";
    var data = {
        month: d.date.getMonth() + 1,
        year: d.date.getFullYear(),
        event_id: eventID
    };
    $.get(countsURL, data, function(data, textStatus, jqXHR) {
        console.log(data);
        playsData.labels = data.dates;
        playsData.datasets[0].data = data.audio_plays_list;
        playsData.datasets[1].data = data.video_plays_list;
        playsData.datasets[2].data = data.total_plays_list;
        minsData.labels = data.dates;
        minsData.datasets[0].data = data.audio_seconds_list;
        minsData.datasets[1].data = data.video_seconds_list;
        minsData.datasets[2].data = data.total_seconds_list;
        var playsActive = $("#metric-graph__show__data-1").hasClass("active");
        if (playsActive) {
            drawGraph(playsData);
        } else {
            drawGraph(minsData);
        }

    });
});