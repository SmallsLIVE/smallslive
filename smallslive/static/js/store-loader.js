function loadInfo(infoUrl){
    $('#artist-container').html("");
    $('#artist-container').addClass("artist-loading-gif");
    $.ajax({
        url: infoUrl,
        success: function (data) {
            var $target;
            $('#artist-container').removeClass("artist-loading-gif");
            $target = $('#artist-container');
            $target.html(data);
            $target.data('url', infoUrl);
        }
    });
}
$(document).on('click', ".artist-category", function(){
        let url = $(this).data("url");
        if(url){
            $("#store-home").hide()
            $("#artist-store").show()
            loadInfo(url)
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
    var isElementInView = Utils.isElementInView($('#storeTitle'), false);

    if (isElementInView) {
        $('.store-nav').css('position', 'absolute')
        $('.store-nav').css('top', 'auto')
    } else {
        $('.store-nav').css('position', 'fixed')
        $('.store-nav').css('top', '0px')
    }
    
})
