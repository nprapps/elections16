// Global jQuery references
var $cards = null;
var $titlecard = null;
var $audioPlayer = null;
var $playToggleBtn = null;
var $rewindBtn = null;
var $forwardBtn = null;
var $duration = null;
var $begin = null;

// Global references
var candidates = {}
var isTouch = Modernizr.touch;

/*
 * Run on page load.
 */
var onDocumentLoad = function(e) {
    $cards = $('.cards');
    $titlecard = $('.card').eq(0);
    $audioPlayer = $('.audio-player');
    $playToggleBtn = $('.toggle-btn');
    $rewindBtn = $('.rewind');
    $forwardBtn = $('.forward');
    $duration = $('.duration');
    $begin = $('.begin');

    $playToggleBtn.on('click', AUDIO.toggleAudio);
    $rewindBtn.on('click', AUDIO.rewindAudio);
    $forwardBtn.on('click', AUDIO.forwardAudio);
    $begin.on('click', onBeginClick);

    setupFlickity();
    AUDIO.setupAudio();

    $cards.css({
        'opacity': 1,
        'visibility': 'visible'
    });
}

var setupFlickity = function() {
    $cards.height($(window).height());

    $cards.flickity({
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

    if ($('.is-selected').is('#podcast') && $audioPlayer.data().jPlayer.status.currentTime === 0) {
        AUDIO.setMedia(PODCAST_URL);
    }
}

var onCardAnimationFinish = function(e) {
    var flickity = $cards.data('flickity');
    var newSlideIndex = flickity.selectedIndex;

    if (newSlideIndex > 0) {
        $('.global-header').addClass('bg-header');
    }
}

var onBeginClick = function(e) {
    $cards.flickity('next');
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
