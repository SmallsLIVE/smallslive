/* Bootstrap datepicker for Metrics */
var drawGraph = function (data, label) {
    var ctx = document.getElementById("graph-canvas").getContext("2d");
    window.myLine = new Chart(ctx).Line(data, {
        responsive: true,
        maintainAspectRatio: false,
        bezierCurve: false,
        bezierCurveTension: 0.25,
        scaleShowVerticalLines: false,
        scaleOverride: false,
        showScale: true,
        pointDotRadius: 6,
        datasetStrokeWidth: 4,
        scaleFontSize: 10,
        scaleFontStyle: "bold",
        scaleFontColor: "#999",
        multiTooltipTemplate: "<%if (label){%><%=datasetLabel%>: <%}%><%= value %> " + label
    });
};

var $datePicker = $('#metric-graph__date-picker input');
$datePicker.datepicker({
    format: 'MM // yyyy',
    minViewMode: "months",
    orientation: "top auto",
    startDate: new Date(2015, 7-1, 1),
    autoclose: true
});

var date = new Date();
$datePicker.datepicker("setDate", date);

