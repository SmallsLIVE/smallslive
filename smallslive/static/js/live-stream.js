/*
Periodically checks if the time is after the current event end time and either switches it for the next event
 or shows a message that nothing is streaming now.
 */

var LiveStream = (function() {
    var CHECK_INTERVAL = 60; // in seconds
    var start;
    var end;
    var intervalId;
    var checkIfEnded = function() {
        var now = new Date();
        if (now > end) {
            var $currentEvent= $(".live-stream-current");
            var $nextEvent = $(".mini-event").first();
            if($nextEvent.length) {
                end = new Date($nextEvent.attr("data-end-time"));
                var $nextEventHtml = $($nextEvent.find('.mini-event-info').html().replace(/mini-event-info/gi, "live-stream-current"));
                $nextEvent.remove();
                $currentEvent.html($nextEventHtml);
                $(".live-stream-current__date").before($('.live-stream-current__title'));
            } else {
                noEventStreaming();
                clearInterval(intervalId);
            }
        }
    };
    var noEventStreaming = function() {
        $(".live-stream__title").hide();
        $(".live-stream__title--no-show").show();
        $(".coming-up__no-events").show();
        $(".live-stream-info").remove();
    };
    var init = function(currentEventStart, currentEventEnd) {
        $(".coming-up__no-events").hide();
        var now = new Date();
        start = new Date(currentEventStart);
        if (currentEventEnd !== "" && now > start) {
            end = new Date(currentEventEnd);
            intervalId = window.setInterval(checkIfEnded, CHECK_INTERVAL * 1000);
        } else {
            noEventStreaming();
        }
    };
    return {
        init: init
    };
})();
