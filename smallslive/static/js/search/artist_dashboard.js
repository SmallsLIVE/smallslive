
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
  loadMore(false, true);

  function initializeFilters() {

    $('#artist_archive_status_filter').on('change', function () {
      currentPage = 0;
      totalPages = 1;
      loadMore(false, true);
      $('#artistEventsList').html("");
    });

    $('#artist_archive_order_filter').on('change', function () {
      currentPage = 0;
      totalPages = 1;
      loadMore(false, true);
      $('#artistEventsList').html("");
    });

    $('#load-more-btn').on('click', function () {
      loadMore(false);
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
      $datePickerTo.datepicker("setStartDate", newDate.date);
    });

    $datePickerFrom.on('click', function () {
      var dropdown = $('#search-date-picker .dropdown-menu');
      if (dropdown[0] && dropdown[0].style.display === 'block') {
        $datePickerFrom.datepicker('hide');
      } else {
        $datePickerFrom.datepicker('show');
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
      // Means any ajax results will not append to existing items.
      // For pagination use apply = false;

      sendEventRequest(
        [updateShows]
      );

      $datePickerFrom.click();
      $datePickerFrom.focus();

      $datePickerFrom.datepicker("setEndDate", newDate.date);

    });

    $datePickerTo.on('click', function () {
      var dropdown = $('#dashboard-desktop-datepicker #search-date-picker .dropdown-menu');
      if (dropdown[0] && dropdown[0].style.display === 'block') {
        $datePickerTo.datepicker('hide');
      } else {
        $datePickerTo.datepicker('show');
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
        $("#dashboard-desktop-datepicker").css("display", "flex").hide().fadeIn(500, function() {
            $(document).bind("click", hide);
            $("#dashboard-desktop-datepicker").data('shown', true);
        });

        $("#search-date-picker-from-dashboard input").click();
        $("#search-date-picker-from-dashboard input").focus();
    }

    function hide(event) {
        var $target = $(event.target);
        if (($target.closest('.noclick').length == 0) &&
        (!($target.hasClass('day') || $target.hasClass('year')))) {
            $('#dashboard-desktop-datepicker').fadeOut(500, function () {
                $(document).unbind('click');
                $('#dashboard-desktop-datepicker').data('shown', false);
            });
        }
    }

    $("#dashboard-apply-button").click(function () {
        $("#dashboard-desktop-datepicker").fadeOut(500, function () {
            $(document).unbind("click");
            $("#dashboard-desktop-datepicker").data('shown', false);
        });
        currentPage = 0;
        totalPages = 1;
        $('#artistEventsList').html("")
        $('#artistEventsList').addClass("artist-loading-gif");
        loadMore(false);

    });

    $("#dashboard-desktop-reset").click(function () {
        defaultStatusValue = $("#artist_archive_status_filter option:first-child").val()
        defaultStatusText = $("#artist_archive_status_filter option:first-child").text()
        defaultOrderValue = $("#artist_archive_order option:first-child").val()
        defaultOrderText = $("#artist_archive_order option:first-child").text()
        $("#artist_archive_status_filter").val(defaultStatusValue)
        $("#artist_archive_status_filter + .select-selected").text(defaultStatusText)
        $("#artist_archive_order").val(defaultOrderValue)
        $("#artist_archive_order + .select-selected").text(defaultOrderText)
        $("#search-date-picker-from-dashboard").find(".date-picker-text").val("")
        $("#search-date-picker-to-dashboard").find(".date-picker-text").val("")
        currentPage = 0;
        totalPages = 1;
        $('#artistEventsList').html("")
        $('#artistEventsList').addClass("artist-loading-gif");
        loadMore(false);
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
        $(this).text('Edit');
      }
    });

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

    $(document).on("click", "#show-gig-info-btn", function (event) {
      if (!$(this).hasClass("active")) {
        $(this).addClass("active");
        $("#show-video-metrics-btn").removeClass("active");
        $("#edit-event-dashboard").addClass("active");
        $("#event-info").removeClass("active");
      }
    });

    $(document).on("click", "#show-video-metrics-btn", function (event) {
      if (!$(this).hasClass("active")) {
        $(this).addClass("active");
        $("#show-gig-info-btn").removeClass("active");
        $("#edit-event-dashboard").removeClass("active");
        $("#event-info").addClass("active");
      }
    });

    $(document).on("click", "#event-info-close-btn", function () {
      var $container = $(this).closest(".artist-event");
      $container.removeClass("active");
      $container.prev(".artist-events-list").addClass("active");
    })

    $(document).on("click", ".set-changer", function (event) {
      event.preventDefault();
      $(".set-changer").removeClass("artist-active-set");
      var setId = $(this).data("set-id");
      if (!$(this).hasClass("artist-active-set")) {
        $(this).addClass("artist-active-set");
      }
      var $toShow = $(".event-metrics-container.flex-row#set-metrics-" + setId);
      var playListIndex = $toShow.data("set-number");
      var $toHide = $(".event-metrics-container.flex-row");
      $toHide.each(function () {
        if (!$(this).hasClass("hidden")) {
          $(this).addClass("hidden");
        }
      });
      $toShow.removeClass("hidden");

      videoPlayer.playlistItem(playListIndex);

    })

  }

  function sendEventRequest(callbacks) {

    var dateFrom = $datePickerFrom.datepicker("getDate");
    var dateTo = $datePickerTo.datepicker("getDate");

    params = {
      'start_date_filter': dateFrom,
      'end_date_filter': dateTo,
      'page': ++currentPage
    };

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
            callback(data);
          }
        }
      }
    });

  }

  function updateShows(data) {
    $("#event-load-gif").addClass("hidden");
    $("#artistEventsList").removeClass("artist-loading-gif");
    $('.concerts-footer').show();
    if (data.template) {
      if (currentPage > 1) {
        $("#artistEventsList").append(data.template);
      } else {
        $("#artistEventsList").html(data.template);
      }
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
  }

  function showEventInfo(url) {
    $('#event-info').html($('#event-info-load-gif').clone().removeClass('hidden'));
    $.ajax({
      type: 'GET',
      url: url,
      success: function(data) {
        $('#event-info-load-gif').addClass('hidden');
        $('#event-info').html(data);
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
        setupPlayer(playList);
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

  function showFirstEvent(data) {

    fromDateLimit = firstEventDate;
    toDateLimit = lastEventDate;
    $datePickerFrom.datepicker("setStartDate", fromDateLimit);
    $datePickerFrom.datepicker("setEndDate", toDateLimit);
    $datePickerTo.datepicker("setStartDate", fromDateLimit);
    $datePickerTo.datepicker("setEndDate", toDateLimit);

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



    });
    videoPlayer.on('pause', function() {

    });

  }

  function loadMore(mobile, loadFirstEvent) {

    $("#event-load-gif").removeClass("hidden");
    $('.concerts-footer').hide();

    var  optNumber = 0;
    var params = {};

    if (currentPage >= totalPages) {
      return;
    }

    if (mobile === true) {

      params.page = ++currentPage;
      params.start_date_filter = $('#start-date').val();
      params.end_date_filter =  $('#until-date').val();

      todayDate=(new Date().getMonth() + 1)  + "/" + new Date().getDate() + "/" + new Date().getFullYear();
      if ( params.end_date_filter === todayDate || params.end_date_filter !== "" && params.start_date_filter !== "" ) {
        optNumber +=1;
      }

      if (statusFilter !== 'all') {
        params.leader_filter = statusFilter === 'leader';
        optNumber +=1;
      }

      var orderMobile = $('#refine-order-filter option:selected').val()
      if (orderMobile !== 'newest') {
        params.order = orderMobile;
        optNumber +=1;
      }
      $('#filter-number').text("(" + optNumber + ")");
    }

    var callbacks = [updateShows];
    if (loadFirstEvent) {
      callbacks.push(showFirstEvent);
    }
    sendEventRequest(callbacks);
  }

});

function askPrivate(setId) {
    $('#privateConfirm').modal('show');
    selectedSetId=setId;
}

function askPublish(setId) {
    $('#publishConfirm').modal('show');
    selectedSetId=setId;
}
function makeSetPrivate() {
    $.post('/events/sets/' + selectedSetId + '/private/', {
      csrfmiddlewaretoken: '{{ csrf_token }}'
    }, function (data, status) {
    });
    hideMakePrivate();
    $("#set-id-" + selectedSetId).find('.publish-button').replaceWith(
        '<button class="publish-button" onclick="askPublish(' + selectedSetId + ')">Publish</button>'
    )
    $("#set-id-" + selectedSetId).find('.set-status').text('Hidden')
    showSuccess('private')
}

function showSuccess(state) {
    //var $publishSuccess = $('#publishSuccess');
    //$publishSuccess.find('.success-state').text(state);
    //$publishSuccess.modal('show')
    $("#hide-scss-btn").data("type", state)
    hideSuccess()
}

function publishSet() {
    $.post('/events/sets/' + selectedSetId + '/publish/', {
      csrfmiddlewaretoken: '{{ csrf_token }}'
    }, function(data, status) {
    });
    hidePublish();
    $("#set-id-" + selectedSetId).find('.publish-button').replaceWith(
        '<button class="publish-button" onclick="askPrivate(' + selectedSetId + ')">Make Private</button>'
    )
    $("#set-id-" + selectedSetId).find('.set-status').text('Published');
    showSuccess('public')
}

function hideMakePrivate() {
    $('#privateConfirm').modal('hide');
}

function hidePublish() {
    $('#publishConfirm').modal('hide');
}

function hideSuccess(data) {
    $('#publishSuccess').modal('hide');
    var $currentSet = $(".artist-active-set.accent-color.set-changer")[0];
    var successType = $("#hide-scss-btn").data("type");
    if (successType === "public" || data ==="public"){
        $("#private-button").removeClass("hidden")
        $("#public-button").addClass("hidden")
        $("#mobile-private-button").removeClass("hidden")
        $("#mobile-public-button").addClass("hidden")
        $("#mobile-private-button").click()
    };
    if (successType === "private" || data ==="private"){
        $("#private-button").addClass("hidden")
        $("#public-button").removeClass("hidden")
        $("#mobile-private-button").addClass("hidden")
        $("#mobile-public-button").removeClass("hidden")
        $("#mobile-public-button").click()
    };
}

function showSelectFormat(videoUrl, audioUrl) {
    var $downloadFormat = $('#downloadFormat');
    var audioButton = $downloadFormat.find('#downloadFormatAudioUrl');
    var videoButton = $downloadFormat.find('#downloadFormatVideoUrl');

    if (audioUrl !== '') {
        audioButton.attr({href: audioUrl}).on('click', function () {
            $downloadFormat.modal('hide');
        });
        audioButton.find('button').prop('disabled', false);
    } else {
        audioButton.find('button').prop('disabled', true);
    }

    if (videoUrl !== '') {
        videoButton.attr({href: videoUrl}).on('click', function () {
            $downloadFormat.modal('hide');
        });
        videoButton.find('button').prop('disabled', false);
    } else {
        videoButton.find('button').prop('disabled', true);
    }
    $downloadFormat.modal('show');
}

var resizeTimer;


function loadArtist(value, select) {
  $.ajax({
    type: 'GET',
    url: '/search/artist_form_autoconplete/?artist-start=' + value,
    success: function(data){
        data.artist_list.forEach(function(artist) {
            select.selectize.addOption({ value: artist.val, text: artist.full_name })
            select.selectize.refreshOptions()
        })

    }
  })
}

$(window).on('resize', function(e) {

  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(function() {

    $(".jcrop-holder").remove();
    $("#id_cropping-image").remove();
    $(".field-box.allow-fullsize").remove();
    image_cropping.init();

  }, 1000);

});