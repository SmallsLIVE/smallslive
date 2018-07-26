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

    $("#desktop-search-bar, #search-bar").keyup(function () {
        delay(function () {
            searchBarTerm = $('#desktop-search-bar:visible, #search-bar input:visible').val();
            if (searchBarTerm.length > 1) {
                sendSearchBarRequest();
            }
            else {
                $(".search-bar-autocomplete-container").css("display", "none");
            }
        }, 400);
    });

    $("#desktop-search-bar").focusout(function () {
        setTimeout(function(){ $(".search-bar-autocomplete-container").css("display", "none"); }, 300);
    });
});

$(document).on('click','.search-bar-more', function(){
    $(".search-input").submit();
});
