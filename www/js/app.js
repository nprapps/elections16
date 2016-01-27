// Global jQuery references
var $cardsWrapper = null;
var $titlecard = null;
var $audioPlayer = null;
var $playToggleBtn = null;
var $globalHeader = null;
var $globalControls = null;
var $rewindBtn = null;
var $forwardBtn = null;
var $duration = null;
var $begin = null;
var $mute = null;
var $flickityNav = null;

// Global references
var candidates = {}
var isTouch = Modernizr.touch;
var currentState = null;
var rem = null;
var dragDirection = null;
var LIVE_AUDIO_URL = 'http://nprdmp-live01-mp3.akacast.akamaistream.net/7/998/364916/v1/npr.akacast.akamaistream.net/nprdmp_live01_mp3'

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
    $globalHeader = $('.global-header');
    $globalControls = $('.global-controls');
    $duringModeNotice = $('.during-mode-notice');
    $duration = $('.duration');
    $begin = $('.begin');
    $mute = $('.mute-button');

    rem = getEmPixels();

    $begin.on('click', onBeginClick);
    $playToggleBtn.on('click', AUDIO.toggleAudio);
    $mute.on('click', AUDIO.toggleAudio);
    $rewindBtn.on('click', AUDIO.rewindAudio);
    $forwardBtn.on('click', AUDIO.forwardAudio);
    $(window).resize(onResize);

    setupFlickity();
    setPolls();
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

    $flickityNav = $('.flickity-prev-next-button');

    // bind events that must be bound after flickity init
    $cardsWrapper.on('cellSelect', onCardChange);
    $cardsWrapper.on('dragStart', onDragStart);
    $cardsWrapper.on('dragMove', onDragMove);
    $cardsWrapper.on('dragEnd', onDragEnd);
    $cardsWrapper.on('keydown', onKeydown);
    $flickityNav.on('click', onFlickityNavClick);

    // set height on titlecard if necessary
    var $thisCard = $('.is-selected');
    var cardHeight = $thisCard.find('.card-inner').height();
    checkOverflow(cardHeight, $thisCard);
}

var onCardChange = function(e) {
    var flickity = $cardsWrapper.data('flickity');
    var newCardIndex = flickity.selectedIndex;

    var $thisCard = $('.is-selected');
    var cardHeight = $thisCard.find('.card-inner').height();

    checkOverflow(cardHeight, $thisCard);

    $globalHeader.removeClass('bg-header');

    if (newCardIndex > 0) {
        $globalControls.show();
        $globalHeader.show();
        $duringModeNotice.show();
        $flickityNav.show();
        if (currentState == 'during' && $audioPlayer.data().jPlayer.status.currentTime === 0) {
            AUDIO.setMedia(LIVE_AUDIO_URL);
        }
    } else {
        $globalControls.hide();
        $globalHeader.hide();
        $duringModeNotice.hide();
        $flickityNav.hide();
    }

    if ($thisCard.is('#podcast') && $audioPlayer.data().jPlayer.status.currentTime === 0) {
        // PODCAST_URL is defined in the podcast template
        AUDIO.setMedia(PODCAST_URL);
    }

    ANALYTICS.trackEvent('card-enter', $thisCard.attr('id'));
}

var onDragStart = function(e, pointer) {
    dragDirection = null;
}

var onDragMove = function(e, pointer, moveVector) {
    if (moveVector.x > 0) {
        dragDirection = 'previous';
    } else {
        dragDirection = 'next';
    }
}

var onDragEnd = function(e, pointer) {
    var flickity = $cardsWrapper.data('flickity');
    var newCardIndex = flickity.selectedIndex;

    if (dragDirection === 'previous') {
        var exitedCardID = $cards.eq(newCardIndex + 1).attr('id');
        ANALYTICS.trackEvent('card-swipe-previous', exitedCardID);
    } else if (dragDirection === 'next') {
        var exitedCardID = $cards.eq(newCardIndex - 1).attr('id');
        ANALYTICS.trackEvent('card-swipe-next', exitedCardID);
    }

    ANALYTICS.trackEvent('card-exit', exitedCardID);
}

var onKeydown = function(e) {
    var flickity = $cardsWrapper.data('flickity');
    var newCardIndex = flickity.selectedIndex;

    if (e.which === 37) {
        var keyDirection = 'previous';
    } else if (e.which === 39) {
        var keyDirection = 'next';
    } else {
        return;
    }

    if (e.target !== $cardsWrapper[0]) {
        ANALYTICS.trackEvent('keyboard-nav-wrong-target')
    } else {
        if (keyDirection === 'previous') {
            var exitedCardID = $cards.eq(newCardIndex + 1).attr('id');
            ANALYTICS.trackEvent('keyboard-nav-previous', exitedCardID);
        } else if (keyDirection === 'next') {
            var exitedCardID = $cards.eq(newCardIndex - 1).attr('id');
            ANALYTICS.trackEvent('keyboard-nav-next', exitedCardID);
        }
    }

    ANALYTICS.trackEvent('card-exit', exitedCardID);
}

var onFlickityNavClick = function(e) {
    var flickity = $cardsWrapper.data('flickity');
    var newCardIndex = flickity.selectedIndex;

    if ($(this).hasClass('previous')) {
        var exitedCardID = $cards.eq(newCardIndex + 1).attr('id');
        ANALYTICS.trackEvent('nav-click-previous', exitedCardID);
    } else if ($(this).hasClass('next')) {
        var exitedCardID = $cards.eq(newCardIndex - 1).attr('id');
        ANALYTICS.trackEvent('nav-click-next', exitedCardID);
    }

    ANALYTICS.trackEvent('card-exit', exitedCardID);
}

var checkOverflow = function(cardHeight, $slide) {
    if (cardHeight > $(window).height()) {
        $slide.find('.card-background').height(cardHeight + (6 * rem));
    } else {
        $slide.find('.card-background').height('100%');
    }
}

var onBeginClick = function(e) {
    $cardsWrapper.flickity('next');
    ANALYTICS.trackEvent('begin-btn-click');
    ANALYTICS.trackEvent('card-exit', 'title');
}

var setPolls = function() {
    // set poll for cards
    for (var i = 0; i < $cards.length; i++) {
        var $thisCard = $cards.eq(i);
        var refreshRoute = $thisCard.data('refresh-route');
        var refreshRate = $thisCard.data('refresh-rate');

        if (refreshRoute && refreshRate > 0) {
            var fullURL = APP_CONFIG.S3_BASE_URL + refreshRoute;
            var fullRefreshRate = refreshRate * 1000;

            var cardGetter = _.partial(getCard, fullURL, $thisCard, i);
            setInterval(cardGetter, fullRefreshRate)
        }
    }

    // set poll for state
    checkState();
    setInterval(checkState, 60000)
}

var getCard = function(url, $card, i) {
    setTimeout(function() {
        $.ajax({
            url: url,
            ifModified: true,
            success: function(data, status) {
                if (status === 'success') {
                    var $cardInner = $(data).find('.card-inner');
                    $card.html($cardInner);
                }
            }
        });
    }, i * 1000);
}

var checkState = function() {
    $.ajax({
        url: APP_CONFIG.S3_BASE_URL + '/current-state.json',
        dataType: 'json',
        ifModified: true,
        success: function(data, status) {
            if (status === 'success' && data['state'] !== currentState) {
                currentState = data['state']
                if (currentState === 'during') {
                    AUDIO.setLive();
                }
            }
        }
    });
}

var onResize = function() {
    $cardsWrapper.height($(window).height());
    $cardsWrapper.flickity('resize');

    var $thisCard = $cards.filter('.is-selected');
    var cardHeight = $thisCard.find('.card-inner').height();
    checkOverflow(cardHeight, $thisCard);
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
