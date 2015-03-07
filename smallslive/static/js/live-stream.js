var LiveStream = (function() {
    var checkIfEnded = function() {
        console.log("dinamo");
        if (2>1) {
            var $currentEvent= $(".live-stream-current");
            var $nextEventHtml = $(".mini-event-info").first().html().replace(/mini-event-info/gi, "live-stream-current");
            $currentEvent.html($nextEventHtml);
        }
    };
    var init = function(currentEventEnd) {
        this.end = currentEventEnd;
        //window.setInterval(checkIfEnded, 1000);
        checkIfEnded();
    };
    return {
        init: init
    }
})();

LiveStream.init("test");
