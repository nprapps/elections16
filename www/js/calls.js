var $acceptAP;
var $rejectAP;
var $callNPR;
var $uncallNPR;

var ACCEPT_AP_URL = document.location.href + 'accept-ap';
var CALL_NPR_URL = document.location.href + 'call-npr'

var onDocumentLoad = function() {
    $acceptAP = $('.accept-ap');
    $rejectAP = $('.reject-ap')
    $callNPR = $('.call-npr');
    $uncallNPR = $('.uncall-npr');

    $acceptAP.on('click', onAPClick);;
    $rejectAP.on('click', onAPClick);
    $callNPR.on('click', onCallNPRClick);
    $uncallNPR.on('click', onUncallNPRClick);
}

var onAPClick = function(e) {
    var data = {
        race_id: $(this).data('race-id')
    }
    var $parent = $(this).parent();

    $.post(ACCEPT_AP_URL, data, function() {
        console.log($parent);
        var $btns = $parent.find('.ap');
        console.log($btns);
        $btns.toggleClass('hidden');
    });
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