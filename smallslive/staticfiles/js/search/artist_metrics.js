var payoutsUrl = '/artist-dashboard/my-payouts';

function formattedPayout(seconds) {
    var hrs = Math.floor(seconds / 3600);
    seconds -= hrs * 3600;
    var mnts = Math.floor(seconds / 60);
    seconds -= mnts * 60;
    formattedString = hrs + " hrs " + mnts + " min " + seconds + " seconds"
    return formattedString
}

function initializeMetrics(){
    var artistSeconds = document.getElementById('artist-seconds');
    var eventsSeconds = document.getElementById('event-seconds');
    var artistSecondsValue = $(artistSeconds).data('seconds')
    var eventsSecondsValue = $(eventsSeconds).data('seconds')
    artistSeconds.innerHTML = formattedPayout(artistSecondsValue)
    eventsSeconds.innerHTML = formattedPayout(eventsSecondsValue)

}

$(document).ready(function () {
    var $payoutData = $('#payoutData');
    var $currentPayoutData = $('#currentPayoutData');
    initializeMetrics();
    $("#artist_payout_select").on('change', function () {
        var payoutId = $("#artist_payout_select").val();
        if (payoutId !== 'current') {
            $.ajax({
                url: payoutsUrl + '/' + payoutId,
                success: function (data) {
                    $payoutData.html(data);
                    $payoutData.show();
                    $currentPayoutData.hide();
                }
            })
        } else {
            $payoutData.hide();
            $currentPayoutData.show();
        }
    });
});