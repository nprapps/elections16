// Global jQuery references
var $window = null;
var $body = null;
var $cardsWrapper = null;
var $titlecard = null;
var $audioPlayer = null;
var $playToggleBtn = null;
var $globalHeader = null;
var $globalNav = null;
var $globalControls = null;
var $rewindBtn = null;
var $forwardBtn = null;
var $duration = null;
var $begin = null;
var $newsletterContainer = null;
var $newsletterForm = null;
var $newsletterInput = null;
var $mute = null;
var $flickityNav = null;
var $subscribeBtn = null
var $supportBtn = null;
var $linkRoundupLinks = null;
var $alert = null;
var $alertAction = null;
var $closeAlert = null;

// Global references
var candidates = {}
var isTouch = Modernizr.touch;
var currentState = null;
var rem = null;
var dragDirection = null;
var LIVE_AUDIO_URL = 'http://nprdmp-live01-mp3.akacast.akamaistream.net/7/998/364916/v1/npr.akacast.akamaistream.net/nprdmp_live01_mp3'
var playedAudio = false;
var globalStartTime = null;
var slideStartTime = null;
var timeOnSlides = {};
var currentCard = null;

var focusWorkaround = false;
if (/(android)/i.test(navigator.userAgent) || navigator.userAgent.match(/OS 5(_\d)+ like Mac OS X/i)) {
   focusWorkaround = true;
}

/*
 * Run on page load.
 */
var onDocumentLoad = function(e) {
    $window = $(window);
    $body = $('body');
    $cardsWrapper = $('.cards');
    $cards = $('.card');
    $titlecard = $('.card').eq(0);
    $audioPlayer = $('.audio-player');
    $playToggleBtn = $('.toggle-btn');
    $rewindBtn = $('.rewind');
    $forwardBtn = $('.forward');
    $globalNav = $('.global-nav');
    $globalHeader = $('.global-header');
    $globalControls = $('.global-controls');
    $duringModeNotice = $('.during-mode-notice');
    $duration = $('.duration');
    $begin = $('.begin');
    $newsletterContainer = $('#newsletter');
    $newsletterForm = $newsletterContainer.find('form');
    $newsletterInput = $newsletterContainer.find('input');
    $mute = $('.mute-button');
    $subscribeBtn = $('.btn-subscribe');
    $supportBtn = $('.donate-link a');
    $linkRoundupLinks = $('.link-roundup a');
    $alert = $('.alert');
    $alertAction = $('.alert-action');
    $closeAlert = $('.close-alert');

    rem = getEmPixels();

    $body.on('click', '.begin', onBeginClick);
    $body.on('click', '.link-roundup a', onLinkRoundupLinkClick);
    $playToggleBtn.on('click', AUDIO.toggleAudio);
    $mute.on('click', AUDIO.toggleAudio);
    $rewindBtn.on('click', AUDIO.rewindAudio);
    $forwardBtn.on('click', AUDIO.forwardAudio);
    $newsletterForm.on('submit', onNewsletterSubmit);
    $supportBtn.on('click', onSupportBtnClick);
    $closeAlert.on('click', onCloseAlertClick);

    $window.resize(onResize);
    $window.on('beforeunload', onUnload);

    setupFlickity();
    setPolls();
    AUDIO.setupAudio();

    $cardsWrapper.css({
        'opacity': 1,
        'visibility': 'visible'
    });

    if (window.navigator.standalone) {
        ANALYTICS.trackEvent('launched-from-homescreen', currentState);
    }
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

    globalStartTime = new Date();
    slideStartTime = new Date();
    currentCard = 0;

    for (var i = 0; i < $cards.length; i++) {
        var id = $cards.eq(i).attr('id');
        timeOnSlides[id] = 0;
        detectMobileBg($cards.eq(i));
    }

    $flickityNav = $('.flickity-prev-next-button');

    // bind events that must be bound after flickity init
    $cardsWrapper.on('cellSelect', onCardChange);
    $cardsWrapper.on('settle', onCardSettle);
    $cardsWrapper.on('dragStart', onDragStart);
    $cardsWrapper.on('dragMove', onDragMove);
    $cardsWrapper.on('dragEnd', onDragEnd);
    $cardsWrapper.on('keydown', onKeydown);

    if (isTouch) {
        $flickityNav.on('touchend', onFlickityNavClick);
    } else {
        $flickityNav.on('click', onFlickityNavClick);
    }
    // set height on titlecard if necessary
    var $thisCard = $('.is-selected');
    var cardHeight = $thisCard.find('.card-inner').height() + (6 * rem);
    checkOverflow(cardHeight, $thisCard);
}

var detectMobileBg = function($card) {
    var $cardBackground = $card.find('.card-background');

    if ($cardBackground.data('mobile-bg') && $(window).width() <= 768) {
        var bgURL = $cardBackground.data('mobile-bg');
        $cardBackground.css('background-image', 'url("' + bgURL + '")');
    } else {
        var bgURL = $cardBackground.data('default-bg');
        $cardBackground.css('background-image', 'url("' + bgURL + '")');
    }
}


var onCardChange = function(e) {
    var flickity = $cardsWrapper.data('flickity');
    var newCardIndex = flickity.selectedIndex;

    var $thisCard = $('.is-selected');
    var cardHeight = $thisCard.find('.card-inner').height() + (6 * rem);
    checkOverflow(cardHeight, $thisCard);

    $globalHeader.removeClass('bg-header');

    if (newCardIndex > 0) {
        $globalNav.addClass("show-nav");
        $duringModeNotice.show();
        $flickityNav.show();
        if (currentState == 'during' && !playedAudio) {
            AUDIO.setMedia(LIVE_AUDIO_URL);
            playedAudio = true;
        }
    } else {
        $globalNav.removeClass("show-nav");
        $duringModeNotice.hide();
        $flickityNav.hide();
    }

    if ($thisCard.is('#podcast') && !playedAudio) {
        // PODCAST_URL is defined in the podcast template
        AUDIO.setMedia(PODCAST_URL);
        playedAudio = true;
    }
}

var checkOverflow = function(cardHeight, $slide) {
    if (cardHeight > $(window).height()) {
        $slide.find('.card-background').height(cardHeight + (6 * rem));
    } else {
        $slide.find('.card-background').height('100%');
    }
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

    if (currentCard === newCardIndex) {
        return;
    }

    if (dragDirection === 'previous') {
        var exitedCardID = $cards.eq(newCardIndex + 1).attr('id');
        ANALYTICS.trackEvent('card-swipe-previous', exitedCardID);
    } else if (dragDirection === 'next') {
        var exitedCardID = $cards.eq(newCardIndex - 1).attr('id');
        ANALYTICS.trackEvent('card-swipe-next', exitedCardID);
    }
    logCardExit(exitedCardID);
}

var onKeydown = function(e) {
    var flickity = $cardsWrapper.data('flickity');
    var newCardIndex = flickity.selectedIndex;

    if (currentCard === newCardIndex) {
        return;
    }

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

    logCardExit(exitedCardID);
}

var onFlickityNavClick = function(e) {
    if ($(this).attr('disabled')) {
        return;
    }

    var flickity = $cardsWrapper.data('flickity');
    var newCardIndex = flickity.selectedIndex;

    if ($(this).hasClass('previous')) {
        var exitedCardID = $cards.eq(newCardIndex + 1).attr('id');
        ANALYTICS.trackEvent('nav-click-previous', exitedCardID);
    } else if ($(this).hasClass('next')) {
        var exitedCardID = $cards.eq(newCardIndex - 1).attr('id');
        ANALYTICS.trackEvent('nav-click-next', exitedCardID);
    }
    logCardExit(exitedCardID);
}

var onCardSettle = function() {
    var flickity = $cardsWrapper.data('flickity');
    currentCard = flickity.selectedIndex;

    /*
     * Workaround for bouncing kbd tray on some mobile webkit browsers (iphone 5, nexus 6).
     *
     * Attaches a focus handler that forces focus back on redraws triggered by keyboard
     * after other commands have executed. It should only fire once to avoid recursion.
     */
    if (focusWorkaround && $(flickity.selectedElement).is($newsletterContainer)) {
        $newsletterInput.one('focus', function() {
            setTimeout(function() {
                $newsletterInput.focus();
            }, 100);
        });
    }
}

var onBeginClick = function(e) {
    $cardsWrapper.flickity('next');
    ANALYTICS.trackEvent('begin-btn-click', currentState);
    logCardExit('title');
}

var logCardExit = function(id) {
    var timeBucket = calculateTimeBucket(slideStartTime)[0];
    var timeValue = calculateSlideExitTime(id);
    ANALYTICS.trackEvent('card-exit', id, timeBucket, timeValue);
}

var calculateSlideExitTime = function(id) {
    var currentTime = new Date();
    var timeOnSlide = Math.abs(currentTime - slideStartTime);
    timeOnSlides[id] += timeOnSlide;
    slideStartTime = new Date();
    return timeOnSlide;
}

var calculateTimeBucket = function(startTime) {
    var currentTime = new Date();
    var totalTime = Math.abs(currentTime - startTime);
    var seconds = Math.floor(totalTime/1000);
    var timeBucket = getTimeBucket(seconds);

    return [timeBucket, totalTime];
}

var getTimeBucket = function(seconds) {
    if (seconds < 60) {
        var tensOfSeconds = Math.floor(seconds / 10) * 10;
        var timeBucket = tensOfSeconds.toString() + 's';
    } else if (seconds >=60 && seconds < 300) {
        var minutes = Math.floor(seconds / 60);
        var timeBucket = minutes.toString() + 'm';
    } else {
        var minutes = Math.floor(seconds / 60);
        var fivesOfMinutes = Math.floor(minutes / 5) * 5;
        var timeBucket = fivesOfMinutes.toString() + 'm';
    }

    return timeBucket
}

var onUnload = function(e) {
    // log final slide time
    var currentSlideId = $('.is-selected').attr('id');
    calculateSlideExitTime(currentSlideId);

    // log all slide total time buckets and time values
    for (slide in timeOnSlides) {
        if (timeOnSlides.hasOwnProperty(slide)) {
            if (timeOnSlides[slide] > 0) {
                var timeBucket = getTimeBucket(timeOnSlides[slide] / 1000);
                ANALYTICS.trackEvent('total-time-on-slide', slide, timeBucket, timeOnSlides[slide]);
            }
        }
    }
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
                    var $cardBackground = $(data).find('.card-background');

                    var htmlString = $cardInner.prop('outerHTML');
                    if ($cardBackground.length > 0) {
                        htmlString += $cardBackground.prop('outerHTML');
                    }

                    $card.html(htmlString);
                    detectMobileBg($card);
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
                var oldState = currentState;
                currentState = data['state']
                if (!oldState && currentState === 'during') {
                    AUDIO.setLive();
                }

                if (oldState === 'before' && currentState === 'during') {
                    setLiveAlert();
                }
            }
        }
    });
}

var setLiveAlert = function() {
    $alert.removeClass().addClass('alert signal-during');
    $alertAction.off('click');
    $alertAction.on('click', function() {
        location.reload(true);
    });
}

var onCloseAlertClick = function() {
    $alert.addClass('alert-slide-up')
}

var onResize = function() {
    $cardsWrapper.height($(window).height());
    $cardsWrapper.flickity('resize');

    var $thisCard = $cards.filter('.is-selected');
    var cardHeight = $thisCard.find('.card-inner').height();
    checkOverflow(cardHeight, $thisCard);

    for (var i = 0; i < $cards.length; i++) {
        detectMobileBg($cards.eq(i));
    }
}


var onSupportBtnClick = function(e) {
    var timesToClick = calculateTimeBucket(globalStartTime);
    ANALYTICS.trackEvent('support-btn-click', currentState, timesToClick[0], timesToClick[1]);
}

var onLinkRoundupLinkClick = function() {
    var href = $(this).attr('href');
    var timesToClick = calculateTimeBucket(globalStartTime);
    ANALYTICS.trackEvent('link-roundup-click', href, timesToClick[0], timesToClick[1]);
}

/*
* STUB TEST COMMANDS
*/

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

var onNewsletterSubmit = function(e) {
    e.preventDefault();

    var $el = $(this);
    var email = $el.find('#newsletter-email').val();

    var clearStatusMessage = function() {
        var statusMsgExists = $el.find('.message').length;
        if (statusMsgExists > 0) {
            $el.find('.message').remove();
        }
    }

    if (!email) {
        return;
    }

    var timesToClick = calculateTimeBucket(globalStartTime);
    ANALYTICS.trackEvent('newsletter-subscribe', currentState, timesToClick[0], timesToClick[1]);

    // wait state
    clearStatusMessage();
    var waitMsg = '<div class="message wait">'
    waitMsg += '<p><i class="fa fa-spinner fa-spin"></i>&nbsp;' + COPY.newsletter.waiting_text + '</p>';
    waitMsg += '</div>'
    $el.append(waitMsg);
    $subscribeBtn.hide();

    $.ajax({
        url: APP_CONFIG.NEWSLETTER_POST_URL,
        timeout: APP_CONFIG.NEWSLETTER_POST_TIMEOUT,
        method: 'POST',
        data: {
            email: email,
            orgId: 0,
            isAuthenticated: false
        },
        success: function(response) { // success
            var successMsg = '<div class="message success">'
            successMsg += '<h3>' + COPY.newsletter.success_headline + '</h3>';
            successMsg += '<p>' + COPY.newsletter.success_text + ' ' + email + '.</p>';
            successMsg += '</div>'
            clearStatusMessage();
            $el.html(successMsg);
            ANALYTICS.trackEvent('newsletter-signup-success', currentState);
        },
        error: function(response) { // error
            var errorMsg = '<div class="message error">';
            errorMsg += '<h3>' + COPY.newsletter.error_headline + '</h3>';
            errorMsg += '<p>' + COPY.newsletter.error_text + '</p>';
            errorMsg += '</div>'
            clearStatusMessage();
            $el.append(errorMsg);
            $subscribeBtn.show();
            ANALYTICS.trackEvent('newsletter-signup-error', currentState);
        }
    });
}
$(onDocumentLoad);
