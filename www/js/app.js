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
var $newsletterForm = null;

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
    $globalHeader = $('.global-header');
    $globalControls = $('.global-controls');
    $duration = $('.duration');
    $begin = $('.begin');
    $newsletterForm = $('#newsletter-signup');

    $playToggleBtn.on('click', AUDIO.toggleAudio);
    $rewindBtn.on('click', AUDIO.rewindAudio);
    $forwardBtn.on('click', AUDIO.forwardAudio);
    $begin.on('click', onBeginClick);
    $newsletterForm.on('submit', onNewsletterSubmit);

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
    //$globalHeader.addClass('bg-header');
    $cards.off('scroll');
}

var onCardChange = function(e) {
    var flickity = $cardsWrapper.data('flickity');
    var oldSlideIndex = flickity.selectedIndex - 1;
    var newSlideIndex = flickity.selectedIndex;

    var $thisSlide = $('.is-selected');

    $globalHeader.removeClass('bg-header');
    $cards.on('scroll', onCardScroll);

    if (newSlideIndex > 0) {
        $globalControls.show();
        $globalHeader.show();
        //$globalHeader.addClass('bg-header');
    } else {
        $globalControls.hide();
        $globalHeader.hide();
    }

    if ($thisSlide.is('#podcast') && $audioPlayer.data().jPlayer.status.currentTime === 0) {
        AUDIO.setMedia(PODCAST_URL);
    }
}

var onCardAnimationFinish = function(e) {
    var flickity = $cardsWrapper.data('flickity');
    var newSlideIndex = flickity.selectedIndex;

    if (newSlideIndex > 0) {
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

var onNewsletterSubmit = function(e) {
    e.preventDefault();

    var $el = $(this);
    var email = $el.find('#newsletter-email').val();

    if (!email) {
        return;
    }

    ANALYTICS.trackEvent('newsletter-signup');
    $el.css('opacity', 0.5);

    $.ajax({
        url: APP_CONFIG.NEWSLETTER_POST_URL,
        timeout: APP_CONFIG.NEWSLETTER_POST_TIMEOUT,
        method: 'POST',
        data: {
            email: email,
            orgId: 0,
            isAuthenticated: false
        },
        success: function(response) {
            $el.html('success');
            $el.css('opacity', 1);
            ANALYTICS.trackEvent('newsletter-signup-success');
        },
        error: function(response) {
            $el.html('error');
            $el.css('opacity', 1);
            ANALYTICS.trackEvent('newsletter-signup-error');
        }
    });
}

$(onDocumentLoad);
