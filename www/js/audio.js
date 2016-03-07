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

        $cards.eq(audioPlayingIndex).find('.toggle-btn').removeClass().addClass('toggle-btn loading fa-spin');
        $cards.eq(audioPlayingIndex).find('.segment-text').text('Loading');

        for (var i = 0; i < timedAnalytics.length; i++) {
            timedAnalytics[i]['measured'] = false;
        }

        ANALYTICS.trackEvent('audio-started', url);
    }

    var playAudio = function() {
        $audioPlayer.jPlayer('play');

        audioPlayingIndex = currentCard;

        $('.toggle-btn').removeClass().addClass('toggle-btn play');
        $cards.eq(audioPlayingIndex).find('.toggle-btn').removeClass().addClass('toggle-btn pause');

        $('.rewind').addClass('darken');
        $('.forward').addClass('darken');
        $cards.eq(audioPlayingIndex).find('.rewind').removeClass('darken');
        $cards.eq(audioPlayingIndex).find('.forward').removeClass('darken');

        $nowPlaying.removeClass('stop-playing').addClass('is-playing');
    }


    var pauseAudio = function() {
        $audioPlayer.jPlayer('pause');
        $cards.eq(audioPlayingIndex).find('.toggle-btn').removeClass().addClass('toggle-btn play');
        $cards.eq(audioPlayingIndex).find('.rewind').addClass('darken');
        $cards.eq(audioPlayingIndex).find('.forward').addClass('darken');
        $nowPlaying.removeClass('is-playing').addClass('stop-playing');

        ANALYTICS.trackEvent('audio-paused', $audioPlayer.data().jPlayer.status.src);
    }

    var stopAudio = function() {
        $audioPlayer
            .jPlayer('stop')
            .jPlayer('clearMedia');
        $cards.eq(audioPlayingIndex).find('.toggle-btn').removeClass().addClass('toggle-btn play');
        $nowPlaying.removeClass('is-playing').addClass('stop-playing');
        ANALYTICS.trackEvent('audio-stopped', $audioPlayer.data().jPlayer.status.src);
    }

    var rewindAudio = function() {
        if ($(this).hasClass('darken')) {
            return;
        }

        if (!$audioPlayer.data('jPlayer').status.paused) {
            var currentTime = $audioPlayer.data('jPlayer')['status']['currentTime'];
            var seekTime =  currentTime > 15 ? currentTime - 15 : 0;
            $audioPlayer.jPlayer('play', seekTime);

            ANALYTICS.trackEvent('audio-rewind', $audioPlayer.data().jPlayer.status.src);
        }
    }

    var forwardAudio = function() {
        if ($(this).hasClass('darken')) {
            return;
        }

        if (!$audioPlayer.data('jPlayer').status.paused) {
            var currentTime = $audioPlayer.data('jPlayer')['status']['currentTime'];
            var seekTime =  currentTime + 15;
            $audioPlayer.jPlayer('play', seekTime);

            ANALYTICS.trackEvent('audio-forward', $audioPlayer.data().jPlayer.status.src);
        }
    };

    var toggleAudio = function() {
        var url = $(this).data('url');
        var currentSrc = $audioPlayer.data('jPlayer')['status']['src'];
        var currentState = $audioPlayer.data('jPlayer')['status']['paused']

        if (currentSrc !== url) {
            setMedia(url);
            return;
        }

        if (currentState === true && currentSrc === url ) {
            playAudio();
        } else if (currentState === false && currentSrc === url) {
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

        if ($cards.eq(audioPlayingIndex).find('.toggle-btn').hasClass('loading')) {
            $cards.eq(audioPlayingIndex).find('.toggle-btn').removeClass().addClass('toggle-btn pause');
            if (LIVE) {
                $cards.eq(audioPlayingIndex).find('.segment-type').text('Live Audio');
            }
        }

        if (position > 10) {
            var timeBucket = ANALYTICS.getTimeBucket(position);
            if (!timedAnalytics[timeBucket]) {
                timedAnalytics[timeBucket] = true;
                ANALYTICS.trackEvent('audio-time-listened', $audioPlayer.data().jPlayer.status.src, timeBucket);
            }
        }

        $cards.eq(audioPlayingIndex).find('.duration').text($.jPlayer.convertTime(remainingTime));
    }

    var onEnded = function(e) {
        $cards.eq(audioPlayingIndex).find('.toggle-btn').removeClass('pause').addClass('play');
        $cards.eq(audioPlayingIndex).find('.rewind').addClass('darken');
        $cards.eq(audioPlayingIndex).find('.forward').addClass('darken');
        $nowPlaying.removeClass('is-playing').addClass('stop-playing');
        ANALYTICS.trackEvent('audio-ended', $audioPlayer.data().jPlayer.status.src);
    }

    var stopLivestream = function(e) {
        stopAudio();
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
