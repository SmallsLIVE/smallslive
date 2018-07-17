searchBarTerm = "";

function sendSearchBarRequest() {
    $.ajax({
        url: '/search/ajax/search-bar/',
        data: {
            'main_search': searchBarTerm
        },
        dataType: 'json',
        success: function (data) {
            if (data.template) {
                $(".search-bar-autocomplete-container").html(data.template)

                if (!$(".search-bar-autocomplete-container").is(":visible")) {
                    $(".search-bar-autocomplete-container").css("display", "block");
                }
            }
        }
    });
}

$(document).ready(function () {
    var delay = (function () {
        var timer = 0;
        return function (callback, ms) {
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
        };
    })();

    $("#search-bar").keyup(function () {
        delay(function () {
            searchBarTerm = $('#search-bar').val();
            if (searchBarTerm.length > 1) {
                sendSearchBarRequest();
            }
            else {
                $(".search-bar-autocomplete-container").css("display", "none");
            }
        }, 400);
    });

    $("#search-bar").focusout(function () {
        $(".search-bar-autocomplete-container").css("display", "none");
    });
});

$(document).on('click','.search-bar-more', function(){
    $(".search-input").submit();
});
