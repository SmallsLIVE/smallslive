
$(document).ready(function () {
  Stripe.setPublishableKey('{{ STRIPE_PUBLIC_KEY }}');
  $(window).resize();
});

var $lastPlayer,
  $audioPlayer,
  audioPlayerTrack,
  $trackInfo,
  $mainContainer,
  $playerContainer,
  $lastPlayerContainer,
  $lastPlayerContainerButton,
  play;

function playTrack($element) {

  if (!$element) {
    if (!$trackInfo) {
      $element = $($(".my-downloads-album__tracks-table__row.flex-row:not(.disabled)")[0]);
    } else {
      $element = $trackInfo.closest(".my-downloads-album__tracks-table__row.flex-row:not(.disabled)");
    }
  }

  var progress = calculateProgress($element, event);
  //find audio player and track number and set the big player track number
  $audioPlayer = $element.find(".audio audio");
  audioPlayerTrack = $audioPlayer.data("track");

  $mainContainer = $element.closest(".big-player");
  $playerContainer = $mainContainer.find(".album__header__cover");
  $playerContainer.data("track", audioPlayerTrack);

  //make active track color red, toggles player button and remove previous track color
  $trackInfo = $element.find(".track-info");

  if ($lastPlayerContainer && $lastPlayerContainer.length)  {
    $lastPlayerContainerButton = $lastPlayerContainer.find(".purchases-player-button");
  } else {
    $lastPlayerContainerButton = $playerContainer.find(".purchases-player-button");
  }

  $playerContainerButton = $playerContainer.find(".purchases-player-button");

  var audioProgress = $audioPlayer.currentTime / $audioPlayer.duration * 100;

  if ($trackInfo.hasClass("active-track")) {
    $(".active-track").removeClass("active-track");
    play = false;
    $playerContainerButton.removeClass("mypause-btn");
    $playerContainerButton.addClass("myplay-btn");
    $playerContainerButton.find('div').html('<i class="fas fa-play"></i>');
  } else {
    $audioPlayer.closest(".my-downloads-album__tracks-table__row").find(".progress-bar").addClass("active-bar");
    $(".active-track").removeClass("active-track");
    $element.find(".track-info").addClass("active-track");
    play = true;
    if ($lastPlayerContainerButton) {
      $lastPlayerContainerButton.addClass("myplay-btn");
      $lastPlayerContainerButton.removeClass("mypause-btn");
    }
    $playerContainerButton.addClass("mypause-btn");
    $playerContainerButton.removeClass("myplay-btn");
    $playerContainerButton.find('div').html('<i class="fas fa-pause"></i>');
  }

  //toggles player
  if ($lastPlayer) {
      $lastPlayer[0].pause();
      $("#" + $lastPlayer.data("track"))
      .children(".progress-bar")
      .addClass("paused");
  }
  togglePlayer(play);

  $lastPlayerContainer = $playerContainer;
  $lastPlayer = $audioPlayer;

}

$(document).on('click', ".my-downloads-album__tracks-table__row.flex-row:not(.disabled)", function  (event) {
  playTrack($(this));
});

function togglePlayer(play){
  if (!$audioPlayer) {
      $audioPlayer = $bigContainer.find(".audio audio[data-track='0']");
      $(trackInfo).first().addClass("active-track");
  }
  if (play) {
    $audioPlayer[0].play();
    $("#" + $playerContainer.data("track"))
      .children(".progress-bar")
      .removeClass("paused");
  } else {
    $audioPlayer[0].pause();
    $("#" + $playerContainer.data("track"))
    .children(".progress-bar")
    .addClass("paused");
    $(".active-track").removeClass("active-track");
  }
}

$(document).on('click', ".purchases-player-button", function () {
  playTrack();
})
var audioPlayers = document.getElementsByClassName("audio-player");

function readableTime(seconds) {
    var hr = ~~(seconds / 3600);
    var min = ~~((seconds % 3600) / 60);
    var sec = seconds % 60;
    var sec_min = "";
    if (hr > 0) {
        sec_min += "" + hr + ":" + (min < 10 ? "0" : "");
    }
    sec_min += "" + min + ":" + (sec < 10 ? "0" : "");
    sec_min += "" + sec;
    return sec_min;
}

function calculateProgress(element, position) {

  var mX, mY, distance,
    $element  = $(element);

  function calculateDistance(elem, mouseX, mouseY) {
    return Math.floor(mouseX - (elem.offset().left), 2);
  }
  mX = position.pageX;
  mY = position.pageY;
  distance = Math.floor(calculateDistance($element, mX, mY) / element.width() * 100);
  return distance
};
function changeProgress(progress, player) {
  newProgress = Math.floor(player.duration) * progress / 100
  player.currentTime = newProgress;
  updateProgressTrack('player', newProgress)
}

$(".event-display").on("click", function () {
  albumId = $(this).data("parent-pk")
  album_type = $(this).data("type")
  bought_tracks = $(this).data("bought")
  loadAlbum(albumId, bought_tracks, album_type)
})

var mouseEventHandler = function (ev) {
  if (ev.type == "mousemove"){
      var position = ev
  } else {
      var position = {};
      position.pageX = ev.changedTouches[0].pageX;
      position.pagey = ev.changedTouches[0].pageY;
  }

  dragabbleProgess = calculateProgress($(this), position) + "%";
  $(this).find(".my-downloads-album__tracks-table__row").find(".progress-bar").css("width", dragabbleProgess);
}
startProgressHold =  function(event) {
  maincontainer = $(this).closest(".track-container")[0];
  active = $(maincontainer).find(".track-info.active-track");
  if( active.length > 0) {
      if (event.type == "mousedown") {
          el.addEventListener("mousemove", mouseEventHandler);
      } else {
          el.addEventListener("touchmove", mouseEventHandler);
      }

      clearInterval(setTime);
  }
}
$(document).on( "touchstart",  ".length-bar", startProgressHold);
$(document).on( "mousedown",  ".length-bar", startProgressHold);

endProgressHold =  function(ev){
    if(ev.type == "mouseup"){
        var position = ev
    }else{
        var position = {};
        position.pageX = ev.originalEvent.changedTouches[0].pageX
        position.pagey = ev.originalEvent.changedTouches[0].pageY
    }
    maincontainer = $(this).closest(".track-container")[0]
    active = $(maincontainer).find(".track-info.active-track")
    if(active.length > 0){
         if(event.type == "mouseup"){
            el.removeEventListener("mousemove", mouseEventHandler)
        }else{
            el.removeEventListener("touchmove", mouseEventHandler)
        }
        player = maincontainer.getElementsByClassName("audio-player")[0];
        changeProgress(calculateProgress($(maincontainer), position), player)
        setTime = setInterval( t=> {
            currentTime = Math.floor(player.currentTime)
            $(player).closest(".my-downloads-album__tracks-table__row").find(".progress-bar").addClass("active-bar")
            timeTracker = $(player).closest(".my-downloads-album__tracks-table__row").find(".my-downloads-album__tracks-table__column.duration")[0]
            progress = player.currentTime / player.duration * 100
            progressWidth = progress + "%"
            $(player).closest(".my-downloads-album__tracks-table__row").find(".progress-bar").css("width", progressWidth )
            $(timeTracker).html(readableTime(currentTime))
        },100)
    }
}

$(document).on( "touchend",  ".length-bar", endProgressHold);
$(document).on( "mouseup",  ".length-bar", endProgressHold);
Array.prototype.forEach.call(audioPlayers, function(player) {
    player.addEventListener("play", function(){
            setTime = setInterval( t=> {
            currentTime = Math.floor(player.currentTime)
            $(player).closest(".my-downloads-album__tracks-table__row").find(".progress-bar").addClass("active-bar")
            timeTracker = $(player).closest(".my-downloads-album__tracks-table__row").find(".my-downloads-album__tracks-table__column.duration")[0]
            progress = player.currentTime / player.duration * 100
            progressWidth = progress + "%"
            updateProgressTrack( $(player).data('track'), progress)
            $(player).closest(".my-downloads-album__tracks-table__row").find(".progress-bar").css("width", progressWidth )
            $(timeTracker).html(readableTime(currentTime))
        },100)

    });
    player.addEventListener("pause", function(){
        clearInterval(setTime)
        $(player).closest(".my-downloads-album__tracks-table__row").find(".progress-bar").removeClass("active-bar")
    });
    player.addEventListener("ended", function(){
        $(player).closest(".my-downloads-album__tracks-table__row").find(".progress-bar").removeClass("active-bar");
        $(player).closest(".big-player").find(".purchases-player-button").removeClass("mypause-btn");
        $(player).closest(".big-player").find(".purchases-player-button").addClass("myplay-btn");
        $(playerContainerButton).find('div').html('<i class="fas fa-play"></i>')
        $(".active-track").removeClass("active-track");
        player.currentTime = 0;
        clearInterval(setTime)
    });
});
