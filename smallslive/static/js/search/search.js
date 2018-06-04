var searchTerm, artistPageNum, artistMaxPageNum, eventPageNum, eventMaxPageNum;

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
            'q': searchTerm,
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

                if(artistPageNum === 1) {
                    $("#left_arrow").css('visibility', 'hidden');
                } else {
                    $("#left_arrow").css('visibility', 'visible');
                }

                if(artistPageNum === artistMaxPageNum) {
                    $("#right_arrow").css('visibility', 'hidden');
                } else {
                    $("#right_arrow").css('visibility', 'visible');
                }
            }
        },
        error: function (data) {
            $("#artists").show();
            $(".loading-image").css("display", "none");
            $(".container-list-article").css("height", "auto");
            $("#right_arrow").css('visibility', 'hidden');
        }
    });
}

function changePage(param) {
  eventPageNum = parseInt(param.getAttribute("data-page-number"));
  sendEventRequest();
}

function sendEventRequest() {
    $.ajax({
        url: '/search/ajax/event/',
        data: {
            'q': searchTerm,
            'page': eventPageNum
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
    artistPageNum = eventPageNum = 1;
    artistMaxPageNum = eventMaxPageNum = 2;

    $("[name='q']").val(searchTerm);
    $("#left_arrow").css('visibility', 'hidden');

    $("#left_arrow").click(function () {
        if (artistPageNum !== 1) {
            
            artistPageNum -= 1;
            $("#artists").hide();
            $(".loading-image").css("display", "block");
            $(".container-list-article").css("height", height);

            sendArtistRequest();
        }
    });

    $("#right_arrow").click(function () {
        if (artistPageNum !== artistMaxPageNum) {
            artistPageNum += 1;
          $("#artists").hide();
            $(".loading-image").css("display", "block");
            $(".container-list-article").css("height", $("#artists").height());
            
            sendArtistRequest();
        }
    });

    $("#next-page-btn").click(function () {
        if (eventPageNum !== eventMaxPageNum) {
            eventPageNum += 1;
            
            sendEventRequest();
        }
    });
});
