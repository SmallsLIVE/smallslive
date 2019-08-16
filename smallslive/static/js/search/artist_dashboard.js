
$(document).ready(function () {

  var $datePickerFrom = $("#search-date-picker-from-dashboard input");
  var $datePickerTo = $("#search-date-picker-to-dashboard input");

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
        updateShows
      );
      $datePickerFrom.datepicker("setEndDate", dateTo);

      $datePickerFrom.click();
      $datePickerFrom.focus();

    });

    $datePickerTo.on('click', function () {
      var dropdown = $('#dashboard-desktop-datepicker #search-date-picker .dropdown-menu');
      if (dropdown[0] && dropdown[0].style.display === 'block') {
        $datePickerTo.datepicker('hide');
      } else {
        $datePickerTo.datepicker('show');
      }
    });

  }

  function bindEvents() {

    $(document).on('click', '.artist-event-row', function () {

      if( viewPortLength("width") < 960){
        $('.artist-dashboard-event-container').show("slide", { direction: "right" }, 300);
        $('.artist-events-list').hide("slide", { direction: "left" }, 300);
      }

      var url = $(this).data('ajax-edit-url');
      showEventForm(url);
      url = $(this).data('ajax-info-url');
      showEventInfo(url);
    });

    $(document).on('click', '#form-edit-button', function () {
      $("#submit-id-submit").removeAttr('disabled');
      enableEditForm();
    });

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


  function showEventForm(url) {
    $('#edit-event-dashboard').html($('#event-edit-form-load-gif').clone().removeClass('hidden'));
    $.ajax({
      type: 'GET',
      url: url,
      success: function(data) {
        $('#event-edit-form-load-gif').addClass('hidden');
        $('#edit-event-dashboard').html(data);
        EventForm.SITE_URL = "{{ request.META.HTTP_HOST }}";
        EventForm.init(false);
        image_cropping.init();
        $("#event-edit-form input").prop("disabled", true);
        $("#event-edit-form select").prop("disabled", true);
      },
      error: function() {

      }
    });
  }

  function enableEditForm () {
    $("#event-edit-form input").prop("disabled", false);
    $("#event-edit-form select").prop("disabled", false);
  }

  function showEventInfo(url) {
    $('#event-info').html($('#event-info-load-gif').clone().removeClass('hidden'));
    $.ajax({
      type: 'GET',
      url: url,
      success: function(data) {
        $('#event-info-load-gif').addClass('hidden');
        $('#event-info').html(data);

      },
      error: function() {

      }
    });
  }

  function showFirstEventForm(data) {
    $row = $(data.template).first("artist-event-row");
    var url = $row.data('ajax-edit-url');
    showEventForm(url);
  }

  function showFirstEventInfo(data) {
    $row = $(data.template).first("artist-event-row");
    var url = $row.data('ajax-info-url');
    showEventInfo(url);
  }

  function showFirstEvent(data) {

    showFirstEventForm(data);
    showFirstEventInfo(data);

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

