// Global jQuery references
var $window = null;
var $body = null;
var $cardsWrapper = null;
var $audioPlayer = null;
var $globalHeader = null;
var $globalNav = null;
var $globalControls = null;
var $rewindBtn = null;
var $forwardBtn = null;
var $nowPlaying = null;
var $segmentType = null;
var $duration = null;
var $begin = null;
var $newsletterContainer = null;
var $newsletterForm = null;
var $newsletterButton = null;
var $newsletterInput = null;
var $mute = null;
var $flickityNav = null;
var $flickityDots = null;
var $subscribeBtn = null
var $supportBtn = null;
var $liveAlert = null;
var $liveAlertAction = null;
var $linkAlert = null;
var $linkAlertAction = null;
var $closeAlert = null;
var $donateHeadline = null;
var $donateText = null;
var $donateLink = null;

// Global references
var candidates = {}
var isTouch = Modernizr.touchevents;
var currentState = null;
var rem = null;
var dragDirection = null;
var playedAudio = false;
var globalStartTime = null;
var slideStartTime = null;
var timeOnSlides = {};
var currentCard = null;
var exitedCardID = null;
var cardExitEvent = null;
if (!LIVE) {
    var LIVE = false;
}
var testLogged = false;
var donateButtonText = null;
var resultsMultiOpen = [];
var router = null;
var deeplinked = false;
var deeplinkNotificationDismissed = false;

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
    $audioPlayer = $('.audio-player');
    $rewindBtn = $('.rewind');
    $forwardBtn = $('.forward');
    $mute = $('.mute-button');
    $nowPlaying = $('.now-playing');
    $segmentType = $('.segment-type');
    $globalNav = $('.global-nav');
    $globalHeader = $('.global-header');
    $globalControls = $('.global-controls');
    $duringModeNotice = $('.during-mode-notice');
    $duration = $('.duration');
    $begin = $('.begin');
    $newsletterContainer = $('#newsletter');
    $newsletterForm = $newsletterContainer.find('form');
    $newsletterInput = $newsletterContainer.find('input');
    $subscribeBtn = $('.btn-subscribe');
    $supportBtn = $('.donate-link a');
    $liveAlert = $('#join-alert');
    $liveAlertAction = $liveAlert.find('.alert-action');
    $linkAlert = $('#link-alert');
    $linkAlertAction = $linkAlert.find('.alert-action');
    $closeAlert = $('.close-alert');
    $donateHeadline = $('.donate-headline');
    $donateText = $('.donate-text');
    $donateLink = $('.donate-link');

    rem = getEmPixels();

    $body.on('click', '.begin', onBeginClick);
    $body.on('click', '.link-roundup a', onLinkRoundupLinkClick);
    $body.on('click', '.results-multi .state-result', onStateResultsClick);
    $body.on('click', '#live-audio .segment-play', AUDIO.toggleAudio);
    $body.on('click', '#live-audio .segment-play', closeAlert);
    $body.on('click', '#podcast .toggle-btn', AUDIO.toggleAudio);
    $body.on('click', '.audio-story .toggle-btn', AUDIO.toggleAudio);
    $mute.on('click', AUDIO.toggleAudio);
    $rewindBtn.on('click', AUDIO.rewindAudio);
    $forwardBtn.on('click', AUDIO.forwardAudio);
    $newsletterForm.on('submit', onNewsletterSubmit);
    $closeAlert.on('click', onCloseAlertClick);
    $donateLink.on('click', onDonateLinkClick);

    $window.resize(onResize);
    $window.on('beforeunload', onUnload);

    setupFlickity();

    resultsCountdown($('#results-dem'));
    resultsCountdown($('#results-gop'));
    resultsMultiToggle();

    initRouter();

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

var initRouter = function() {
    routes = {
        '/nprone': navigateToAudioCard,
        '/cards/:cardId': navigateToCard
    };
    router = Router(routes);
    router.init();
}

var setupFlickity = function() {
    $cardsWrapper.height($(window).height());

    $cardsWrapper.flickity({
        cellSelector: '.card',
        cellAlign: 'center',
        draggable: isTouch,
        dragThreshold: 20,
        imagesLoaded: true,
        pageDots: isTouch ? false : true,
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
    $flickityDots = $('.flickity-page-dots');

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
    $flickityDots.on('click', onFlickityDotsClick);

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

    if ($cardBackground.find('.photo-credit').data('mobile-credit') && $(window).width() <= 768) {
        var photoCredit = $cardBackground.find('.photo-credit').data('mobile-credit');
        $cardBackground.find('.photo-credit').text(photoCredit);
    } else {
        var photoCredit = $cardBackground.find('.photo-credit').data('default-credit');
        $cardBackground.find('.photo-credit').text(photoCredit);
    }
}

var navigateToAudioCard = function(id) {
    for (var i = 0; i < $cards.length; i++) {
        if ($cards.eq(i).hasClass('live-audio') || $cards.eq(i).hasClass('podcast')) {
            $('.toggle-btn').removeClass().addClass('toggle-btn play');
            $mute.removeClass('playing').addClass('muted');
            playedAudio = true;
            $cardsWrapper.flickity('select', i);
            ANALYTICS.trackEvent('deeplink', id);
            break;
        }
    }
    if (!APP_CONFIG.DEBUG) {
        router.setRoute('');
    }
}

var navigateToCard = function(id) {
    var $card = $('#' + id);
    var index = $cards.index($card);
    if (index > -1) {
        deeplinked = true;

        if (LIVE || $card.hasClass('live-audio') || $card.hasClass('podcast')) {
            $('.toggle-btn').removeClass().addClass('toggle-btn play');
            $mute.removeClass('playing').addClass('muted');
            playedAudio = true;
        }
        if (LIVE && !$card.hasClass('live-audio')) {
            setLinkAlert();
        }
        $cardsWrapper.flickity('select', index);
        ANALYTICS.trackEvent('deeplink', id);
    }
    if (!APP_CONFIG.DEBUG) {
        router.setRoute('');
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
        $flickityDots.show();
    } else {
        $globalNav.removeClass("show-nav");
        $duringModeNotice.hide();
        $flickityNav.hide();
        $flickityDots.hide();
        if (deeplinked && LIVE && !deeplinkNotificationDismissed) {
            closeAlert();
            playedAudio = false;
        }
    }

    if ($thisCard.is('#live-audio') && LIVE && !playedAudio) {
        AUDIO.setMedia(LIVE_AUDIO_URL);
        playedAudio = true;
    }

    if ($thisCard.is('#donate') && !testLogged) {
        startTest();
        testLogged = true;
    }
}

var checkOverflow = function(cardHeight, $slide) {
    if (cardHeight > $(window).height()) {
        $slide.find('.card-background').height(cardHeight + (6 * rem));
    } else {
        $slide.find('.card-background').height('100%');
    }
}

var startTest = function() {
    var rand = getRandomInt(0, COPY.donate_buttons.length);
    donateButtonText = COPY.donate_buttons[rand].text;
    $donateLink.find('a').text(donateButtonText);
    ANALYTICS.trackEvent('button-test', donateButtonText);
}

var getRandomInt = function(min, max) {
    return Math.floor(Math.random() * (max - min)) + min;
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
        exitedCardID = $cards.eq(newCardIndex + 1).attr('id');
        cardExitEvent = 'card-swipe-previous';
    } else if (dragDirection === 'next') {
        exitedCardID = $cards.eq(newCardIndex - 1).attr('id');
        cardExitEvent = 'card-swipe-next';
    }
    ANALYTICS.logCardExit(exitedCardID, cardExitEvent);
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
            exitedCardID = $cards.eq(newCardIndex + 1).attr('id');
            cardExitEvent = 'keyboard-nav-previous';
        } else if (keyDirection === 'next') {
            exitedCardID = $cards.eq(newCardIndex - 1).attr('id');
            cardExitEvent = 'keyboard-nav-next';
        }
    }

    ANALYTICS.logCardExit(exitedCardID, cardExitEvent);
}

var onFlickityNavClick = function(e) {
    if ($(this).attr('disabled')) {
        return;
    }

    var flickity = $cardsWrapper.data('flickity');
    var newCardIndex = flickity.selectedIndex;

    if ($(this).hasClass('previous')) {
        exitedCardID = $cards.eq(newCardIndex + 1).attr('id');
        cardExitEvent = 'nav-click-previous'
    } else if ($(this).hasClass('next')) {
        exitedCardID = $cards.eq(newCardIndex - 1).attr('id');
        cardExitEvent = 'nav-click-next';
    }

    ANALYTICS.logCardExit(exitedCardID, cardExitEvent);
}

var onFlickityDotsClick = function(e) {
    var flickity = $cardsWrapper.data('flickity');
    var newCardIndex = flickity.selectedIndex;

    if (currentCard === newCardIndex) {
        return;
    }

    var cardExitEvent = 'page-dot-nav';
    var exitedCardID = $cards.eq(currentCard).attr('id');
    ANALYTICS.logCardExit(exitedCardID, cardExitEvent);
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
    ANALYTICS.logCardExit('title');
}

var onUnload = function(e) {
    // log final slide time
    var currentSlideId = $('.is-selected').attr('id');
    ANALYTICS.calculateSlideExitTime(currentSlideId);

    // log all slide total time buckets and time values
    for (slide in timeOnSlides) {
        if (timeOnSlides.hasOwnProperty(slide)) {
            if (timeOnSlides[slide] > 0) {
                var timeBucket = ANALYTICS.getTimeBucket(timeOnSlides[slide] / 1000);
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
            setInterval(cardGetter, fullRefreshRate);
        }
    }

    // set poll for state
    checkState();
    setInterval(checkState, 15000)
}

var getCard = function(url, $card, i) {
    setTimeout(function() {
        $.ajax({
            url: url,
            ifModified: true,
            success: function(data, status) {
                if (status === 'success') {
                    var $cardInner = $(data).find('.full-block');
                    var $cardBackground = $(data).find('.card-background');

                    var htmlString = $cardInner.prop('outerHTML');
                    if ($cardBackground.length > 0) {
                        htmlString += $cardBackground.prop('outerHTML');
                    }

                    $card.html(htmlString);
                    detectMobileBg($card);

                    if ($card.is('#live-audio')) {
                        checkLivestreamStatus();
                    }
                    if ($card.is('.results-multi')) {
                        resultsMultiToggle();
                    }
                }

                if ($card.is('.results') || $card.is('.results-multi')) {
                    resultsCountdown($card);
                }
            }
        });
    }, i * 1000);
}

var checkLivestreamStatus = function() {
    if (LIVE && $audioPlayer.data('jPlayer').status.paused) {
        $('.toggle-btn').removeClass().addClass('toggle-btn play');
    }

    if (!LIVE && $mute.is(':visible')) {
        AUDIO.stopLivestream();
    }
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
                if (oldState === 'before' && currentState === 'during') {
                    setLiveAlert();
                }
            }
        }
    });
}

var setLiveAlert = function() {
    $liveAlert.addClass('signal-during');
    $liveAlertAction.off('click');
    $liveAlertAction.on('click', function() {
        ANALYTICS.trackEvent('alert-click', 'live-event');
        location.reload(true);
    });
}

var setLinkAlert = function() {
    $linkAlert.removeClass('alert-slide-up').addClass('signal-during');
    $linkAlertAction.off('click');
    $linkAlertAction.on('click', function() {
        var index = $cards.index($('#live-audio'));
        $cardsWrapper.flickity('select', index);
        ANALYTICS.trackEvent('alert-click', 'listen-live');
    });
}

var onCloseAlertClick = function() {
    closeAlert();
    ANALYTICS.trackEvent('alert-click', 'close-alert');
}

var closeAlert = function() {
    deeplinkNotificationDismissed = true;
    $linkAlert.addClass('alert-slide-up');
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

var onDonateLinkClick = function(e) {
    var timesToClick = ANALYTICS.calculateTimeBucket(globalStartTime);
    var value = 'Cable donate card - ' + donateButtonText;
    ANALYTICS.trackEvent('donate-link-click', value, timesToClick[0], timesToClick[1]);
}

var onLinkRoundupLinkClick = function() {
    var href = $(this).attr('href');
    var timesToClick = calculateTimeBucket(globalStartTime);
    ANALYTICS.trackEvent('link-roundup-click', href, timesToClick[0], timesToClick[1]);
}


var onStateResultsClick = function() {
    var s = $(this).data('state');

    // toggle it open or closed
    $(this).toggleClass('open');

    // update the list of open states
    if($(this).hasClass('open')) {
        resultsMultiOpen.push(s);
    } else {
        resultsMultiOpen = resultsMultiOpen.filter(function(d) {
            return d != s;
        });
    }
}

// on multi-state result cards, toggle open state
var resultsMultiToggle = function() {
    resultsMultiOpen.forEach(function(d,i) {
        $('.state-result[data-state="' + d + '"]').addClass('open');
    });
}

// countdown spinner to the next results card data refresh
var resultsCountdown = function($card) {
    var refreshRate = parseInt($card.data('refresh-rate'));

    if (refreshRate === 0 || $card.length === 0) {
        return;
    }

    var counter = null;
    var interval = null;

    var $indicator = $card.find('.update-indicator');
    $indicator
        .empty()
        .append('<b class="icon icon-spin3"></b> <span class="text"></span>');

    var $indicatorSpinner = $indicator.find('.icon');
    var $indicatorText = $indicator.find('.text');

    var startIndicator = function() {
        $indicatorSpinner.removeClass('animate-spin');
        counter = refreshRate;
        updateText();
        interval = setInterval(updateIndicator, 1000);
    }

    var updateIndicator = function() {
        counter--;
        updateText();
        if (counter === 0) {
            stopIndicator();
        }
    }

    var stopIndicator = function() {
        clearInterval(interval);
        $indicatorSpinner.addClass('animate-spin');
        $indicatorText.text('Loading');
    }

    var updateText = function() {
        if (counter > 9) {
            $indicatorText.text('0:' + counter);
        } else {
            $indicatorText.text('0:0' + counter);
        }
    }

    startIndicator();

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

    var timesToClick = ANALYTICS.calculateTimeBucket(globalStartTime);
    ANALYTICS.trackEvent('newsletter-subscribe', currentState, timesToClick[0], timesToClick[1]);

    // wait state
    clearStatusMessage();
    var waitMsg = '<div class="message wait">'
    waitMsg += '<p><i class="icon icon-spinner animate-spin"></i>&nbsp;' + COPY.newsletter.waiting_text + '</p>';
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
$(onDocumentLoad);
