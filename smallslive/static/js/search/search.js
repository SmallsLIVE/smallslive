var searchTerm, artistSearchTerm, artistInstrument, artistPageNum, artistMaxPageNum, eventPageNum, eventMaxPageNum, eventOrderFilter, eventFilter, eventDateFrom, eventDateTo, apply;

function sendArtistRequest() {
    $.ajax({
        url: '/search/ajax/artist/',
        data: {
            'main_search': searchTerm,
            'artist_search': artistSearchTerm,
            'instrument': artistInstrument,
            'page': artistPageNum
        },
        dataType: 'json',
        success: function (data) {
            if (data.template) {
                $("#artist-subheader").html(data.showingResults)
                $("#artists").html(data.template);
                $(".container-list-article").removeClass("artist-loading-gif");
                $("#artists").css("visibility", "visible");
                artistMaxPageNum = data.numPages;

                if (artistPageNum === 1) {
                    $(".left_arrow").addClass('artist-arrow-disabled');
                } else {
                    $(".left_arrow").removeClass('artist-arrow-disabled');
                }

                if (artistPageNum === artistMaxPageNum) {
                    $(".right_arrow").addClass('artist-arrow-disabled');
                } else {
                    $(".right_arrow").removeClass('artist-arrow-disabled');
                }
            }
        },
        error: function (data) {
            $("#artists").show();
            $("#artist-load-gif").css("display", "none");
            $(".container-list-article").css("height", "auto");
            $(".right_arrow").css('visibility', 'hidden');
        }
    });
}

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

function showArtistInfo(artist) {
    $.ajax({
        url: '/search/ajax/artist-info/',
        data: {
            'id': $(artist).data("id")
        },
        dataType: 'json',
        success: function (data) {
            if (data.template) {
                $("#musicianContent").hide();
                $(".artist-search-profile-container").html(data.template);
                $(".artist-search-profile-container")[0].style.display = 'block';
                $("#artist-subheader").html("SHOWING 1 - 1 OF 1 RESULTS");
                $("#back-search").css("display", "flex");
            }
        }
    });
}

function sendEventRequest() {
    if (eventDateFrom) {
        var utcDateFrom = eventDateFrom.getFullYear() + '/' + (eventDateFrom.getMonth() + 1) + '/' + eventDateFrom.getDate();
    }
    if (eventDateTo) {
        var utcDateTo = eventDateTo.getFullYear() + '/' + (eventDateTo.getMonth() + 1) + '/' + eventDateTo.getDate();
    }

    $.ajax({
        url: '/search/ajax/event/',
        data: {
            'main_search': searchTerm,
            'page': eventPageNum,
            'order': eventOrderFilter,
            'date_from': utcDateFrom ? utcDateFrom : null,
            'date_to': utcDateTo ? utcDateTo : null
        },
        dataType: 'json',
        success: function (data) {
            if (data.template) {
                $("#event-subheader").html(data.showingResults);
                $("#event-subheader-footer").html(data.showingResults);

                if (apply || eventFilter) {
                    apply = false;
                    eventFilter = false;
                    $("#events .shows-container").html("");
                }

                $(data.template).find("article").each(function( index ) {
                    $("#events .shows-container").append($( this ));
                });

                eventMaxPageNum = data.numPages;

                $("#event-load-gif").css("display", "none");
                if (data.numPages != eventPageNum) {
                    $("#load-more-btn").show();
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
    apply = false;
    eventFilter = false;

    $("[name='q']").val(searchTerm);
    $('#artist-search').val('');

    $(".left_arrow").click(function () {
        if (artistPageNum !== 1) {

            artistPageNum -= 1;
            $(".container-list-article").addClass("artist-loading-gif");
            $("#artists").css("visibility", "hidden");
            sendArtistRequest();
        }
    });

    $(".right_arrow").click(function () {
        if (artistPageNum !== artistMaxPageNum) {
            artistPageNum += 1;
            $(".container-list-article").addClass("artist-loading-gif");
            $("#artists").css("visibility", "hidden");
            sendArtistRequest();
        }
    });

    $("#next-page-btn").click(function () {
        if (eventPageNum !== eventMaxPageNum) {
            eventPageNum += 1;

            sendEventRequest();
        }
    });

    $('#events-filter').change(function () {
        eventFilter = true;
        eventOrderFilter = $(this).val();
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

    $("#artist-search").keyup(function () {
        delay(function () {
            artistPageNum = 1;
            artistSearchTerm = $('#artist-search').val();
            //$("#artists").hide();
            //$("#artist-load-gif").css("display", "flex");
            $(".container-list-article").addClass("artist-loading-gif");
            $("#artists").css("visibility", "hidden");
            sendArtistRequest();
        }, 700);
    });

    $(".instrument-btn").click(function () {

        if (!$(".instruments-container").is(":visible")) {
            $(".instruments-container").css("display", "flex");
        } else {
            $(".instruments-container").css("display", "none");
        }
    });

    $(".instrument").click(function () {
        artistInstrument = $(this).text();
        $('.instrument-btn').text(artistInstrument);
        artistPageNum = 1;

        $(".container-list-article").addClass("artist-loading-gif");
        $("#artists").css("visibility", "hidden");

        sendArtistRequest();
        $(".instruments-container").css("display", "none");
    });

    ////////////////


    $(".datepicker-btn").click(function () {

        if (!$(".datepicker-container").is(":visible")) {
            $(".datepicker-container").css("display", "flex");
        } else {
            $(".datepicker-container").css("display", "none");
        }

        $("#search-date-picker-from input").click();
        $("#search-date-picker-from input").focus();
    });

    /////////////////////

    var $datePickerFrom = $('#search-date-picker-from input');
    $datePickerFrom.datepicker({
        format: 'mm/dd/yyyy',
        autoclose: true,
        container: '#search-date-picker-from',
        showOnFocus: false
    });

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
        showOnFocus: false
    });

    $datePickerTo.on('changeDate', function (newDate) {
        eventDateTo = newDate.date;
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

    $("#back-search").click(function () {
        $("#back-search").hide();
        $("#musicianContent").show();
        $(".artist-search-profile-container").hide();
        $("#showsContent").show();
    });

    $("#apply-button").click(function () {
        apply = true;
        eventPageNum = 1;
        sendEventRequest();
    });
});
