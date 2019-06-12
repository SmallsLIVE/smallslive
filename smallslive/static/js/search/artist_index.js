
$(document).ready(function() {

  var $filter = $('#most-popular-filter');

  var setMostPopular = function (value) {
  var mostPopularFilter = $('#most-popular-container').find('.event-row');
    $.get(popularQueryUrl + "?range=" + value,
      function (data) {
        mostPopularFilter.replaceWith(data.content);
      });
  };
  $filter.on('change', function () {
    setMostPopular($filter.val());
  });

  if (typeof popularFilterDefaultValue != 'undefined') {
    $filter.val(popularFilterDefaultValue);
    $filter.trigger("change");
  }

  $('.scroll-left').css('visibility', 'initial')
  const alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
  "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
  buttons = {}
  alphabet.map((letter) => {
  buttons[letter] = document.createElement('div');
  $(buttons[letter]).addClass('white-border-button')
      .html(letter)
      .appendTo($("#a-z-search")).click(() => {
        $('#a-z-search .white-border-button').css('background-color', '#f0f0eb')
        $(buttons[letter]).css('background-color', '#fff')
        if(searchTerm.trim() != ""){
          searchTerm = "";
          sendArtistRequest(()=>{
          $('#artist-search').val($(buttons[letter]).text())
          $("#artist-search").change()
          });
        }else{
          $('#artist-search').val($(buttons[letter]).text())
          $("#artist-search").change()
        }

      })
  });
  $('.scroll-right').click(() => {
    let scrollF = setInterval(function() {$( "#a-z-search" ).scrollLeft($( "#a-z-search" ).scrollLeft() + 30)}, 10)
    setTimeout(() => {clearInterval(scrollF)}, 120)
    let scrollS = setInterval(function() {$( "#a-z-search" ).scrollLeft($( "#a-z-search" ).scrollLeft() + 10)}, 80)
    setTimeout(() => {clearInterval(scrollS)}, 320)
    setTimeout(function(){
      if($( "#a-z-search" ).scrollLeft() == 0){
        $('.scroll-right').css('visibility', 'initial')
        $('.scroll-left').css('visibility', 'hidden')

      }else if( $( "#a-z-search" ).scrollLeft() == 819 ){
        $('.scroll-right').css('visibility', 'hidden')
        $('.scroll-left').css('visibility', 'initial')
      }else{
        $('.scroll-left').css('visibility', 'initial')
        $('.scroll-right').css('visibility', 'initial')
      }
    }, 310)

  });
  $('.scroll-left').click(() => {
    let scrollF = setInterval(function() {$( "#a-z-search" ).scrollLeft($( "#a-z-search" ).scrollLeft() - 30)}, 10)
    setTimeout(() => {clearInterval(scrollF)}, 120)
    let scrollS = setInterval(function() {$( "#a-z-search" ).scrollLeft($( "#a-z-search" ).scrollLeft() - 10)}, 10)
    setTimeout(() => {clearInterval(scrollS)}, 300)
    setTimeout(() => {
      if($( "#a-z-search" ).scrollLeft() == 0){
        $('.scroll-right').css('visibility', 'initial')
        $('.scroll-left').css('visibility', 'hidden')

      }else if( $( "#a-z-search" ).scrollLeft() == 819 ){
        $('.scroll-right').css('visibility', 'hidden')
        $('.scroll-left').css('visibility', 'initial')
      }else{
        $('.scroll-left').css('visibility', 'initial')
        $('.scroll-right').css('visibility', 'initial')
      }
    }, 310)

  });


  foundArtistNumber = $(".artist-mobile").length
  if ( foundArtistNumber === 1 ){
    $uniqueArtist = $(".artist-mobile")[0];
    $($uniqueArtist).find(".artist-row")[0].click()
  }

  $('.instruments-container .close-button').on('click', function() {
      $(this).closest('.instruments-container').hide();
  });

  $(".musicians-result").on("click", function () {
      $(".musicians-result.active").removeClass("active");
      $(this).addClass("active");

      $(".search-container.pad-content > section").hide();
      var $section = $("#" + $(this).data("type"));
      $section.show();
      $section.find(".slide-btn.next").css("visibility", "visible");

  });
});