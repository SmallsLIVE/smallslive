var search_term, artist_page_num, event_page_num;

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
        url: '/search/get-artists/',
        data: {
            'q': search_term,
            'artist-page': artist_page_num
        },
        dataType: 'json',
        success: function (data) {
            if (data.artists) {
                $("#artists").html(data.artists);
                $("#artists").show();
                $(".loading-image").css("display", "none");
                $(".container-list-article").css("height", "auto");
            }
        }
    });
}

$(document).ready(function () {
    search_term = getUrlParameter("q");
    artist_page_num = event_page_num = 1;

    $("#left_arrow").click(function () {
        if (artist_page_num != 1) {
            artist_page_num -= 1;
            $("#artists").hide();
            $(".loading-image").css("display", "block");
            $(".container-list-article").css("height", height);

            sendArtistRequest();
        }
    });

    $("#right_arrow").click(function () {
        artist_page_num += 1;
        height = $("#artists").height();
        $("#artists").hide();
        $(".loading-image").css("display", "block");
        $(".container-list-article").css("height", height);
        
        sendArtistRequest();
    });
});