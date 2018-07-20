var searchTerm, artistSearchTerm, artistInstrument, artistPageNum, artistMaxPageNum, eventPageNum, eventMaxPageNum, eventOrderFilter, eventDate;

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

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
                $("#artists").show();
                $(".loading-image").css("display", "none");
                $(".container-list-article").css("height", "auto");
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
            $(".loading-image").css("display", "none");
            $(".container-list-article").css("height", "auto");
            $(".right_arrow").css('visibility', 'hidden');
        }
    });
}

function changePage(param) {
    eventPageNum = parseInt(param.getAttribute("data-page-number"));
    sendEventRequest();
}

function sendEventRequest() {
    if (eventDate) {
        var utcDate = eventDate.getFullYear() + '/' + (eventDate.getMonth() + 1) + '/' + eventDate.getDate();
    }
    $.ajax({
        url: '/search/ajax/event/',
        data: {
            'main_search': searchTerm,
            'page': eventPageNum,
            'order': eventOrderFilter,
            'date': utcDate ? utcDate : null
        },
        dataType: 'json',
        success: function (data) {
            if (data.template) {
                $("#event-subheader").html(data.showingResults)
                $("#event-subheader-footer").html(data.showingResults)
                $("#events").html(data.template);
                $("#page-numbers-footer").html(data.pageNumbersFooter);

                eventMaxPageNum = data.numPages;
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
    artistSearchTerm = searchTerm;
    artistInstrument = "";
    artistPageNum = eventPageNum = 1;
    artistMaxPageNum = eventMaxPageNum = 2;
    eventOrderFilter = "newest";

    $("[name='q']").val(searchTerm);
    $('#artist-search').val('');

    $(".left_arrow").click(function () {
        if (artistPageNum !== 1) {

            artistPageNum -= 1;
            $("#artists").hide();
            $(".loading-image").css("display", "flex");
            sendArtistRequest();
        }
    });

    $(".right_arrow").click(function () {
        if (artistPageNum !== artistMaxPageNum) {
            artistPageNum += 1;
            $("#artists").hide();
            $(".loading-image").css("display", "flex");
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

    $(".search-artist-box").keyup(function () {
        delay(function () {
            artistPageNum = 1;
            artistSearchTerm = $('.search-artist-box').val();
            $("#artists").hide();
            $(".loading-image").css("display", "flex");
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

        sendArtistRequest();
        $(".instruments-container").css("display", "none");
    });

    var $datePicker = $('#search-date-picker input');
    var now = new Date();
    $datePicker.datepicker({
        format: 'MM // dd // yyyy',
        autoclose: true,
        container: '#search-date-picker'
    });

    $datePicker.on('changeDate', function (newDate) {
        eventDate = newDate.date;
        $('#events-filter').val('oldest');

        $("[value='oldest']").click()
    });

});
