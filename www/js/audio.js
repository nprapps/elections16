var AUDIO = (function() {
    var NO_AUDIO = (window.location.search.indexOf('noaudio') >= 0);
    var timedAnalytics = [
        {
            'seconds': 5,
            'unit': '5s',
            'measured': false
        },
        {
            'seconds': 30,
            'unit': '30s',
            'measured': false
        },
        {
            'seconds': 60,
            'unit': '1m',
            'measured': false
        },
        {
            'seconds': 300,
            'unit': '5m',
            'measured': false
        },
    ]

    var setupAudio = function() {
        $audioPlayer.jPlayer({
            swfPath: 'js/lib',
            ended: onEnded,
            loop: false,
            supplied: 'mp3',
            timeupdate: onTimeupdate,
            volume: NO_AUDIO ? 0 : 1
        });
    }

    var setMedia = function(url) {
        $audioPlayer.jPlayer('setMedia', {
            'mp3': url
        });
        playAudio();

        for (var i = 0; i < timedAnalytics.length; i++) {
            timedAnalytics[i]['measured'] = false;
        }

        ANALYTICS.trackEvent('audio-started', url);
    }

    var playAudio = function() {
        $audioPlayer.jPlayer('play');
        $playToggleBtn.removeClass('play').addClass('pause');
        $mute.removeClass('muted').addClass('playing');
        ANALYTICS.trackEvent('audio-resumed', $audioPlayer.data().jPlayer.status.src);
    }

    var pauseAudio = function() {
        $audioPlayer.jPlayer('pause');
        $playToggleBtn.removeClass('pause').addClass('play');
        $mute.removeClass('playing').addClass('muted');
        ANALYTICS.trackEvent('audio-paused', $audioPlayer.data().jPlayer.status.src);
    }

    var rewindAudio = function() {
        var currentTime = $audioPlayer.data('jPlayer')['status']['currentTime'];
        var seekTime =  currentTime > 15 ? currentTime - 15 : 0;
        $audioPlayer.jPlayer('play', seekTime);
        ANALYTICS.trackEvent('audio-rewind', $audioPlayer.data().jPlayer.status.src);
    }

    var forwardAudio = function() {
        var currentTime = $audioPlayer.data('jPlayer')['status']['currentTime'];
        var seekTime =  currentTime + 15;
        $audioPlayer.jPlayer('play', seekTime);
        ANALYTICS.trackEvent('audio-forward', $audioPlayer.data().jPlayer.status.src);
    };

    var toggleAudio = function() {
        if ($playToggleBtn.hasClass('play')) {
            playAudio();
        } else {
            pauseAudio();
        }
    }

    var onTimeupdate = function(e) {
        var totalTime = e.jPlayer.status.duration;
        var position = e.jPlayer.status.currentTime;
        var remainingTime = totalTime - position;

        for (var i = 0; i < timedAnalytics.length; i++) {
            var obj = timedAnalytics[i];

            if (position >= obj.seconds && !obj.measured) {
                ANALYTICS.trackEvent('audio-' + obj.unit, $audioPlayer.data().jPlayer.status.src);
                obj.measured = true;
            }
        }

        $duration.text($.jPlayer.convertTime(remainingTime));
    }

    var onEnded = function(e) {
        ANALYTICS.trackEvent('audio-ended', $audioPlayer.data().jPlayer.status.src);
    }

    return {
        'setupAudio': setupAudio,
        'setMedia': setMedia,
        'rewindAudio': rewindAudio,
        'forwardAudio': forwardAudio,
        'toggleAudio': toggleAudio
    }
})();

