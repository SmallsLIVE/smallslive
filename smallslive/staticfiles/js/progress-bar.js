
function updateProgress(progress, e) {
  if (progress < 100) {
    //console.log('Progress: ' + progress.toString());
    if (e.target.className == "progress-bar") {
      $(e.target).css("width", progress + "%");
      $(e.target).data("percentage", progress);
      $(e.target)
        .parent(".progress-holder")
        .data("progress", progress);
      $(e.target)
        .parent(".progress-holder")
        .trigger("progressUpdate");
    } else {
      $(e.target)
        .children(".progress-bar")
        .css("width", progress + "%");
      $(e.target).data("progress", progress);
      $(e.target).trigger("progressUpdate");
    }
    if (e.target.className == "progress-btn") {
      $(e.target)
        .parent(".progress-bar")
        .css("width", progress + "%");

      $(e.target)
        .parent(".progress-bar")
        .parent(".progress-holder")
        .data("progress", progress);
      $(e.target)
        .parent(".progress-bar")
        .parent(".progress-holder")
        .trigger("progressUpdate");
    }
  }
  audioPlayer.currentTime = (audioPlayer.duration / 100) * progress;
}
function getPercentage(e) {
  var x;
  if (e.type == "touchmove") {
    x = e.originalEvent.touches[0].clientX;
  } else {
    x = e.clientX;
  }
  //$(document).width()
  var rect = document
    .getElementsByClassName("progress-bar")[0]
    .getBoundingClientRect();

  let percentage = ((x - rect.left) / $(".progress-holder").width()) * 100;
  $(".progress-holder").trigger("testeo");

  //console.log('Percentage: ' + percentage.toString());

  return Math.floor(percentage);
}

function keepMoving(event) {
  $(document).on("touchmove", document, e => {
    e.preventDefault();
    updateProgress(getPercentage(e), event);
  });
  $(document).on("mousemove", document, e => {
    updateProgress(getPercentage(e), event);
  });
}

function stopMoving() {
  $(document).unbind("mousemove");
  $(document).unbind("touchmove");
}

$(document).on("mousedown", ".progress-btn", e => {
  keepMoving(e);
});
$(document).on("touchstart", ".progress-btn", e => {
  keepMoving(e);
});

$(document).mouseup(e => {
  stopMoving();
});

$(document).on("touchend", e => {
  stopMoving();
});
$(document).on("mousedown", ".progress-bar", e => {
  keepMoving(e);
});
$(document).on("touchstart", ".progress-bar", e => {
  keepMoving(e);
});

$(document).on("mousedown", ".progress-btn", e => {
  keepMoving(e);
});

$(document).on("touchstart", ".progress-btn", e => {
  keepMoving(e);
});

$(document).on("mousedown", ".progress-holder", e => {
  keepMoving(e);
});
$(document).on("touchstart", ".progress-holder", e => {
  keepMoving(e);
});

$(document).on("mouseup", ".progress-bar", e => {
  stopMoving();
});
$(document).on("touchend", ".progress-bar", e => {
  stopMoving();
});

$(document).on("mouseup", ".progress-holder", e => {
  stopMoving();
});
$(document).on("touchend", ".progress-holder", e => {
  stopMoving();
});

$(document).on("mousedown", ".progress-holder", function(e) {
  $(e.target)
    .children(".progress-bar")
    .css("width", $(e.target).data("percentage"));
});

$(document).on("touchend", ".progress-holder", function(e) {
  $(e.target)
    .children(".progress-bar")
    .css("width", $(e.target).data("percentage"));
});

function updateProgressTrack(id, progress) {
  //console.log('updateProgressTrack: ' + progress.toString());
  $("#" + id)
    .children(".progress-bar")
    .css("width", progress + "%");
}
