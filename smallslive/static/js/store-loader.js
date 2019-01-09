console.log("a")
function loadInfo(infoId){
    $('#artist-container').html("");
    $('#artist-container').addClass("artist-loading-gif");
    $.ajax({
        url: "/store/artist-catalogue/",
        data:{id: infoId},
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


