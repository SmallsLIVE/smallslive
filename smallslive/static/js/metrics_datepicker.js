/* Bootstrap datepicker for Metrics */
var drawGraph = function (data, label) {
    var ctx = document.getElementById("graph-canvas").getContext("2d");
    var config = {
        type: 'line',
        data: data,
        options: {
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
            multiTooltipTemplate: "<%if (label){%><%=datasetLabel%>: <%}%><%= value %> " + label,
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {
                        minUnit: 'day'
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        suggestedMax: 10
                    }
                }]
            }
        }
    };
    window.myLine = new Chart(ctx, config);
};

var updateGraph = function (data) {
    window.myLine.data = data;
    window.myLine.update();
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

