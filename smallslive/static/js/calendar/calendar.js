var searchTerm, artistSearchTerm, artistInstrument, artistPageNum, artistMaxPageNum, eventPageNum, eventMaxPageNum, eventOrderFilter, venueFilter, eventFilter, eventDateFrom, eventDateTo, apply, artist_pk;

function changePage(param) {
    eventPageNum = parseInt(param.getAttribute("data-page-number"));
    sendEventRequest();
}

function loadMoreEvents() {
    eventPageNum += 1;
    $("#load-more-btn").hide();
    $("#event-load-gif").css("display", "block");
    sendEventRequest();
}

function sendEventRequest() {
    if (eventDateFrom) {
        var utcDateFrom = eventDateFrom.getFullYear() + '/' + (eventDateFrom.getMonth() + 1) + '/' + eventDateFrom.getDate();
    }
    else {
        var utcDateFrom = null;
    }
    if (eventDateTo) {
        var utcDateTo = eventDateTo.getFullYear() + '/' + (eventDateTo.getMonth() + 1) + '/' + eventDateTo.getDate();
    }
    else {
        var utcDateTo = null;
    }

    $.ajax({
        url: '/search/ajax/event/',
        data: {
            'main_search': searchTerm,
            'page': eventPageNum,
            'order': eventOrderFilter,
            'venue': venueFilter,
            'date_from': utcDateFrom ? utcDateFrom : new Date(),
            'date_to': utcDateTo ? utcDateTo : null,
            'artist_pk': artist_pk ? artist_pk : null
        },
        dataType: 'json',
        success: function (data) {
            if (data.template) {
                $('#event-subheader').html(data.showingResults);
                $('#event-subheader-footer').html(data.showingResults);

                if (apply || eventFilter) {
                    apply = false;
                    eventFilter = false;
                    $('#events .shows-container').html('');
                }

                var article = $(data.template).find('article');
                if (!article.length) {
                    $('#events .shows-container').html(data.template);
                }
                article.each(function( index ) {
                    $('#events .shows-container').append($( this ));
                });
                eventMaxPageNum = data.numPages;

                $("#event-load-gif").css("display", "none");

                if (data.numPages != eventPageNum) {
                    $("#load-more-btn").show();
                } else {
                    $("#load-more-btn").hide();
                }
            }
        }
    });
}

$(document).ready(function () {
    searchTerm = getUrlParameter("q");
    if (searchTerm) {
        searchTerm = searchTerm.replace(/\+/g, ' ');
    } else {
        searchTerm = '';
    }
    artistSearchTerm = "";
    artistInstrument = "";
    artistPageNum = eventPageNum = 1;
    artistMaxPageNum = eventMaxPageNum = 2;
    eventOrderFilter = "newest";
    venueFilter = "all";
    apply = false;
    eventFilter = false;

    $("#next-page-btn").click(function () {
        if (eventPageNum !== eventMaxPageNum) {
            eventPageNum += 1;

            sendEventRequest();
        }
    });

    $('#period-filter').change(function () {
        eventFilter = true;

        if ($(this).val() == 'All Upcoming') {
            eventDateTo = null;
            eventDateFrom = new Date();
        }
        else if ($(this).val() == 'One Day') {
            eventDateTo = new Date((new Date()).getTime() + 1 * 24 * 60 * 60 * 1000);
            eventDateFrom = new Date();
            $("#search-date-picker-from input").datepicker("update", eventDateFrom);
            $("#search-date-picker-to input").datepicker("update", eventDateTo);
        }
        else if ($(this).val() == 'One Week') {
            eventDateTo = new Date((new Date()).getTime() + 7 * 24 * 60 * 60 * 1000);
            eventDateFrom = new Date();
            $("#search-date-picker-from input").datepicker("update", eventDateFrom);
            $("#search-date-picker-to input").datepicker("update", eventDateTo);
        }
        else if ($(this).val() == 'One Month') {
            eventDateTo = new Date((new Date()).getTime() + 31 * 24 * 60 * 60 * 1000);
            eventDateFrom = new Date();
            $("#search-date-picker-from input").datepicker("update", eventDateFrom);
            $("#search-date-picker-to input").datepicker("update", eventDateTo);
        }

        eventPageNum = 1;
        sendEventRequest();
    });

    $('#club-filter').change(function () {
        eventFilter = true;
        venueFilter = $(this).val();
        eventPageNum = 1;

        sendEventRequest();
    });

    var delay = (function () {
        var timer = 0;
        return function (callback, ms) {
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
        };
    })();

    ////////////////

    $('.datepicker-btn').bind("click", ToggleDisplay);

    function ToggleDisplay() {
        if ($(".datepicker-container").data('shown'))
            hide();
        else 
            display();
    }

    function display() {
        $(".datepicker-container").css("display", "flex").hide().fadeIn(500, function() {
            $(document).bind("click", hide);
            $(".datepicker-container").data('shown', true)}); 

        $("#search-date-picker-to input").click();
        $("#search-date-picker-to input").focus();    
    }

    function hide() {   
        if (($(window.event.toElement).closest('.noclick').length == 0) &&
        (!($(window.event.toElement).hasClass("day") || $(window.event.toElement).hasClass("year")))) {
            $(".datepicker-container").fadeOut(500, function () {
                $(document).unbind("click");
                $(".datepicker-container").data('shown', false);
            });
        }
    }

    /////////////////////

    var $datePickerFrom = $('#search-date-picker-from input');
    $datePickerFrom.datepicker({
        format: 'mm/dd/yyyy',
        autoclose: true,
        container: '#search-date-picker-from',
        showOnFocus: false,
        startDate: new Date()
    }).datepicker('setDate', 'now');

    $datePickerFrom.on('changeDate', function (newDate) {
        eventDateFrom = newDate.date;
        //$('#events-filter').val('oldest');
        //$("[value='oldest']").click();
        $("#search-date-picker-to input").click();
        $("#search-date-picker-to input").focus();
    });

    $datePickerFrom.on('click', function () {
        var dropdown = $('#search-date-picker .dropdown-menu');
        if (dropdown[0] && dropdown[0].style.display === 'block') {
            $datePickerFrom.datepicker('hide');
        } else {
            $datePickerFrom.datepicker('show');
        }

    });

    //////////////////////

    var $datePickerTo = $('#search-date-picker-to input');
    $datePickerTo.datepicker({
        format: 'mm/dd/yyyy',
        autoclose: false,
        container: '#search-date-picker-to',
        showOnFocus: false,
        startDate: new Date()
    });

    $datePickerTo.on('changeDate', function (newDate) {
        eventDateTo = newDate.date;

        from = (eventDateFrom.getMonth() + 1) + '/' + eventDateFrom.getDate() + '/' + eventDateFrom.getFullYear();
        from = '<span class="accent-color">' + from + '</span>';
        to = (eventDateTo.getMonth() + 1) + '/' + eventDateTo.getDate() + '/' + eventDateTo.getFullYear();
        to = '<span class="accent-color">' + to + '</span>';

        $(".datepicker-btn").html("From " + from + " to " + to);
    });

    $datePickerTo.on('click', function () {
        var dropdown = $('#search-date-picker .dropdown-menu');
        if (dropdown[0] && dropdown[0].style.display === 'block') {
            $datePickerTo.datepicker('hide');
        } else {
            $datePickerTo.datepicker('show');
        }

    });

    ///////////

    $("#apply-button").click(function () {
        apply = true;
        eventPageNum = 1;
        $(".datepicker-container").hide();
        sendEventRequest();
    });

    $(".datepicker-reset").click(function () {
        $('#search-date-picker-from input').val("").datepicker("update");
        $('#search-date-picker-to input').val("").datepicker("update");
        eventDateFrom = eventDateTo = null;
        $("#search-date-picker-from input").click();
        $("#search-date-picker-from input").focus();
    });
});
