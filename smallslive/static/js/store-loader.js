console.log("a")
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


