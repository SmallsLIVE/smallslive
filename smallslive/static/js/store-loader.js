// function loadInfo(infoId){
//     $('#artist-store').html("");
//     $('#artist-store').addClass("artist-loading-gif");
//     $.ajax({
//         url: "/store/artist-catalogue/",
//         data:{id: infoId},
//         success: function (data) {
//             var $target;
//             $('#artist-store').removeClass("artist-loading-gif");
//             $target = $('#artist-store');
//             $target.html(data.template);
//         }
//     });
// }
$(document).on('click', ".artist-category", function () {
    let id = $(this).data("id");
    if (id) {
        $("#store-home").hide()
        $("#artist-store").show()
        loadInfo(id)
    } else {
        $("#artist-store").hide()
        $("#store-home").show()
    }
})


function isScrolledIntoView(elem) {
    var docViewTop = $(window).scrollTop();
    var docViewBottom = docViewTop + $(window).height();

    var elemTop = $(elem).offset().top;
    var elemBottom = elemTop + $(elem).height();

    return ((elemBottom <= docViewBottom) && (elemTop >= docViewTop));
}


function Utils() {

}

Utils.prototype = {
    constructor: Utils,
    isElementInView: function (element, fullyInView) {
        var pageTop = $(window).scrollTop();
        var pageBottom = pageTop + $(window).height();
        var elementTop = $(element).offset().top;
        var elementBottom = elementTop + $(element).height();

        if (fullyInView === true) {
            return ((pageTop < elementTop) && (pageBottom > elementBottom));
        } else {
            return ((elementTop <= pageBottom) && (elementBottom >= pageTop));
        }
    }
};

var Utils = new Utils();
$(document).scroll(function () {
    if ($('#storeTitle').length) {
        var isElementInView = Utils.isElementInView($('#storeTitle'), false);
        if (isElementInView) {
            $('.store-nav').css('position', 'absolute')
            $('.store-nav').css('top', 'auto')
        } else {
            $('.store-nav').css('position', 'fixed')
            $('.store-nav').css('top', '0px')
        }
    }
})

$(document).on('click', ".load-more-btn", function () {
    var loadBtn = $(this);
    var artistId = loadBtn.data("artist");
    var pageNumber = loadBtn.data("page");
    var url = loadBtn.data('url');
    $.ajax({
        url: url,
        data: {
            artist: artistId,
            page: pageNumber
        },
        success: function (data) {
            if (data.last_page) {
                loadBtn.hide()
            } else {
                loadBtn.data("page", pageNumber + 1)
            }
            var $target;
            if (artistId) {
                //$target = $('#artist-albums');
                $target = $('#all-recordings-container');
            } else {
                $target = $('#all-recordings-container');
            }
            $target.append(data.template);
        }
    });
})

$.expr[":"].contains = $.expr.createPseudo(function (arg) {
    return function (elem) {
        return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
    };
});

$(document).on('keyup', ".artist-search", function () {
    if ($(this)[0].value == "") {
        $(".artist-category").show()
    } else {
        $(".artist-category").hide()
        $(".artist-featured").show()
        $(".artist-category:contains('" + $(this)[0].value + "')").show();
    }
})
$(document).on('keyup', "#artist-search-all", function () {
    artistList = $("#artist-list")
    if ($(this)[0].value == "") {
        artistList.hide()
    } else {
        $(".artist-result").hide()
        artistResults = $(".artist-result:contains('" + $(this)[0].value + "')")
        noResults = $("#no-results")
        if (artistResults.length > 0) {
            artistList.show()
            noResults.hide()
            artistResults.show();
        } else {
            artistList.show()
            noResults.show()
        }

    }
})

$(document).on('click', ".artist-result", function () {
    let artistId = $(this).data("id");
    $("#artist-search-all").val($(this).text())
    loadInfo(artistId)
})

function loadInfo(artistId) {
    var loadBtn = $("#store-load-btn")
    loadBtn.data("page", 2)
    loadBtn.data("artist", artistId)
    var url = loadBtn.data('url');
    $('#artist-store').html("");
    $('#artist-store').addClass("artist-loading-gif");
    $.ajax({
        url: url,
        data: {
            artist: artistId,
            page: 1
        },
        success: function (data) {
            if (data.last_page) {
                loadBtn.hide()
            }
            $("#artist-list").hide()
            var $target;
            $('#artist-store').removeClass("artist-loading-gif");
            $target = $('#all-recordings-container');
            $target.html(data.template);
        }
    });
}

$("#artist-search-all").focusout(function () {
    setTimeout(function () {
        $("#artist-list").css("display", "none");
    }, 300);
});

$(document).on('click', ".reset-search", function () {
    let loadBtn = $("#store-load-btn")
    loadBtn.data("artist", "")
    loadBtn.show()
    $("#artist-search-all").val("")
    loadInfo()
})


$(document).ready(function () {
    artistId = getUrlParameter("artist_pk");
    artistId = artistId ? artistId : "";
    if (artistId) {
        loadInfo(artistId)

        $("#artist-search-all").val($(".search-bar-result-text[data-id=" + artistId + "]").text())
    }
})