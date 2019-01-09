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


