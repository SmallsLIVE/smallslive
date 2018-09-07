var searchTerm, artistSearchTerm, artistInstrument, artistPageNum, artistMaxPageNum, eventPageNum, eventMaxPageNum, eventOrderFilter, eventDate;

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
                $(data.template).find("article").each(function( index ) {
                    $("#events .event-row").append($( this ));
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

    var $datePicker = $('#search-date-picker input');
    var now = new Date();
    $datePicker.datepicker({
        format: 'MM // dd // yyyy',
        autoclose: true,
        container: '#search-date-picker',
        showOnFocus: false
    });

    $datePicker.on('changeDate', function (newDate) {
        eventDate = newDate.date;
        $('#events-filter').val('oldest');
        $("[value='oldest']").click()
    });

    $datePicker.on('click', function () {
        var dropdown = $('#search-date-picker .dropdown-menu');
        if (dropdown[0] && dropdown[0].style.display === 'block') {
            $datePicker.datepicker('hide');
        } else {
            $datePicker.datepicker('show');
        }

    });
});
