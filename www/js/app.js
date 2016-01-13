// Global jQuery references
var $cards = null;

// Global references
var candidates = {}
var isTouch = Modernizr.touch;

/*
 * Run on page load.
 */
var onDocumentLoad = function(e) {
    $cards = $('.cards');

    setupFlickity();
}

var setupFlickity = function() {
    $cards.height($(window).height());

    $cards.flickity({
        cellAlign: 'center',
        draggable: isTouch,
        wrapAround: true,
        imagesLoaded: true,
        pageDots: false
    })
}

var getCandidates = function() {
    $.getJSON('assets/candidates.json', function(data) {
        return data;
    });
}

var makeListOfCandidates = function(candidates) {
    var candidateList = [];
    for (var i = 0; i < candidates.length; i++) {
        var firstName = candidates[i]['first'];
        var lastName = candidates[i]['last'];

        var candidateName = firstName + ' ' + lastName;

        candidateList.push(candidateName);
    }

    return candidateList;
}

$(onDocumentLoad);
