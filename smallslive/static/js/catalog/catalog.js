
$(document).ready(function () {
  Stripe.setPublishableKey(stripePublicKey);
  $(window).resize();

  $(document).on('click', '.download', function (event) {
    event.stopPropagation();
    var mp3Url = $(this).data('mp3-href');
    var mp3Name = $(this).data('mp3-name');
    var hdUrl = $(this).data('hd-href');
    var hdName = $(this).data('hd-name');
    $('#downloadFormatMp3Url').attr('href', mp3Url);
    $('#downloadFormatMp3Url').attr('download', mp3Name);
    $('#downloadFormatHdUrl').attr('href', hdUrl);
    $('#downloadFormatHdUrl').attr('download', hdName);
    $('#downloadFormat').modal('show');
  });

  /* Product selection and purchase */


  function showFlow(flowType) {

    $mainContainer = $("#my-downloads-product__" + flowType);
    setSelected('catalog', null, 0);
    showPanel("SelectType");
    $donationConfirmationDialog.modal("hide");
    $(".album.big-player").addClass("hidden");
    $("#my-downloads-product__" + flowType).removeClass('hidden');
    $(".store-banner").addClass("hidden");
    $(".white-line-bottom").addClass("hidden");
    $(".newest-recordings-container.downloads").addClass("hidden");

  }

  $('#selectionConfirmationDialog').on('hidden.bs.modal', function () {
    //$("#my-downloads-product__purchase").addClass("hidden");
  });

  var $donationConfirmationDialog = $("#supportConfirmationDialog");

  $(document).on('click', '#projectDonationBtn, #projectDonationBtnMobile', function (event) {

    $donationConfirmationDialog.modal("show");

    var contents = $("#donation-confirmation-body").html();
    $donationConfirmationDialog.find('.modal-body').html(contents);

  });

  $(document).on('click', '#supportLogIn', function (event) {

    /* Before logging in, make sure the next url is set correctly
    on the form's action so that the confirmation email con lead the user
     to continue donating */
    $("#supportConfirmationDialog").modal("hide");

    var $modal = $("#logIn");
    var next = $(this).attr("data-redirect-url");
    var action = $modal.find("form").attr("action");
    var parts = action.split("next=");

    parts[1] = next;
    action = parts.join("next=");

    $modal.modal("show");
    $modal.find("form").attr("action", action);

  });


  $(document).on("click", "#confirmDonationButton", function () {
    // Initiate the flow if PO chooses  a pop up to start  the  flow
    window.location = $(this).data("support-url");
  });

  var $downloadConfirmationDialog = $("#downloadConfirmationDialog");

  $(document).on("click", "#tracksDownloadBtn, #tracksDownloadBtnMobile", function (event) {

    var $table = $("#track-list-tbl");
    var $clonedTable = $table.clone(true).removeClass("hidden");
    var $tableContainer = $downloadConfirmationDialog.find(".table-container");
    if ($tableContainer.find("#track-list-tbl").length === 0) {
      $tableContainer.append($clonedTable);
    }
    $downloadConfirmationDialog.modal("show");

  });

  $(document).on("click", "#downloadConfirmationDialog .cancel", function () {
    $downloadConfirmationDialog.modal("hide");
  });


});

function downloadAll(urls) {
  var link = document.createElement('a');

  link.setAttribute('download', null);
  link.style.display = 'none';

  document.body.appendChild(link);

  for (var i = 0; i < urls.length; i++) {
    link.setAttribute('href', urls[i]);
    link.click();
  }

  document.body.removeChild(link);
}

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
      $element = $($(".my-downloads-album__tracks-table__row.flex-row:not(.disabled):not(.no-play)")[0]);
    } else {
      $element = $trackInfo.closest(".my-downloads-album__tracks-table__row.flex-row:not(.disabled):not(.no-play)");
    }
  }

  if ($element.hasClass("play-on-library")) {
    // Let's redirect to the library
    var url = $element.data("url");
    window.location.href = url;
    return;

  }

  if ($element.hasClass("no-play")) {
    return;
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
