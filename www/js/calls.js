var $acceptAP;
var $rejectAP;
var $callNPR;
var $uncallNPR;

var ACCEPT_AP_URL = document.location.href + 'accept-ap';
var CALL_NPR_URL = document.location.href + 'call-npr'

var onDocumentLoad = function() {
    $acceptAP = $('.accept-ap');
    $rejectAP = $('.reject-ap')
    $callNPR = $('.npr-call');
    $uncallNPR = $('.npr-uncall');

    $acceptAP.on('click', onAPClick);;
    $rejectAP.on('click', onAPClick);
    $callNPR.on('click', onCallNPRClick);
    $uncallNPR.on('click', onUncallNPRClick);
}

var onAPClick = function(e) {
    var data = {
        race_id: $(this).data('race-id')
    }

    $.post(ACCEPT_AP_URL, data, refreshPage);
}

var onCallNPRClick = function(e) {
    var data = {
        race_id: $(this).data('race-id'),
        result_id: $(this).data('result-id')
    }
    $.post(CALL_NPR_URL, data, refreshPage);
}

var onUncallNPRClick = function(e) {
    console.log(e);
    var data = {
        race_id: $(this).data('race-id'),
        result_id: $(this).data('result-id')
    }

    $.post(CALL_NPR_URL, data, refreshPage);
}

var refreshPage = function() {
    $.get(window.location.href, function(data) {
        $('body').html(data);
        console.log(data);
    });
}

$(onDocumentLoad);