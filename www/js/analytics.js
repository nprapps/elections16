/*
 * Module for tracking standardized analytics.
 */

var _gaq = _gaq || [];
var _sf_async_config = {};
var _comscore = _comscore || [];

var ANALYTICS = (function () {

    // Global time tracking variables
    var slideStartTime =  new Date();
    var timeOnLastSlide = null;

    /*
     * Google Analytics
     */
    var setupGoogle = function() {
        var orientation = 'portrait';
        if (window.orientation == 90 || window.orientation == -90) {
            orientation = 'landscape';
        }

        var screenType = Modernizr.touch ? 'touch' : 'traditional';

        var station = Cookies.get('station');

        var customDimensions = {
            'dimension1': null, // story ID (seamus ID for stub?)
            'dimension2': APP_CONFIG.NPR_GOOGLE_ANALYTICS.TOPICS, // topics
            'dimension3': APP_CONFIG.NPR_GOOGLE_ANALYTICS.PRIMARY_TOPIC, // primary topic
            'dimension4': null, // story theme, what is this?
            'dimension5': null, // program
            'dimension6': null, // parents, what is this?
            'dimension7': null, // story tags
            'dimension8': null, // byline
            'dimension9': null, // content partner organization
            'dimension10': null, // publish date, does this make sense for our project?
            'dimension11': null, // page type, what are we?
            'dimension12': null, // original referrer, from localstorage
            'dimension13': null, // original landing page, from localstorage
            'dimension14': station ? station : null, // localized station, read the cookie
            'dimension15': null, // favorite station, read the cookie
            'dimension16': null, // audio listener, from localstorage
            'dimension17': null, // days since first session, from localstorage
            'dimension18': null, // first session date, from localstorage
            'dimension19': null, // registered user, from localstorage
            'dimension20': null, // logged in sessions, from localstorage
            'dimension21': null, // registration date, from localstorage
            'dimension22': document.title, // story title
            'dimension23': orientation, // screen orientation
            'dimension24': screenType // screen type
        };

        (function(i,s,o,g,r,a,m) {
            i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
            (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
            m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
        })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

        ga('create', APP_CONFIG.VIZ_GOOGLE_ANALYTICS.ACCOUNT_ID, 'auto');
        ga('create', APP_CONFIG.NPR_GOOGLE_ANALYTICS.ACCOUNT_ID, 'auto', 'dotOrgTracker');
        ga('dotOrgTracker.set', customDimensions);
        ga('send', 'pageview');
        ga('dotOrgTracker.send', 'pageview');
     }

    /*
     * Comscore
     */
    var setupComscore = function() {
        _comscore.push({ c1: "2", c2: "17691522" });

        (function() {
            var s = document.createElement("script"), el = document.getElementsByTagName("script")[0]; s.async = true;
            s.src = (document.location.protocol == "https:" ? "https://sb" : "http://b") + ".scorecardresearch.com/beacon.js";
            el.parentNode.insertBefore(s, el);
        })();
    }

    /*
     * Nielson
     */
    var setupNielson = function() {
        (function () {
            var d = new Image(1, 1);
            d.onerror = d.onload = function () { d.onerror = d.onload = null; };
            d.src = ["//secure-us.imrworldwide.com/cgi-bin/m?ci=us-803244h&cg=0&cc=1&si=", escape(window.location.href), "&rp=", escape(document.referrer), "&ts=compact&rnd=", (new Date()).getTime()].join('');
        })();
    }

    /*
     * Chartbeat
     */
    var setupChartbeat = function() {
        /** CONFIGURATION START **/
        _sf_async_config.uid = 18888;
        _sf_async_config.domain = "npr.org";
        /** CONFIGURATION END **/
        (function(){
            function loadChartbeat() {
                window._sf_endpt=(new Date()).getTime();
                var e = document.createElement("script");
                e.setAttribute("language", "javascript");
                e.setAttribute("type", "text/javascript");
                e.setAttribute("src",
                    (("https:" == document.location.protocol) ?
                     "https://a248.e.akamai.net/chartbeat.download.akamai.com/102508/" :
                     "http://static.chartbeat.com/") +
                    "js/chartbeat.js");
                document.body.appendChild(e);
            }
            var oldonload = window.onload;
            window.onload = (typeof window.onload != "function") ?
                loadChartbeat : function() { oldonload(); loadChartbeat(); };
        })();
    }

    /*
     * Event tracking.
     */
    var trackEvent = function(category, action, label, value) {
        var eventData = {
            'hitType': 'event',
            'eventCategory': category
        }

        if (action) {
            eventData['eventAction'] = action
        }

        if (label) {
            eventData['eventLabel'] = label;
        }

        if (value) {
            eventData['eventValue'] = value;
        }

        ga('send', eventData);
    }

    // SHARING

    var openShareDiscuss = function() {
        trackEvent('open-share-discuss');
    }

    var closeShareDiscuss = function() {
        trackEvent('close-share-discuss');
    }

    var clickTweet = function(location) {
        trackEvent('tweet', location);
    }

    var clickFacebook = function(location) {
        trackEvent('facebook', location);
    }

    var clickEmail = function(location) {
        trackEvent('email', location);
    }

    var postComment = function() {
        trackEvent('new-comment');
    }

    var actOnFeaturedTweet = function(action, tweet_url) {
        trackEvent('featured-tweet-action', action, null);
    }

    var actOnFeaturedFacebook = function(action, post_url) {
        trackEvent('featured-facebook-action', action, null);
    }

    var copySummary = function() {
        trackEvent('summary-copied');
    }

    // NAVIGATION
    var usedKeyboardNavigation = false;

    var useKeyboardNavigation = function() {
        if (!usedKeyboardNavigation) {
            trackEvent('keyboard-nav');
            usedKeyboardNavigation = true;
        }
    }

    var completeTwentyFivePercent =  function() {
        trackEvent('completion', '0.25');
    }

    var completeFiftyPercent =  function() {
        trackEvent('completion', '0.5');
    }

    var completeSeventyFivePercent =  function() {
        trackEvent('completion', '0.75');
    }

    var completeOneHundredPercent =  function() {
        trackEvent('completion', '1');
    }

    var startFullscreen = function() {
        trackEvent('fullscreen-start');
    }

    var stopFullscreen = function() {
        trackEvent('fullscreen-stop');
    }

    var begin = function(location) {
        trackEvent('begin', location);
    }

    var readyChromecast = function() {
        trackEvent('chromecast-ready');
    }

    var startChromecast = function() {
        trackEvent('chromecast-start');
    }

    var stopChromecast = function() {
        trackEvent('chromecast-stop');
    }

    setupGoogle();
    setupComscore();
    setupNielson();

    return {
        'setupChartbeat': setupChartbeat,
        'trackEvent': trackEvent,
        'openShareDiscuss': openShareDiscuss,
        'closeShareDiscuss': closeShareDiscuss,
        'clickTweet': clickTweet,
        'clickFacebook': clickFacebook,
        'clickEmail': clickEmail,
        'postComment': postComment,
        'actOnFeaturedTweet': actOnFeaturedTweet,
        'actOnFeaturedFacebook': actOnFeaturedFacebook,
        'copySummary': copySummary,
        'useKeyboardNavigation': useKeyboardNavigation,
        'completeTwentyFivePercent': completeTwentyFivePercent,
        'completeFiftyPercent': completeFiftyPercent,
        'completeSeventyFivePercent': completeSeventyFivePercent,
        'completeOneHundredPercent': completeOneHundredPercent,
        'startFullscreen': startFullscreen,
        'stopFullscreen': stopFullscreen,
        'begin': begin,
        'readyChromecast': readyChromecast,
        'startChromecast': startChromecast,
        'stopChromecast': stopChromecast
    };
}());
