var $acceptAP;
var $rejectAP;
var $callNPR;
var $uncallNPR;
var $overlay;
var $body;

var ACCEPT_AP_URL = document.location.href + 'accept-ap';
var CALL_NPR_URL = document.location.href + 'call-npr'

var pageRefresh = null;

var onDocumentLoad = function() {
    $acceptAP = $('.accept-ap');
    $rejectAP = $('.reject-ap')
    $callNPR = $('.npr-call');
    $uncallNPR = $('.npr-uncall');
    $overlay = $('.overlay');
    $body = $('body');

    $acceptAP.on('click', onAPClick);
    $rejectAP.on('click', onAPClick);
    $callNPR.on('click', onCallNPRClick);
    $uncallNPR.on('click', onUncallNPRClick);

    pageRefresh = setInterval(refreshPage, 10000);
}

var onAPClick = function(e) {
    var data = {
        race_id: $(this).data('race-id')
    }

    $overlay.fadeIn();
    $.post(ACCEPT_AP_URL, data,function() {
        refreshPage(true);
    });
}

var onCallNPRClick = function(e) {
    var data = {
        race_id: $(this).data('race-id'),
        result_id: $(this).data('result-id')
    }

    $overlay.fadeIn();
    $.post(CALL_NPR_URL, data, function() {
        refreshPage(true);
    });
}

var onUncallNPRClick = function(e) {
    var data = {
        race_id: $(this).data('race-id'),
        result_id: $(this).data('result-id')
    }

    $overlay.fadeIn();
    $.post(CALL_NPR_URL, data, function() {
        refreshPage(true);
    });
}

var refreshPage = function() {
    $.get(window.location.href, function(data) {
        var $oldContainer = $('.container');
        var $newHTML = $(data);
        var $newContainer = $newHTML.filter('.container');
        $oldContainer.html($newContainer);

        $acceptAP.off('click');
        $rejectAP.off('click');
        $callNPR.off('click');
        $uncallNPR.off('click');
        clearInterval(pageRefresh);

        onDocumentLoad();

        $overlay.fadeOut();
    });
}

$(onDocumentLoad);
