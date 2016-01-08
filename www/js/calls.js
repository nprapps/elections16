var $callAP;
var $callNPR;
var $uncallNPR;

var ACCEPT_AP_URL = document.location.href + 'accept-ap';
var CALL_NPR_URL = document.location.href + 'call-npr'

var onDocumentLoad = function() {
    $acceptAP = $('.accept-ap');
    $callNPR = $('.call-npr');
    $uncallNPR = $('.uncall-npr');

    $acceptAP.on('click', onAcceptAPClick);
    $callNPR.on('click', onCallNPRClick);
    $uncallNPR.on('click', onUncallNPRClick);
}

var onAcceptAPClick = function(e) {
    var data = {
        race_id: $(this).data('race-id')
    }

    $.post(ACCEPT_AP_URL, data);
}

var onCallNPRClick = function(e) {
    var data = {
        race_id: $(this).data('race-id'),
        candidate_id: $(this).data('candidate-id')
    }

    $.post(CALL_NPR_URL, data);
}

var onUncallNPRClick = function(e) {
    var data = {
        race_id: $(this).data('race-id'),
        candidate_id: $(this).data('candidate-id')
    }

    $.post(CALL_NPR_URL, data);
}

$(onDocumentLoad);