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
    var nproneDeepLink = (window.location.search.indexOf('nprone') >= 0);
    var queryParams = window.location.search;

    /*
     * Google Analytics
     */

    var embedGa = function() {
        (function(i,s,o,g,r,a,m) {
            i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
            (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
            m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
        })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
    }

    var setupVizAnalytics = function() {
        ga('create', APP_CONFIG.VIZ_GOOGLE_ANALYTICS.ACCOUNT_ID, 'auto');
        if (nproneDeepLink) {
            ga('set', 'page', '/' + queryParams);
        }
        ga('send', 'pageview');
    }

    var setupDotOrgAnalytics = function() {
        ga('create', APP_CONFIG.NPR_GOOGLE_ANALYTICS.ACCOUNT_ID, 'auto', 'dotOrgTracker');
        if (nproneDeepLink) {
            ga('dotOrgTracker.set', 'page', '/' + queryParams);
        }

        var orientation = 'portrait';
        if (window.orientation == 90 || window.orientation == -90) {
            orientation = 'landscape';
        }
        var screenType = Modernizr.touch ? 'touch' : 'traditional';
        var station = Cookies.get('station');

        var customDimensions = {
            'dimension1': null, // story ID (this is the SEAMUS ID)
            'dimension2': APP_CONFIG.NPR_GOOGLE_ANALYTICS.TOPICS, // topics, see Google spreadsheet for ids. First id begins with P for primary
            'dimension3': APP_CONFIG.NPR_GOOGLE_ANALYTICS.PRIMARY_TOPIC, // primary topic -- name of the topic, not the ID
            'dimension4': null, // story theme, which is the html theme in Seamus
            'dimension5': null, // program, english name of program
            'dimension6': APP_CONFIG.NPR_GOOGLE_ANALYTICS.TOPICS, // parents, roll up program, theme, topics, etc.
            'dimension7': null, // story tags
            'dimension8': null, // byline
            'dimension9': null, // content partner organization
            'dimension10': null, // publish date, yyyymmddhh
            'dimension11': null, // page type, seamus page type
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

        var storage = new CrossStorageClient('http://www.npr.org/politics/election2016/cross-storage-iframe.html');
        storage.onConnect().then(function() {
            return storage.get('firstVisitDate', 'hasListenedToAudio', 'isLoggedIn', 'isRegistered', 'originalLandingPage', 'originalReferrer', 'regDate');
        }).then(function(res) {
            customDimensions['dimension17'] = res[0] ?  setDaysSinceFirstVisit(storage, res[0]) : 0;
            customDimensions['dimension18'] = res[0] ? res[0] : setFirstVisitDate(storage);
            customDimensions['dimension16'] = res[1] ? res[1] : null;
            customDimensions['dimension20'] = res[2] ? res[2] : null;
            customDimensions['dimension19'] = res[3] ? res[3] : null;
            customDimensions['dimension13'] = res[4] ? res[4] : setOriginalLandingPage(storage);
            customDimensions['dimension12'] = res[5] ? res[5] :  setOriginalReferrer(storage);
            customDimensions['dimension21'] = res[6] ? res[6] : null;
            ga('dotOrgTracker.set', customDimensions);
            ga('dotOrgTracker.send', 'pageview');
        });
    }

    var setDaysSinceFirstVisit = function(storage, firstDate) {
        var firstDateISO = firstDate.substring(0, 4) + '-' + firstDate.substring(4, 6) + '-' + firstDate.substring(6);
        var firstDateTime = new Date(firstDateISO)
        var now = new Date();

        var oneDay = 24 * 60 * 60 * 1000;
        var daysSince = Math.round(Math.abs((firstDateTime.getTime() - now.getTime())/(oneDay)));

        return daysSince.toString();
    }

    var setFirstVisitDate = function(storage) {
        var now = new Date();
        var year = now.getFullYear().toString();
        var day = now.getDate().toString();
        var month = now.getMonth() + 1;
        if (month < 10) {
            month = '0' + month.toString();
        }
        var dateString = year + month + day;

        storage.set('firstVisitDate', dateString);
        return dateString;
    }

    var setOriginalLandingPage = function(storage) {
        var url = APP_CONFIG.S3_BASE_URL;
        storage.set('originalLandingPage', url);
        return url;
    }

    var setOriginalReferrer = function(storage) {
        var referrerString = null;

        var utmSource = getParameterByName('utm_source', window.location.href);
        if (utmSource) {
            referrerString = utmSource;
        } else {
            var referrer = document.referrer;
            if (!referrer) {
                referrerString = 'direct';
            } else {
                var l = document.createElement('a');
                l.href = referrer;
                referrerString = l.hostname;
            }
        }

        storage.set('originalReferrer', referrerString);
        return referrerString;
    }

    function getParameterByName(name, url) {
        if (!url) url = window.location.href;
        name = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }

    var setupGoogle = function() {
        embedGa();
        setupVizAnalytics();
        setupDotOrgAnalytics();
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

    var logCardExit = function(id, exitEvent) {
        var timeValue = calculateSlideExitTime(id);
        ANALYTICS.trackEvent('card-exit', id, exitEvent, timeValue);
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


    setupGoogle();
    setupComscore();
    setupNielson();

    return {
        'setupChartbeat': setupChartbeat,
        'trackEvent': trackEvent,
        'logCardExit': logCardExit,
        'calculateSlideExitTime': calculateSlideExitTime,
        'calculateTimeBucket': calculateTimeBucket,
        'getTimeBucket': getTimeBucket,
        'nproneDeepLink': nproneDeepLink
    };
}());
