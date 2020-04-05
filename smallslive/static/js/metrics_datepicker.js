/* Bootstrap datepicker for Metrics */
var drawGraph = function (data, label) {
    var ctx = document.getElementById("graph-canvas").getContext("2d");
    var graphPadding = 100;
    Chart.defaults.global.defaultFontFamily = "'Reem Kufi', sans-serif";
    Chart.defaults.global.defaultFontColor = 'black';
    var config = {
        type: 'line',
        data: data,
        options: {
            legend: {
                display: false
            },
            elements: {
              line: {
                  tension: 0
              }
            },
            layout: {
                padding: {
                    left: 10,
                    right: graphPadding,
                    top: graphPadding,
                    bottom: 10
                }
            },
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
                    },
                    gridLines: {
                        display: false
                    },
                    ticks: {
                        padding: 20,
                        fontSize: 12,
                        callback: function(value, index, values) {
                            return value.toUpperCase();
                        }
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'DATE DURATION',
                        padding: 50
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        suggestedMax: 10,
                        fontSize: 12,
                        padding: 15
                    },
                    gridLines: {
                        lineWidth: 4,
                        drawTicks: false,
                        color: 'white',
                        drawBorder: false
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'MINUTES PLAYED',
                        padding: 50
                    }
                }]
            }
        }
    };
    window.myLine = new Chart(ctx, config);
};

var checkPoints = function(chart, data, datasetIndex, remove) {
  chart.data.datasets[datasetIndex].pointBackgroundColor = [];
  chart.data.datasets[datasetIndex].pointRadius = [];
  for (var i = 1; i <= data.datasets[datasetIndex].data.length - 1; i++) {
    if (data.datasets[datasetIndex].data[i - 1] === data.datasets[datasetIndex].data[i]) {
      if (remove) {
        chart.data.datasets[datasetIndex].pointRadius[i] = 0;
      }
    } else {
      chart.data.datasets[datasetIndex].pointBackgroundColor[i] = 'black';
    }
  }
};

var updateGraph = function (data) {
    window.myLine.data = data;
    checkPoints(window.myLine, data, 0, true);
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

