
$(document).ready(function () {

  var $datePickerFrom = $("#search-date-picker-from-dashboard input");
  var $datePickerTo = $("#search-date-picker-to-dashboard input");
  var fromDateLimit
  var firstEventDate;
  var toDateLimit
  var lastEventDate;

  initializeFilters();
  initializeDashboardDatePickers();
  bindEvents();
  loadMore(true);

  function initializeFilters() {

    $('#artist_archive_status_filter').on('change', function () {
      currentPage = 0;
      totalPages = 1;
      loadMore(true);
      $('#artistEventsList').html("");
    });

    $('#artist_archive_order_filter').on('change', function () {
      currentPage = 0;
      totalPages = 1;
      loadMore(true);
      $('#artistEventsList').html("");
    });

    $('#load-more-btn').on('click', function () {
      loadMore();
    });
  }

  function initializeDashboardDatePickers() {

    $datePickerFrom.datepicker({
      format: 'mm/dd/yyyy',
      autoclose: false,
      container: '#search-date-picker-from-dashboard',
      showOnFocus: false
    });

    $datePickerFrom.on('changeDate', function (newDate) {
      $("#search-date-picker-to-dashboard input").click();
      $("#search-date-picker-to-dashboard input").focus();
      //$datePickerTo.datepicker("setStartDate", newDate.date);
    });

    $datePickerFrom.on('click', function () {
      var dropdown = $('#search-date-picker .dropdown-menu');
      if (!(dropdown[0] && dropdown[0].style.display === 'block')) {
        $datePickerFrom.datepicker('show');
        $datePickerTo.datepicker('hide');
      }
    });

    //////////////////////
    $datePickerTo.datepicker({
      format: 'mm/dd/yyyy',
      autoclose: false,
      container: '#search-date-picker-to-dashboard',
      showOnFocus: false
    });

    $datePickerTo.on("changeDate", function(newDate) {

      //$datePickerFrom.datepicker("setEndDate", newDate.date);

    });

    $datePickerTo.on('click', function () {
      var dropdown = $('#dashboard-desktop-datepicker #search-date-picker .dropdown-menu');
      if (!(dropdown[0] && dropdown[0].style.display === 'block')) {
        $datePickerTo.datepicker('show');
        $datePickerFrom.datepicker('hide');
      }
    });

    $('.datepicker-dashboard-main-btn').bind("click", ToggleDisplay);

    function ToggleDisplay(event) {
      if ($("#dashboard-desktop-datepicker").data('shown'))
        hide(event);
      else
        display();
    }

    function display() {
      $("#dashboard-desktop-datepicker").css("display", "flex")
      $("#dashboard-desktop-datepicker").data('shown', true);
      $("#search-date-picker-from-dashboard input").click();
      $("#search-date-picker-from-dashboard input").focus();
    }

    function hide(event) {
      var $target = $(event.target);
      if (($target.closest('.noclick').length == 0) &&
          (!($target.hasClass('day') || $target.hasClass('year')))) {
        $('#dashboard-desktop-datepicker').data('shown', false);
      }
    }

    $("#dashboard-apply-button").click(function () {
      $("#dashboard-desktop-datepicker").hide().data('shown', false);
      currentPage = 0;
      totalPages = 1;
      $('#artistEventsList').html("")
      $('#artistEventsList').addClass("artist-loading-gif");
      loadMore();
    });

    $("#dashboard-reset").click(function () {
      $("#dashboard-desktop-datepicker").hide().data("shown", false);
      $("#search-date-picker-from-dashboard input").val("").datepicker("update");
      $("#search-date-picker-to-dashboard input").val("").datepicker("update");
      currentPage = 0;
      totalPages = 1;
      $('#artistEventsList').html("");
      $('#artistEventsList').addClass("artist-loading-gif");
      loadMore();
    });


    $("#refine-btn").click(function () {
      $(".refine-overlay").show();
    });

    $(document).on("click", "#dashboard-desktop-datepicker-close", function () {
      $("#dashboard-desktop-datepicker").hide().data("shown", false);
    });

  }

  function bindEvents() {

    $(document).on('click', '.artist-event-row', function () {

      var $container = $(this).closest(".artist-events-list");
      $container.removeClass("active");

      $(".artist-event").addClass("active");

      $(".artist-event-row").removeClass("active");
      $(this).addClass("active");

      var url = $(this).data('ajax-edit-url');
      showEventForm(url);
      url = $(this).data('ajax-info-url');
      showEventInfo(url);

    });

    $(document).on('click', '#form-edit-button', function () {
      var $submit = $("#submit-id-submit");
      if ($submit.attr("disabled") === "disabled") {
        $("#submit-id-submit").removeAttr('disabled');
        enableEditForm();
        $(this).text('Cancel')
      } else {
        $("#submit-id-submit").attr("disabled", "disabled");
        disableEditForm();
        cancelUploadedImage();
        $(this).text('Edit');
      }
    });

    // Ajax upload image
    $(document).on("change", "#id_photo", function () {
      var filePath = $(this).val();
      var fileName = filePath.replace(/^.*[\\\/]/, '');
      if (fileName.length > 20) {
        fileName = fileName.substr(0, 20) + ' ... ';
      }

      var $fileNameSpan = $("#file_name");
      $fileNameSpan.text(fileName);
      $fileNameSpan.attr("original-text", "Choose File");

      var $that = $(this);

      var $form = $(this).closest('form');
      var data = new FormData($form.get(0));
      $('#div_id_photo img').toggleClass('hidden');
      $('#image-load-gif').toggleClass('hidden');
      $('#event_edit_modal').find('.modal-body').html('');
      $('#div_id_cropping .controls').hide();
      $('#image-upload-loading').removeClass("hidden");

      $.ajax({
          url: uploadImagePreviewUrl,
          type: "POST",
          data: data,
          enctype: 'multipart/form-data',
          processData: false,
          contentType: false,
          cache: false,
          success: function (data) {
            if (data.success) {
              $('#image-load-gif').toggleClass('hidden');
              $("#image-upload-loading").toggleClass("hidden");
              updateUploadedImage(data);
            }
          }
      });

    })

    $(document).on("click", "#submit-id-submit", function () {
      $("#event-edit-form").submit();
    });

    $(document).on("submit", "#event-edit-form", function (event) {
      $('#edit-event-dashboard').html($('#event-edit-form-load-gif').clone().removeClass('hidden'));
      var $form = $(this);
      var url = $form.attr("action");
      var infoUrl = $form.data("ajax-info-url");
      event.preventDefault();
      $.ajax({
        type: "POST",
        url: url,
        data: $form.serialize(),
        success: function(data) {
          showEventForm(url);
          showEventInfo(infoUrl);
          updateEventList(data.data.eventId, data.data.title, data.data.photoUrl);
        },
        error: function() {}
      });
    });

    $(document).on("keyup", ".artist_field .selectize-input input", function () {
      var artistSelectorContainer = $(this).closest(".artist-selector");
      var selectElement = $(artistSelectorContainer).find("select")[0];
      //var selectizeElement = $(artistSelectorContainer).find(".selectize-dropdown-content")[0];
      if ($(this).val().length > 1) {
        loadArtist($(this).val(), selectElement)
      }
    });

    $(document).on("click", ".show-gig-info-btn", function (event) {
      if (!$(this).hasClass("active")) {
        $(".show-gig-info-btn").addClass("active");
        $(".show-video-metrics-btn").removeClass("active");
        $("#edit-event-dashboard").addClass("active");
        $("#event-info").removeClass("active");
        resizeInfo();
      }
    });

    $(document).on("click", ".show-video-metrics-btn", function (event) {
      if (!$(this).hasClass("active")) {
        $(".show-video-metrics-btn").addClass("active");
        $(".show-gig-info-btn").removeClass("active");
        $("#edit-event-dashboard").removeClass("active");
        $("#event-info").addClass("active");
      }
    });

    $(document).on("click", "#event-info-close-btn", function () {
      var $container = $(this).closest(".artist-event");
      $container.removeClass("active");
      $container.prev(".artist-events-list").addClass("active");
    });

    $(document).on("click", "#event-info .publish-button", function () {
      selectedEventId = $(this).closest(".artist-set-actions").data("event-id");
      askPublish(selectedEventId);
    });

    $(document).on("click", "#event-info .download", function () {
      selectedEventId = $(this).closest(".artist-set-actions").data("event-id");
      showSelectFormat(selectedEventId);
    });

    $(document).on("click", ".set-changer", function (event) {
      event.preventDefault();
      $(".set-changer").removeClass("artist-active-set");
      var setId = $(this).data("set-id");
      if (!$(this).hasClass("artist-active-set")) {
        $(this).addClass("artist-active-set");
      }
      var $toShow = $(".event-metrics-container.flex-row#set-metrics-" + setId);
      var playListIndex = $toShow.data("set-number");

      currentListIndex = playListIndex;
      if (videoPlaying) {
        videoPlayer.playlistItem(playListIndex);
      }

    });


    //// METRICS DATE PICKER
    $(document).on("click", "#datepicker-dashboard-btn", function () {

      if ($(".artist-events-list-info .datepicker-container").data('shown')) {
        $(".event-metrics-container .datepicker-container").data('shown', false);
      } else {
        $(".artist-events-list-info  .datepicker-container").css("display", "flex")
        $(".artist-events-list-info .datepicker-container").data('shown', true);
        $("#dashboard-metrics-date-picker-from input").click();
        $("#dashboard-metrics-date-picker-from input").focus();
      }
    });

    $(document).on("click", "#dashboard-metrics-datepicker-close", function (event) {
      event.preventDefault();
      $("#dashboard-metrics-date-picker-from input").val("").datepicker("update");
      $("#dashboard-metrics-date-picker-to input").val("").datepicker("update");
      $(".event-metrics-container .datepicker-container").hide().data('shown', false);
      $($(".datepicker-dashboard-left-panel-item")[0]).click();
    })

    $(document).on("mouseup", function (event) {
      var $container = $("#datepicker-dashboard-left-panel");
      var $button = $("#metrics-datepicker-description");

      // if the target of the click isn't the container nor a descendant of the container
      if (!$container.is(event.target) && $container.has(event.target).length === 0) {
        if (!$button.is(event.target)) {
          $container.hide();
        }
      }
    });

    $(document).mouseup(function (e) {
      var container = $(".datepicker-dashboard-container");
      if (!container.is(e.target) && container.has(e.target).length === 0) {
        $(".event-metrics-container .datepicker-container").hide().data('shown', false);
      }
    });

    $(document).on("click", "#metrics-datepicker-description", function () {

      var $panel = $("#datepicker-dashboard-left-panel");

      if (!$panel.visible()) {
        $panel.show();
      } else if ($(".artist-events-list-info .datepicker-container").data('shown')) {
        $(".event-metrics-container .datepicker-container").hide().data('shown', false);
        $panel.show();
      } else {
        $panel.hide();
      }
    });

    $(document).on("click", "#metrics-datepicker-apply-button", function () {
      $(".artist-events-list-info .datepicker-container").hide().data('shown', false);
      var eventDateFrom = $("#dashboard-metrics-date-picker-from input").datepicker('getDate');
      var eventDateTo = $("#dashboard-metrics-date-picker-to input").datepicker('getDate');

      dateFrom = moment(eventDateFrom).format('MM/DD/YYYY');
      dateTo = moment(eventDateTo).format('MM/DD/YYYY');

      var newDateRange = dateFrom + " - " + dateTo;
      $("#metrics-datepicker-description").html(newDateRange);

      loadMetricsData();

    });

    $(document).on("click", ".datepicker-dashboard-left-panel > div", function () {

      if ($(this).data('date') == "all") {
        $("#dashboard-metrics-date-picker-from input").datepicker("update", new Date(2000, 0, 1));
        $("#dashboard-metrics-date-picker-to input").datepicker("update", new Date());
      } else if ($(this).data('date') == "period") {
        d = new Date();
        d.setFullYear(d.getFullYear() - 1);
        $("#dashboard-metrics-date-picker-from input").datepicker("update", d);
        $("#dashboard-metrics-date-picker-to input").datepicker("update", new Date());
      } else {
        $("#dashboard-metrics-date-picker-from input").datepicker("update", new Date($(this).data('start')));
        $("#dashboard-metrics-date-picker-to input").datepicker("update", new Date($(this).data('end')));
      }

      $("#metrics-datepicker-description").html($(this).text());

      $("#dashboard-metrics-date-picker-to input").click();
      $("#dashboard-metrics-date-picker-to input").focus();

      $("#datepicker-dashboard-left-panel").hide();

      loadMetricsData();

    });

  }

  function sendEventRequest(callbacks, loadFirstEvent) {

    var dateFrom = $datePickerFrom.datepicker("getDate");
    var dateTo = $datePickerTo.datepicker("getDate");

    if ($datePickerFrom.length == 0) {
      dateFrom = null;
    }

    if ($datePickerTo.length == 0) {
      dateTo = null;
    }

    params = {
      'page': ++currentPage
    };

    if (dateFrom) {
      utcDateFrom =
        dateFrom.getFullYear() +
        "/" +
        (dateFrom.getMonth() + 1) +
        "/" +
        dateFrom.getDate();
    }
    if (dateTo) {
      utcDateTo =
        dateTo.getFullYear() +
        "/" +
        (dateTo.getMonth() + 1) +
        "/" +
        dateTo.getDate();
    }

    if (dateFrom) {
      params["start_date_filter"] = utcDateFrom;
    }

    if (dateTo) {
      params["end_date_filter"] = utcDateTo;
    }

    var order = $('#artist_archive_order_filter').val();
    params.order = order;

    var isLeader = $('#artist_archive_status_filter').val();
    if (isLeader != "all") {
      params.leader_filter = isLeader === 'leader';
    }

    $.ajax({
      url: eventsUrl,
      data: params,
      dataType: 'json',
      success: function (data) {
        $("#artistEventsList").removeClass("artist-loading-gif");
        firstEventDate = data.first_event_date;
        lastEventDate = data.last_event_date;
        var callback;
        while (callback = callbacks.pop()){
          if (typeof callback === 'function') {
            callback(data, loadFirstEvent);
          }
        }
      }
    });

  }

  function updateShows(data, loadFirstEvent) {
    $("#event-load-gif").addClass("hidden");
    $("#artistEventsList").removeClass("artist-loading-gif");
    $('.concerts-footer').show();
    if (data.template) {
      if (data.total_results > 0) {
        if (currentPage > 1) {
          $("#artistEventsList").append(data.template);
        } else {
          $("#artistEventsList").html(data.template);
          $("#summary-data").removeClass("hidden");
          if (!$("#summary-no-results").hasClass("hidden")) {
            $("#summary-no-results").addClass("hidden");
          }
          showFirstEvent(data, loadFirstEvent);
        }
      } else {
        $("#artistEventsList").html(data.template);
        if (!$("#summary-data").hasClass("hidden")) {
          $("#summary-data").addClass("hidden");
        }
        $("#summary-no-results").removeClass("hidden");
        $('#edit-event-dashboard').html('');
        $('#event-info').html('');
      }
      $("#dashboard-filters").removeClass("hidden");
    }
    if (data.total_results) {
      $("#number-of-shows-label").html(data.total_results);
    }
    if (data.first_event_date) {
      $("#date-from-label").html(data.first_event_date);
    }
    if (data.last_event_date) {
      $("#date-to-label").html(data.last_event_date);
    }
    if (data.total_pages) {
      totalPages = data.total_pages;
      if (currentPage >= totalPages) {
        $('#next-page-btn').hide();
        $('#load-more-btn').hide();
      } else {
        $('#next-page-btn').show();
      }
    }
  }


  function showEventForm(url, callback) {

    if (!url) {
      return;
    }
    // We need to clone the loading gif to show it inside the container.
    // It will be removed when the container's html gets replaced.
    $('#edit-event-dashboard').html($('#event-edit-form-load-gif').clone().removeClass('hidden'));
    $.ajax({
      type: 'GET',
      url: url,
      success: function(data) {
        $('#event-edit-form-load-gif').addClass('hidden');
        $(document).off("click", "#add_more_artists");
        $('#edit-event-dashboard').empty();
        $('#edit-event-dashboard').html(data);
        EventForm.init(false, disableEditForm);
        image_cropping.init();
        disableEditForm;
        if (callback) {
          callback();
        }
      },
      error: function() {

      }
    });
  }

  function updateEventList(eventId, title, photoUrl) {
    var $row = $("#artist-event-row-" + eventId);
    $row.find("div.title").text(title);
    $row.find(".artist-event-picture img").attr("src", photoUrl);
  }

  function disableEditForm() {
    $("#event-edit-form input").prop("disabled", true);
    $("#event-edit-form select").prop("disabled", true);
    $(".event-edit-form-remove-artist").hide();
    $(".artist_field_span").show();
    $(".artist_field").addClass("hidden");
    $(".role_field_span").show();
    $(".role_field").addClass("hidden");
    $(".fa-sort").hide();
    $("#add_more_artists").hide();
    $(".mobile-edit-title.remove").css({"visibility": "hidden"});
    $(".artist-list-form .formset_table").find("tbody").sortable({disabled: true});
    $("#div_id_photo").find("label.white-border-button").addClass("disabled");
    $("#div_id_cropping").css("filter", "grayscale(1)");

  }

  function saveAttributes($element, restore) {

    var attrs = {};
    $element.each(function () {
      $.each(this.attributes, function () {
        if (this.specified) {
          if (restore) {
            if (this.name.indexOf("original") === 0) {
              attrs[this.name] = this.value;
            }
          } else {
            var storeName = "original-" + this.name;
            attrs[storeName] = this.value;
          }
        }
      });
    });

    $.each(attrs, function (key, value) {
      if (restore) {
        var attrName = key.replace("original-", "");
        $element.attr(attrName, value);
        $element.removeAttr(key);
      } else {
        $element.attr(key, value);
      }
    });

  }

  function updateUploadedImage(data) {

    var $imageId = $('#id_image_id');
    $imageId.attr("original-value", $imageId.val());
    $imageId.val(data.id);

    var $image = $("#div_id_photo img");
    $image.attr("original-src", $image.attr("src"));
    $image.attr("src", data.src);
    $('#div_id_cropping .controls').show();
    $('#div_id_photo img').toggleClass('hidden');

    var $imageInput = $("#id_photo");
    saveAttributes($imageInput);

    $imageInput.data("thumbnail-url", data.src);
    $imageInput.attr("data-thumbnail-url", data.src);

    $imageInput.data("min-width", data.width);
    $imageInput.data("min-height", data.height);
    $imageInput.data("org-width", data.width);
    $imageInput.data("org-height", data.height);

    resizeInfo();

  }

  function cancelUploadedImage() {

    var $imageId = $('#id_image_id');
    $imageId.val($imageId.attr("original-value"));

    var $image = $("#div_id_photo img");
    $image.attr("src", $image.attr("original-src"));

    var $imageInput = $("#id_photo");
    $imageInput.removeData();
    saveAttributes($imageInput, true);

    var $fileNameSpan = $("#file_name");
    $fileNameSpan.text($fileNameSpan.attr("original-text"));

    resizeInfo();
  }

  function enableEditForm () {
    $("#event-edit-form input").prop("disabled", false);
    $("#event-edit-form select").prop("disabled", false);
    $(".event-edit-form-remove-artist").show();
    $(".artist_field_span").hide();
    $(".artist_field").removeClass("hidden");
    $(".role_field_span").hide();
    $(".role_field").removeClass("hidden");
    $(".artist-list-form .formset_table").sortable({disabled: false});
    $(".fa-sort").show();
    $("#add_more_artists").show();
    $(".mobile-edit-title.remove").css({"visibility": "visible"});
    $(".artist-list-form .formset_table").find("tbody").sortable({disabled: false});
    $("#div_id_photo").find("label.white-border-button").removeClass("disabled");
    $("#div_id_cropping").css("filter", "none");
  }

  function showEventInfo(url) {

    if (!url) {
      return;
    }
    $('#event-info').html($('#event-info-load-gif').clone().removeClass('hidden'));
    $.ajax({
      type: 'GET',
      url: url,
      success: function(data) {
        $('#event-info-load-gif').addClass('hidden');
        $('#event-info').html(data);
        if (!isFuture) {
          var $videoInfo = $(data).find(".player-video-info");
          var playList = []
          $videoInfo.each(function () {
            var url = $(this).val();
            var id = $(this).data("id");
            var image = $(this).data("image");
            var sources = [{
              file: url,
              type: "mp4",
            }];
            var playInfo = {
              sources: sources,
              mediaid: id,
              image: image
            };
            playList.push(playInfo);
          });
          initializeMetricsDatePickers();
          setupPlayer(playList);
        }
      },
      error: function() {

      }
    });
  }

  function activateFirstItem() {
    $(".artist-event-row:first-of-type").addClass("active");
  }

  function showFirstEventForm(data) {
    var $row = $(data.template).first("artist-event-row");
    var url = $row.data('ajax-edit-url');
    showEventForm(url, activateFirstItem);
  }

  function showFirstEventInfo(data) {
    var $row = $(data.template).first("artist-event-row");
    var url = $row.data('ajax-info-url');
    showEventInfo(url);
  }

  function showFirstEvent(data, loadFirstEvent) {

    if (loadFirstEvent === true) {
      fromDateLimit = firstEventDate;
      toDateLimit = lastEventDate;
      $datePickerFrom.datepicker("setStartDate", fromDateLimit);
      $datePickerTo.datepicker("setEndDate", toDateLimit);
    }

    showFirstEventForm(data);
    showFirstEventInfo(data);

  }

  function setupPlayer(playList) {

    videoPlayer = jwplayer("player-video").setup({
      primary: 'html5',
      playlist: playList,
      skin: jwPlayerSkin,
      width: "100%",
      aspectratio: "16:9",
    });
    videoPlayer.on('play', function () {

      videoPlaying = true;
      var videoListIndex = videoPlayer.getPlaylistIndex();

      console.log(videoListIndex);
      console.log(currentListIndex);

      if (videoListIndex != currentListIndex) {
        if (currentListIndex) {
          videoPlayer.playlistItem(currentListIndex);
        }
      }

    });

    videoPlayer.on('pause', function() {


    });

  }

  function loadMore(loadFirstEvent) {

    $("#event-load-gif").removeClass("hidden");
    $('.concerts-footer').hide();

    var  optNumber = 0;
    var params = {};

    if (currentPage >= totalPages) {
      return;
    }

    var callbacks = [updateShows];
    sendEventRequest(callbacks, loadFirstEvent);
  }

});

function askPrivate(eventId) {
  $('#privateConfirm').modal('show');
  selectedEventId = eventId;
}

function askPublish(eventId) {
  $('#publishConfirm').modal('show');
  selectedEventId = eventId;
}

function makeSetPrivate() {
    $.post('/events/sets/' + selectedSetId + '/private/', {
      csrfmiddlewaretoken: csrfToken
    }, function (data, status) {
    });
    hideMakePrivate();
    $("#set-id-" + selectedSetId).find('.publish-button').replaceWith(
        '<button class="publish-button" onclick="askPublish(' + selectedSetId + ')">Publish</button>'
    )
    $("#set-id-" + selectedSetId).find('.set-status').text('Hidden')
    showSuccess('private')
}

function publishEvent() {
    hideMakePrivate();
    hidePublish();
    $.post('/events/' + selectedEventId + '/publish/', {
      csrfmiddlewaretoken: csrfToken
    }, function (data, status) {
      var $button = $("#artist-event-action-" + selectedEventId).find("button.publish-button");
      var newText = "Make Private";
      if (!data.is_published) {
        newText = "Publish";
      }
      $button.text(newText);
    });
}

function hideMakePrivate() {
    $('#privateConfirm').modal('hide');
}

function hidePublish() {
    $('#publishConfirm').modal('hide');
}

function showSelectFormat() {
    var $downloadDialog = $('#downloadFormat');
    var $table = $("#track-list-tbl");
    var $clonedTable = $table.clone(true).removeClass("hidden").removeAttr("id");
    var $tableContainer = $downloadDialog.find(".table-container");
    if ($tableContainer.find("table").length === 0) {
      $tableContainer.append($clonedTable);
    } else {
      $tableContainer.html('');
      $tableContainer.append($clonedTable);
    }
    $downloadDialog.modal('show');
}

var resizeTimer;


function loadArtist(value, select) {
  $.ajax({
    type: 'GET',
    url: '/search/artist_form_autocomplete/?artist-start=' + value,
    success: function(data){
        data.artist_list.forEach(function(artist) {

            // Select already selected artists and  exclude them from the options.
            var $artists = $(".artist_field option[selected='selected']");
            var exclude = $(".artist_field option[selected='selected']").map(function () {
              return $(this).val();
            }).get();

            if (exclude.indexOf(artist.val.toString()) < 0) {
              select.selectize.addOption({ value: artist.val, text: artist.full_name });
              select.selectize.refreshOptions();
            }
        })

    }
  })
}

function resizeInfo() {
  $(".jcrop-holder").remove();
  $("#id_cropping-image").remove();
  $(".field-box.allow-fullsize").remove();
  image_cropping.init();
}

$(window).on('resize', function(e) {

  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(resizeInfo, 1000);

});


function initializeMetricsDatePickers () {

  var $datePickerFromMetrics = $('#dashboard-metrics-date-picker-from input');
  $datePickerFromMetrics.datepicker({
    format: 'mm/dd/yyyy',
    autoclose: true,
    container: '#dashboard-metrics-date-picker-from',
    showOnFocus: false
  });

  $datePickerFromMetrics.on('changeDate', function (newDate) {
    eventDateFrom = newDate.date;
    $("#dashboard-metrics-date-picker-to input").click();
    $("#dashboard-metrics-date-picker-to input").focus();
  });

  $datePickerFromMetrics.on('click', function () {
    var dropdown = $('#dashboard-metrics-date-picker-from .dropdown-menu');
    if (!(dropdown[0] && dropdown[0].style.display === 'block')) {
      $datePickerFrom.datepicker('show');
    }
  });

  //////////////////////

  var $datePickerToMetrics = $('#dashboard-metrics-date-picker-to input');
  $datePickerToMetrics.datepicker({
    format: 'mm/dd/yyyy',
    autoclose: false,
    container: '#dashboard-metrics-date-picker-to',
    showOnFocus: false
  });

  $datePickerToMetrics.on('changeDate', function (newDate) {
    eventDateTo = newDate.date;

    from = (eventDateFrom.getMonth() + 1) + '/' + eventDateFrom.getDate() + '/' + eventDateFrom.getFullYear();
    to = (eventDateTo.getMonth() + 1) + '/' + eventDateTo.getDate() + '/' + eventDateTo.getFullYear();

    $("#datepicker-description").html(from + " - " + to);
  });

  $datePickerToMetrics.on('click', function () {
    var dropdown = $('#dashboard-metrics-date-picker-to .dropdown-menu');
    if (!(dropdown[0] && dropdown[0].style.display === 'block')) {
      $datePickerTo.datepicker('show');
    }
  });
}

var loadMetricsData = function () {

  var plays = document.getElementById("play-value");
  var time = document.getElementById("time-value");
  var mobilePlays = document.getElementById("mobile-play-value");
  var mobileTime = document.getElementById("mobile-time-value");
  var eventDateFrom = $("#dashboard-metrics-date-picker-from input").datepicker('getDate');
  var eventDateTo = $("#dashboard-metrics-date-picker-to input").datepicker('getDate');

  var data = {};
  data.start = moment(eventDateFrom).format('YYYY-MM-DD');
  data.end = moment(eventDateTo).format('YYYY-MM-DD');

  $(".event-metrics-container.metrics").each(function () {
    var setId = $(this).data("set-id");
    var $container = $("#set-metrics-" + setId);
    data.set_id = setId;
    $.ajax(countsURL, {
      data: data,
      success: function (response) {
          console.log('-----------------------------');
          console.log(response);
          $container.find(".play-value").html(response.playCount);
          var playedSeconds = response.secondsPlayed;
          var formattedSeconds = moment.utc((playedSeconds) * 1000).format('HH:mm:ss');
          $container.find(".time-value").html(formattedSeconds);
      },
      type: 'GET',
      xhrFields: {
          withCredentials: true
      }
    });

  });
};
