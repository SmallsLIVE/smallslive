function loadInfo(infoId){
    $('#artist-store').html("");
    $('#artist-store').addClass("artist-loading-gif");
    $.ajax({
        url: "/store/artist-catalogue/",
        data:{id: infoId},
        success: function (data) {
            var $target;
            $('#artist-store').removeClass("artist-loading-gif");
            $target = $('#artist-store');
            $target.html(data.template);
        }
    });
}
$(document).on('click', ".artist-category", function(){
        let id = $(this).data("id");
        if(id){
            $("#store-home").hide()
            $("#artist-store").show()
            loadInfo(id)
        }else{
            $("#artist-store").hide()
            $("#store-home").show()
        }
})


function isScrolledIntoView(elem)
{
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
$(document).scroll(function(){
    if($('#storeTitle')){
        var isElementInView = Utils.isElementInView($('#storeTitle'), false);
        if (isElementInView) {
            $('.store-nav').css('position', 'absolute')
            $('.store-nav').css('top', 'auto')
        } else {
            $('.store-nav').css('position', 'fixed')
            $('.store-nav').css('top', '0px')
        }
}
if($('.store-header__title__divider')){
    var isElementInView = Utils.isElementInView($('.store-header__title__divider'), false);
    if (isElementInView) {
        $('.store-nav').css('position', 'absolute')
        $('.store-nav').css('top', 'auto')
    } else {
        $('.store-nav').css('position', 'fixed')
        $('.store-nav').css('top', '0px')
    }
}
})

$(document).on('click', ".load-more-btn", function(){
    let loadBtn = $(this)
    let artistId = loadBtn.data("artist")
    let pageNumber = loadBtn.data("page")
    $.ajax({
        url: "/store/album-list/",
        data:{artist: artistId, page: pageNumber},
        success: function (data) {
            if(data.last_page){
                loadBtn.hide()
            }else{
                loadBtn.data("page", pageNumber + 1)
            }
            var $target;
            if(artistId){
                $target = $('#artist-albums');
            }else{
                $target = $('#all-recordings-container');
            }
            $target.append(data.template);
        }
    });
})

$.expr[":"].contains = $.expr.createPseudo(function(arg) {
    return function( elem ) {
        return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
    };
});

$(document).on('keyup', ".artist-search", function(){
    if($(this)[0].value == ""){
        $( ".artist-category").show()
    }else{
        $(".artist-category").hide()
        $(".artist-featured").show()
        $( ".artist-category:contains('" + $(this)[0].value + "')" ).show();
    }
})