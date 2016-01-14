// Global jQuery references
var $cards = null;
var $titlecard = null;

// Global references
var candidates = {}
var isTouch = Modernizr.touch;

/*
 * Run on page load.
 */
var onDocumentLoad = function(e) {
    $cards = $('.cards');
    $titlecard = $('.card').eq(0);

    setupFlickity();
}

var setupFlickity = function() {
    $cards.height($(window).height());


    // make it harder to start the card transition so we can

    Flickity.prototype.hasDragStarted = function( moveVector ) {
      return !this.isTouchScrolling && Math.abs( moveVector.x ) > 10;
    };

    $cards.flickity({
        cellSelector: '.card',
        cellAlign: 'center',
        draggable: isTouch,
        imagesLoaded: true,
        pageDots: false,
        friction: 0.8,
        selectedAttraction: 0.1
    });

    // bind events
    $cards.on('cellSelect', onCardChange);
    $cards.on('settle', onCardAnimationFinish);
}

var onCardChange = function(e) {
    var flickity = $cards.data('flickity');
    var oldSlideIndex = flickity.selectedIndex - 1;
    var newSlideIndex = flickity.selectedIndex;

    if (newSlideIndex > 0) {
        $('.global-controls').show();
    } else {
        $('.global-controls').hide();
        $('.global-header').removeClass('bg-header');

    }
}

var onCardAnimationFinish = function(e) {
    var flickity = $cards.data('flickity');
    var newSlideIndex = flickity.selectedIndex;

    if (newSlideIndex > 0) {
        $('.global-header').addClass('bg-header');
    }
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
