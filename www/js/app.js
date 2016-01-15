// Global jQuery references
var $cardsWrapper = null;
var $titlecard = null;
var $audioPlayer = null;
var $playToggleBtn = null;


// Global references
var candidates = {}
var isTouch = Modernizr.touch;

/*
 * Run on page load.
 */
var onDocumentLoad = function(e) {
    $cardsWrapper = $('.cards');
    $cards = $('.card');
    $titlecard = $('.card').eq(0);
    $audioPlayer = $('.audio-player');
    $playToggleBtn = $('.toggle-btn');
    $rewindBtn = $('.rewind');
    $forwardBtn = $('.forward');

    $playToggleBtn.on('click', AUDIO.toggleAudio);
    $rewindBtn.on('click', AUDIO.rewindAudio);
    $forwardBtn.on('click', AUDIO.forwardAudio);

    setupFlickity();
    AUDIO.setupAudio();

    $cardsWrapper.css({
        'opacity': 1,
        'visibility': 'visible'
    });
}

var setupFlickity = function() {
    $cardsWrapper.height($(window).height());

    $cardsWrapper.flickity({
        cellSelector: '.card',
        cellAlign: 'center',
        draggable: isTouch,
        dragThreshold: 20,
        imagesLoaded: true,
        pageDots: false,
        setGallerySize: false,
        friction: isTouch ? 0.28 : 1,
        selectedAttraction: isTouch ? 0.025 : 1
    });

    // bind events
    $cardsWrapper.on('cellSelect', onCardChange);
    $cardsWrapper.on('settle', onCardAnimationFinish);
}

var onCardScroll = function() {
    $('.global-header').addClass('bg-header');
    $cards.off('scroll');
}

var onCardChange = function(e) {
    var flickity = $cardsWrapper.data('flickity');
    var oldSlideIndex = flickity.selectedIndex - 1;
    var newSlideIndex = flickity.selectedIndex;
    $('.global-header').removeClass('bg-header');
    $cards.on('scroll', onCardScroll);

    if ($('.is-selected').is('#podcast') && $audioPlayer.data().jPlayer.status.currentTime === 0) {
        AUDIO.setMedia(PODCAST_URL);
    }
}

var onCardAnimationFinish = function(e) {
    var flickity = $cardsWrapper.data('flickity');
    var newSlideIndex = flickity.selectedIndex;

    if (newSlideIndex > 0) {
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
