var searchTerm, artistSearchTerm, artistInstrument, artistPageNum, artistMaxPageNum, eventPageNum, eventMaxPageNum, venueFilter, eventFilter, eventDateFrom, eventDateTo, apply, artist_pk, show_event_venue;

function sendArtistRequest(callback) {
    $.ajax({
        url: '/search/ajax/artist/',
        data: {
            'main_search': searchTerm,
            'artist_search': artistSearchTerm,
            'instrument': artistInstrument,
            'page': artistPageNum
        },
        dataType: 'json',
        success: function (data) {
            if (data.template) {
                $("#artist-subheader").html(data.showingResults);
                $("#artists").append(data.template);
                artistMaxPageNum = data.numPages;

                // if (artistPageNum === 1) {
                //     $(".left_arrow").addClass('artist-arrow-disabled');
                // } else {
                //     $(".left_arrow").removeClass('artist-arrow-disabled');
                // }

                // if (artistPageNum === artistMaxPageNum) {
                //     $(".right_arrow").addClass('artist-arrow-disabled');
                // } else {
                //     $(".right_arrow").removeClass('artist-arrow-disabled');
                // }
            }
            callback(data);
        },
        error: function (data) {
            $("#artist-load-gif").css("display", "none");
            $(".container-list-article").css("height", "auto");
            $(".right_arrow").css('visibility', 'hidden');
        }
    });
}

function changePage(param) {
    eventPageNum = parseInt(param.getAttribute("data-page-number"));
    sendEventRequest();
}

function loadMoreEvents() {
    if( $("main.calendar").length > 0){
        show_event_venue = true
    }
    eventPageNum += 1;
    $("#load-more-btn").hide();
    $("#event-load-gif").css("display", "block");
    sendEventRequest();
}

$(document).on('click', '#artists .artist-row', function() {
  var artistId = $(this).data('id');
  $.ajax({
    url: '/search/ajax/artist-info/',
    data: {
      'id': artistId
    },
    dataType: 'json',
    success: function (data) {
      if (data.template) {
        $('#musicianContent').hide();
        $('.artist-search-profile-container').html(data.template);
        $('.artist-search-profile-container')[0].style.display = 'block';
        $('#artist-subheader').html('SHOWING 1 - 1 OF 1 RESULTS');
        $('.artist-search-profile-container .close-button-parent').show();
        $('.search-tabs').addClass('hidden');
        $('*[data-toggle-tab-group="search-results"][data-toggle-tab="archived-shows"]').show();

        eventDateFrom = eventDateTo = null;
        artist_pk = artistId;

        apply = true;
        eventPageNum = 1;
        sendEventRequest();
      }
    }
  });
});

function toggleArrows() {
    var style = $('#artists').css('left');
    var columnWidth = parseInt($('.artist-column').first().css('width').replace('px', ''));
    var left = style.replace('px', '');
    var pseudoPage = parseInt(-left / columnWidth);
    $('.left_arrow').css('visibility', pseudoPage == 0 ? 'hidden' : 'visible');
    $('.right_arrow').css('visibility', pseudoPage == $('.artist-column').length - 1 ? 'hidden': 'visible');
}

toggleArrows();

function sendEventRequest() {
    var utcDateFrom = null;
    var utcDateTo = null;
    
    if (eventDateFrom) {
        utcDateFrom = eventDateFrom.getFullYear() + '/' + (eventDateFrom.getMonth() + 1) + '/' + eventDateFrom.getDate();
    }
    if (eventDateTo) {
        utcDateTo = eventDateTo.getFullYear() + '/' + (eventDateTo.getMonth() + 1) + '/' + eventDateTo.getDate();
    }
    searchFilters = {
        'main_search': searchTerm,
        'page': eventPageNum,
        'order': eventOrderFilter,
        'date_from': utcDateFrom ? utcDateFrom : null,
        'date_to': utcDateTo ? utcDateTo : null,
        'artist_pk': artist_pk ? artist_pk : null,
        'partial': true,
        'show_event_venue' : show_event_venue ? show_event_venue : null
    };
    if (venueFilter) {
        searchFilters['venue'] = venueFilter;
    }
    $.ajax({
        url: '/search/ajax/event/',
        data: searchFilters,
        dataType: 'json',
        success: function (data) {
            if (data.template) {
                var $showsContainer = $('.search-content .shows-container');
                $('#event-subheader').html(data.showingResults);
                $('#event-subheader-footer').html(data.showingResults);

                if (apply || eventFilter) {
                    apply = false;
                    eventFilter = false;
                    $showsContainer.html('');
                    $('#events .shows-container').html('');
                }
                 var article = $(data.template).find('article');
                 if (!article.length) {
                     $('#events .shows-container').html(data.template);
                     $showsContainer.html(data.template);
                 }
                 article.each(function( index ) {
                     $('#events .shows-container').append($( this ));
                     $showsContainer.append($( this ));
                 });

                eventMaxPageNum = data.numPages;
                $("#event-load-gif").css("display", "none");
                $("#load-more-btn").toggle(data.numPages != eventPageNum);
            }
        }
    });
}

$(document).ready(function () {
    searchTerm = getUrlParameter("q");
    searchTerm = searchTerm ? searchTerm.replace(/\+/g, ' '): '';
    artistSearchTerm = "";
    artistInstrument = "";
    artistPageNum = eventPageNum = 1;
    artistMaxPageNum = eventMaxPageNum = 2;
    apply = false;
    eventFilter = false;
    var maxPseudopage = 4;

    $("[name='q']").val(searchTerm);
    $('#artist-search').val('');

    $(".visible-xs.left_arrow").click(function () {
        var style = $('#artists').css('left');
        var columnWidth = parseInt($('.artist-column').first().css('width').replace('px', ''));
        var left = parseInt(style.replace('px', ''));
        if (left % columnWidth) {
            return;
        }
        $('#artists').animate({left: (left + columnWidth) + 'px'},
            100,
            'linear',
            function() {
                toggleArrows();
            });
    });

    $(".visible-xs.right_arrow").click(function () {
        var style = $('#artists').css('left');
        var columnWidth = parseInt($('.artist-column').first().css('width').replace('px', ''));
        var left = parseInt(style.replace('px', ''));
        if (left % columnWidth) {
            return;
        }
        var pseudoPage = parseInt(-left / columnWidth);
        $('#artists').animate(
            {left: (left - columnWidth) + 'px'},
            100,
            'linear',
        function() {
            toggleArrows();
        });
        if (artistPageNum !== artistMaxPageNum && maxPseudopage - pseudoPage <= 4) {
            artistPageNum += 1;
            sendArtistRequest(function() {
                maxPseudopage += 4;
            });
        }
    });

    $("#next-page-btn").click(function () {
        if (eventPageNum !== eventMaxPageNum) {
            eventPageNum += 1;
            sendEventRequest();
        }
    });

    $('#events-filter').change(function () {
        eventFilter = true;
        eventOrderFilter = $(this).val();
        venueFilter = "all";
        eventPageNum = 1;

        sendEventRequest();
    });

    $('#period-filter, #refine-period-filter').change(function () {
        eventFilter = true;

        if (datePickerFromDate) {
            var start = datePickerFromDate;
        } else  {
            var start = new Date();
        }

        if ($(this).val() == 'All Upcoming') {
            eventDateTo = null;
            eventDateFrom = new Date();
        }
        else if ($(this).val() == 'One Day') {
            eventDateTo = new Date(start.getTime() + 1 * 24 * 60 * 60 * 1000);
            eventDateFrom = start;
        }
        else if ($(this).val() == 'One Week') {
            eventDateTo = new Date(start.getTime() + 7 * 24 * 60 * 60 * 1000);
            eventDateFrom = start;
        }
        else if ($(this).val() == 'One Month') {
            eventDateTo = new Date(start.getTime() + 31 * 24 * 60 * 60 * 1000);
            eventDateFrom = start;
        }

        var $filter = $(this);
        if ($filter.attr('id').indexOf('refine') > -1) {
            $("#search-date-picker-from-refine input").datepicker("update", eventDateFrom);
            $("#search-date-picker-to-refine input").datepicker("update", eventDateTo);

        } else {
            $("#search-date-picker-from input").datepicker("update", eventDateFrom);
            $("#search-date-picker-to input").datepicker("update", eventDateTo);

        }
        
        if (eventDateTo) {
            $(".datepicker-btn").html('From <span class="from accent-color"></span> to <span class="to accent-color"></span>');
            $('.datepicker-btn span.from').text(eventDateFrom.toLocaleDateString());
            $('.datepicker-btn span.to').text(eventDateTo.toLocaleDateString());
        } else {
            $(".datepicker-btn").html("DATE");
        }
        if ($('.shows-calendar .datepicker-btn')){
            $(".datepicker-btn").html("DATE");
            $("#calendar-date-range .title2").html( eventDateFrom.toLocaleDateString() + " - " + (eventDateTo != null ? eventDateTo.toLocaleDateString() : ""));
        }

        eventPageNum = 1;
        sendEventRequest();
    });

    var delay = (function () {
        var timer = 0;
        return function (callback, ms) {
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
        };
    })();

    $("#artist-search").keyup(function () {
        delay(function () {
            artistPageNum = 1;
            artistSearchTerm = $('#artist-search').val();
            //$("#artists").hide();
            //$("#artist-load-gif").css("display", "flex");
            $(".container-list-article").addClass("artist-loading-gif");
            $("#artists").css("visibility", "hidden");
            sendArtistRequest();
        }, 700);
    });

    $(".instrument-btn").click(function () {

        if (!$(".instruments-container").is(":visible")) {
            $(".instruments-container").css("display", "flex");
        } else {
            $(".instruments-container").css("display", "none");
        }
    });

    $(document).on('click', function(event) {
        // Instruments Container was clicked.
        var onContainer = $(event.target).closest('.instruments-container').length;
        // Dropdown button was clicked.
        var onButton = $(event.target.closest('.instrument-btn')).length;
        var containerVisible = $('.instruments-container').is(':visible');
        if (containerVisible && !onButton && !onContainer) {
            $(".instruments-container").css('display', 'none');
        }
    });

    $('.instrument').click(function () {
        artistInstrument = $(this).data('instrument');
        $('.instrument-btn').text(artistInstrument || 'Instrument');
        artistPageNum = 1;

        $(".container-list-article").addClass("artist-loading-gif");
        $("#artists").css("visibility", "hidden");

        sendArtistRequest();
        $(".instruments-container").css("display", "none");
    });

    ////////////////

    $('.datepicker-btn').bind("click", ToggleDisplay);

    function ToggleDisplay() {
        if ($(".datepicker-container").data('shown'))
            hide();
        else 
            display();
    }

    function display() {
        var $datePickerContainer = $(".datepicker-container");
        $datePickerContainer.css({'left': datePickerLeft, 'top': datePickerTop});
        $datePickerContainer.css("display", "flex").hide().fadeIn(500, function() {
            $(document).bind("click", hide);
            $(".datepicker-container").data('shown', true);
        });

        var $datePickerInput = $(datePickerInputSelector);
        $datePickerInput.click();
        $datePickerInput.focus();  
    }

    function hide() {   
        if (($(window.event.toElement).closest('.noclick').length == 0) &&
        (!($(window.event.toElement).hasClass("day") || $(window.event.toElement).hasClass("year")))) {
            $(".datepicker-container").fadeOut(500, function () {
                $(document).unbind("click");
                $(".datepicker-container").data('shown', false);
            });
        }
    }

    /////////////////////

    var $datePickerFrom = $('#search-date-picker-from input');
    $datePickerFrom.datepicker({
        format: 'mm/dd/yyyy',
        autoclose: true,
        container: '#search-date-picker-from',
        showOnFocus: false,
        startDate: defaultFromDate,
        endDate: defaultToDate
    });

    if (setFromDate) {
      $datePickerFrom.datepicker('setDate', defaultFromDate);
      datePickerFromDate = new Date(defaultFromDate);
    }

    $datePickerFrom.on('changeDate', function (newDate) {
        datePickerFromDate = newDate.date;
        if (!datePickerToDate || datePickerFromDate > datePickerToDate) {
           datePickerToDate = datePickerFromDate;
           $datePickerTo.datepicker('setDate', datePickerToDate);
        }
        //$('#events-filter').val('oldest');
        //$("[value='oldest']").click();
        $("#search-date-picker-to input").click();
        $("#search-date-picker-to input").focus();
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

    var $datePickerTo = $('#search-date-picker-to input');
    $datePickerTo.datepicker({
        format: 'mm/dd/yyyy',
        autoclose: false,
        container: '#search-date-picker-to',
        showOnFocus: false,
        startDate: defaultFromDate,
        endDate: defaultToDate
    })

    if (setToDate) {
      $datePickerTo.datepicker('setDate', defaultToDate);
      datePickerToDate = new Date(defaultToDate);
    }

    $datePickerTo.on('changeDate', function (newDate) {
        datePickerToDate = newDate.date;
    });

    $datePickerTo.on('click', function () {
        var dropdown = $('#search-date-picker .dropdown-menu');
        if (dropdown[0] && dropdown[0].style.display === 'block') {
            $datePickerTo.datepicker('hide');
        } else {
            $datePickerTo.datepicker('show');
        }

    });

    ///////////

    // If only one result -> go to artist
    var $artists = $('.artist-row');
    if ($artists.length == 1) {
      $artists.click();
    } else {
      $('#artists').removeClass('invisible');
    }

    $(document).on('click', '.artist-search-profile-container .close-button', function () {
        // If only one artist, assume back to search means
        // actually resetting search
        var $artists = $('.artist-row');
        if ($artists.length == 1) {
          window.location.href = '/search';
        } else {
          $("#musicianContent").show();
          $(".artist-search-profile-container").hide();
          $('.artist-search-profile-resume .close-button').show();
          $('.search-tabs').removeClass('hidden');
          artist_pk = null;
          apply = true;
          eventPageNum = 1;
          $('[data-toggle-tab-group="search-results"][data-toggle-tab-target]').show();
          $('[data-toggle-tab-group="search-results"][data-toggle-tab]').hide();
          $('[data-toggle-tab-group="search-results"][data-toggle-tab="musicians"]').show();
          sendEventRequest();
        }
    });

    $("#apply-button").click(function () {
        if($(this).closest('.calendar').length > 0){
            show_event_venue = true
        }
        eventDateFrom = datePickerFromDate;
        eventDateTo = datePickerToDate;
        apply = true;
        eventPageNum = 1;
        $(".datepicker-container").hide();
        sendEventRequest();

        if (!eventDateTo || !eventDateFrom) {
          $(".datepicker-btn").html("DATE");
        }

        from = (datePickerFromDate.getMonth() + 1) + '/' + datePickerFromDate.getDate() + '/' + datePickerFromDate.getFullYear();
        from = '<span class="from accent-color">' + from + '</span>';
        to = (datePickerToDate.getMonth() + 1) + '/' + datePickerToDate.getDate() + '/' + datePickerToDate.getFullYear();
        to = '<span class="to accent-color">' + to + '</span>';

        $(".datepicker-btn").html("From " + from + " to " + to);
    });
    
    $(".datepicker-reset").click(function () {
        $('#search-date-picker-from input').val("").datepicker("update");
        $('#search-date-picker-to input').val("").datepicker("update");
        datePickerFromDate = defaultFromDate;
        datePickerToDate = defaultToDate;
        $("#search-date-picker-from input").click();
        $("#search-date-picker-from input").focus();
    });


    var $datePickerFromRefine = $('#search-date-picker-from-refine input');
    $datePickerFromRefine.datepicker({
        format: 'mm/dd/yyyy',
        autoclose: true,
        container: '#search-date-picker-from-refine',
        showOnFocus: false,
        startDate: new Date()
    }).datepicker('setDate', 'now');

    $datePickerFromRefine.on('changeDate', function (newDate) {
        eventDateFrom = newDate.date;
        //$('#events-filter').val('oldest');
        //$("[value='oldest']").click();
        $("#search-date-picker-to-refine input").click();
        $("#search-date-picker-to-refine input").focus();
    });

    $datePickerFromRefine.on('click', function () {
        var dropdown = $('#search-date-picker .dropdown-menu');
        if (dropdown[0] && dropdown[0].style.display === 'block') {
            $datePickerFromRefine.datepicker('hide');
        } else {
            $datePickerFromRefine.datepicker('show');
        }

    });

    //////////////////////

    var $datePickerToRefine = $('#search-date-picker-to-refine input');
    $datePickerToRefine.datepicker({
        format: 'mm/dd/yyyy',
        autoclose: false,
        container: '#search-date-picker-to-refine',
        showOnFocus: false,
        startDate: new Date()
    });

    $datePickerToRefine.on('changeDate', function (newDate) {
        eventDateTo = newDate.date;

        from = (eventDateFrom.getMonth() + 1) + '/' + eventDateFrom.getDate() + '/' + eventDateFrom.getFullYear();
        from = '<span class="from accent-color">' + from + '</span>';
        to = (eventDateTo.getMonth() + 1) + '/' + eventDateTo.getDate() + '/' + eventDateTo.getFullYear();
        to = '<span class="to accent-color">' + to + '</span>';

        $(".datepicker-btn").html("From " + from + " to " + to);
    });

    $datePickerToRefine.on('click', function () {
        var dropdown = $('#search-date-picker .dropdown-menu');
        if (dropdown[0] && dropdown[0].style.display === 'block') {
            $datePickerToRefine.datepicker('hide');
        } else {
            $datePickerToRefine.datepicker('show');
        }

    });

    $(".refine").click(function () {
        $(".refine-overlay").show();
    });

    $(".closebtn").click(function () {
        $(".refine-overlay").hide();
    });

    $(".refine-apply").click(function () {
        apply = true;
        eventPageNum = 1;
        $(".refine-overlay").hide();
        sendEventRequest();
    });


    $(".reset-all").click(function () {
        $('#search-date-picker-from-refine input').val("").datepicker("update");
        $('#search-date-picker-to-refine input').val("").datepicker("update");
        eventDateFrom = eventDateTo = null;
    });

    /////////////////////

    var $datePickerCalendar = $('#search-date-picker-calendar input');
    $datePickerCalendar.datepicker({
        format: 'mm/dd/yyyy',
        autoclose: true,
        container: '#search-date-picker-calendar',
        showOnFocus: false,
        startDate: defaultFromDate,
        endDate: defaultToDate
    });

    if (setFromDate) {
      $datePickerCalendar.datepicker('setDate', defaultFromDate);
      datePickerFromDate = new Date(defaultFromDate);
    }

    $datePickerCalendar.on('changeDate', function (newDate) {
        datePickerFromDate = newDate.date;
        if (!datePickerToDate || datePickerFromDate > datePickerToDate) {
           datePickerToDate = datePickerFromDate;
           $datePickerTo.datepicker('setDate', datePickerToDate);
        }
        apply = true;
        eventDateFrom = datePickerFromDate
        eventDateTo = null
        eventPageNum = 1;
        $("#calendar-date-range .title2").html( eventDateFrom.toLocaleDateString() + " - " );
        $(".datepicker-container").hide();
        sendEventRequest();
    });

    $datePickerCalendar.on('click', function () {
        var dropdown = $('#search-date-picker-calendar .dropdown-menu');
        if (dropdown[0] && dropdown[0].style.display === 'block') {
            $datePickerCalendar.datepicker('hide');
        } else {
            $datePickerCalendar.datepicker('show');
        }

    });

    //////////////////////
    

});
