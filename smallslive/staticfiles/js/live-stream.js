/*
Periodically checks if the time is after the current event end time and either switches it for the next event
 or shows a message that nothing is streaming now.
 */

var LiveStream = (function() {
    var CHECK_INTERVAL = 10; // in seconds
    var nextStart;
    var currentEnd;
    var intervalId;
    var checkIfEnded = function() {
        var now = new Date();
        var $currentEvent= $(".live-stream-current");
        if (nextStart !== false && now > nextStart) {
            var $nextEvent = $(".mini-event").first();
            if($nextEvent.length) {
                currentEnd = new Date($nextEvent.attr("data-end-time"));
                var $nextEventHtml = $($nextEvent.find('.mini-event-info').html().replace(/mini-event-info/gi, "live-stream-current"));
                $nextEvent.remove();
                $currentEvent.html($nextEventHtml);
                $(".live-stream-current__date").before($('.live-stream-current__title'));
                if($(".mini-event").length === 0) {
                    $('.events').html('<p class="coming-up__no-events">No upcoming events for today.</p>');
                }
            } else {
                noEventStreaming();
                clearInterval(intervalId);
            }
        } else if (currentEnd !== false && now > currentEnd) {
            $currentEvent.html('<p>A break between two events is happening right now.</p>');
            currentEnd = false;
        }
    };
    var noEventStreaming = function() {
        $(".live-stream__title").addClass('live-stream__title--no-show').removeClass('live-stream__title');
        $(".live-stream-current").html('<p>No event is happening right now.</p>');
        $('.events').html('<p class="coming-up__no-events">No upcoming events for today.</p>');
    };
    var init = function(currentEventEnd, nextEventStart) {
        var now = new Date();
        if (currentEventEnd !== false) {
            currentEnd = new Date(currentEventEnd);
        }
        if (nextEventStart !== false) {
            nextStart = new Date(nextEventStart);
        }
        intervalId = window.setInterval(checkIfEnded, CHECK_INTERVAL * 1000);
    };
    return {
        init: init
    };
})();
