var AUDIO = (function() {
    var NO_AUDIO = (window.location.search.indexOf('noaudio') >= 0);
    var timedAnalytics = {};

    var setupAudio = function() {
        $audioPlayer.jPlayer({
            swfPath: 'js/lib',
            ended: onEnded,
            loop: false,
            supplied: 'mp3',
            timeupdate: onTimeupdate,
            preload: 'none',
            volume: NO_AUDIO ? 0 : 1
        });
    }

    var setMedia = function(url) {
        $audioPlayer.jPlayer('setMedia', {
            'mp3': url
        });
        playAudio();

        $('.toggle-btn').removeClass().addClass('toggle-btn loading fa-spin');
        $segmentType.text('Loading');

        $mute.show();

        for (var i = 0; i < timedAnalytics.length; i++) {
            timedAnalytics[i]['measured'] = false;
        }

        ANALYTICS.trackEvent('audio-started', url);
    }

    var playAudio = function() {
        $audioPlayer.jPlayer('play');
        $('.toggle-btn').removeClass().addClass('toggle-btn pause');
        $mute.show();
        $mute.removeClass('muted').addClass('playing');
        $rewindBtn.removeClass('darken');
        $forwardBtn.removeClass('darken');
    }

    var pauseAudio = function() {
        $audioPlayer.jPlayer('pause');
        $('.toggle-btn').removeClass().addClass('toggle-btn play');
        $mute.removeClass('playing').addClass('muted');
        $rewindBtn.addClass('darken');
        $forwardBtn.addClass('darken');

        ANALYTICS.trackEvent('audio-paused', $audioPlayer.data().jPlayer.status.src);
    }

    var stopAudio = function() {
        $audioPlayer
            .jPlayer('stop')
            .jPlayer('clearMedia');
        $mute.removeClass('playing').addClass('muted');
        $('.toggle-btn').removeClass().addClass('toggle-btn play');
        ANALYTICS.trackEvent('audio-stopped', $audioPlayer.data().jPlayer.status.src);
    }

    var rewindAudio = function() {
        if (!$audioPlayer.data('jPlayer').status.paused) {
            var currentTime = $audioPlayer.data('jPlayer')['status']['currentTime'];
            var seekTime =  currentTime > 15 ? currentTime - 15 : 0;
            $audioPlayer.jPlayer('play', seekTime);

            ANALYTICS.trackEvent('audio-rewind', $audioPlayer.data().jPlayer.status.src);
        }
    }

    var forwardAudio = function() {
        if (!$audioPlayer.data('jPlayer').status.paused) {
            var currentTime = $audioPlayer.data('jPlayer')['status']['currentTime'];
            var seekTime =  currentTime + 15;
            $audioPlayer.jPlayer('play', seekTime);

            ANALYTICS.trackEvent('audio-forward', $audioPlayer.data().jPlayer.status.src);
        }
    };

    var toggleAudio = function() {
        if ($audioPlayer.data('jPlayer')['status']['paused']) {
            if (LIVE) {
                setMedia(LIVE_AUDIO_URL);
            } else {
                playAudio();
            }
        } else {
            if (LIVE) {
                stopAudio();
            } else {
                pauseAudio();
            }
        }
    }

    var onTimeupdate = function(e) {
        var totalTime = e.jPlayer.status.duration;
        var position = e.jPlayer.status.currentTime;
        var remainingTime = totalTime - position;

        if ($('.toggle-btn').hasClass('loading')) {
            $('.toggle-btn').removeClass().addClass('toggle-btn pause');
            if (LIVE) {
                $segmentType.text('Live Audio');
            }
        }

        if (position > 10) {
            var timeBucket = getTimeBucket(position);
            if (!timedAnalytics[timeBucket]) {
                timedAnalytics[timeBucket] = true;
                ANALYTICS.trackEvent('audio-time-listened', $audioPlayer.data().jPlayer.status.src, timeBucket);
            }
        }

        $duration.text($.jPlayer.convertTime(remainingTime));
    }

    var onEnded = function(e) {
        $mute.hide();
        $('.toggle-btn').removeClass('pause').addClass('play');
        $rewindBtn.addClass('darken');
        $forwardBtn.addClass('darken');
        ANALYTICS.trackEvent('audio-ended', $audioPlayer.data().jPlayer.status.src);
    }

    var stopLivestream = function(e) {
        stopAudio();
        $mute.hide();
    }

    return {
        'setupAudio': setupAudio,
        'setMedia': setMedia,
        'rewindAudio': rewindAudio,
        'forwardAudio': forwardAudio,
        'toggleAudio': toggleAudio,
        'stopLivestream': stopLivestream
    }
})();

