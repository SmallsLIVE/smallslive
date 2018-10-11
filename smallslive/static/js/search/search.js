var searchTerm, artistSearchTerm, artistInstrument, artistPageNum, artistMaxPageNum, eventPageNum, eventMaxPageNum, eventOrderFilter, eventFilter, eventDateFrom, eventDateTo, apply, artist_pk;

function sendArtistRequest() {
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
                $("#artists").html(data.template);
                $(".container-list-article").removeClass("artist-loading-gif");
                $("#artists").css("visibility", "visible");
                artistMaxPageNum = data.numPages;

                if (artistPageNum === 1) {
                    $(".left_arrow").addClass('artist-arrow-disabled');
                } else {
                    $(".left_arrow").removeClass('artist-arrow-disabled');
                }

                if (artistPageNum === artistMaxPageNum) {
                    $(".right_arrow").addClass('artist-arrow-disabled');
                } else {
                    $(".right_arrow").removeClass('artist-arrow-disabled');
                }
            }
        },
        error: function (data) {
            $("#artists").show();
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

function sendEventRequest() {
    var utcDateFrom = null;
    var utcDateTo = null;
    
    if (eventDateFrom) {
        utcDateFrom = eventDateFrom.getFullYear() + '/' + (eventDateFrom.getMonth() + 1) + '/' + eventDateFrom.getDate();
    }
    if (eventDateTo) {
        utcDateTo = eventDateTo.getFullYear() + '/' + (eventDateTo.getMonth() + 1) + '/' + eventDateTo.getDate();
    }

    $.ajax({
        url: '/search/ajax/event/',
        data: {
            'main_search': searchTerm,
            'page': eventPageNum,
            'order': eventOrderFilter,
            'date_from': utcDateFrom,
            'date_to': utcDateTo,
            'artist_pk': artist_pk ? artist_pk : null,
            'partial': true
        },
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
                }
                 var article = $(data.template).find('article');
                 if (!article.length) {
                     $showsContainer.html(data.template);
                 }
                 article.each(function( index ) {
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
    eventOrderFilter = "newest";
    apply = false;
    eventFilter = false;

    $("[name='q']").val(searchTerm);
    $('#artist-search').val('');

    $(".left_arrow").click(function () {
        if (artistPageNum !== 1) {

            artistPageNum -= 1;
            $(".container-list-article").addClass("artist-loading-gif");
            $("#artists").css("visibility", "hidden");
            sendArtistRequest();
        }
    });

    $(".right_arrow").click(function () {
        if (artistPageNum !== artistMaxPageNum) {
            artistPageNum += 1;
            $(".container-list-article").addClass("artist-loading-gif");
            $("#artists").css("visibility", "hidden");
            sendArtistRequest();
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

    $(".instrument").click(function () {
        artistInstrument = $(this).text();
        $('.instrument-btn').text(artistInstrument);
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
        $(".datepicker-container").css("display", "flex").hide().fadeIn(500, function() {
            $(document).bind("click", hide);
            $(".datepicker-container").data('shown', true)}); 

        $("#search-date-picker-from input").click();
        $("#search-date-picker-from input").focus();  
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
        endDate: new Date()
    });

    $datePickerFrom.on('changeDate', function (newDate) {
        eventDateFrom = newDate.date;
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

    var defaultEndDate = $('.datepicker-btn').data('default-end-date');

    var $datePickerTo = $('#search-date-picker-to input');
    $datePickerTo.datepicker({
        format: 'mm/dd/yyyy',
        autoclose: false,
        container: '#search-date-picker-to',
        showOnFocus: false,
        endDate: new Date()
    }).datepicker('setDate', defaultEndDate);

    $datePickerTo.on('changeDate', function (newDate) {
        eventDateTo = newDate.date;

        from = (eventDateFrom.getMonth() + 1) + '/' + eventDateFrom.getDate() + '/' + eventDateFrom.getFullYear();
        from = '<span class="accent-color">' + from + '</span>';
        to = (eventDateTo.getMonth() + 1) + '/' + eventDateTo.getDate() + '/' + eventDateTo.getFullYear();
        to = '<span class="accent-color">' + to + '</span>';

        $(".datepicker-btn").html("From " + from + " to " + to);
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
        apply = true;
        eventPageNum = 1;
        $(".datepicker-container").hide();
        sendEventRequest();
    });
    
    $(".datepicker-reset").click(function () {
        $('#search-date-picker-from input').val("").datepicker("update");
        $('#search-date-picker-to input').val("").datepicker("update");
        eventDateFrom = eventDateTo = null;
        $("#search-date-picker-from input").click();
        $("#search-date-picker-from input").focus();
    });
});
