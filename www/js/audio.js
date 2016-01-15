var AUDIO = (function() {
    var NO_AUDIO = (window.location.search.indexOf('noaudio') >= 0);

    var setupAudio = function() {
        $audioPlayer.jPlayer({
            swfPath: 'js/lib',
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
    }

    var playAudio = function() {
        $audioPlayer.jPlayer('play');
        $playToggleBtn.removeClass('play').addClass('pause');
    }

    var pauseAudio = function() {
        $audioPlayer.jPlayer('pause');
        $playToggleBtn.removeClass('pause').addClass('play');
    }

    var rewindAudio = function() {
        var currentTime = $audioPlayer.data('jPlayer')['status']['currentTime'];
        var seekTime =  currentTime > 15 ? currentTime - 15 : 0;
        $audioPlayer.jPlayer('play', seekTime);
    }

    var forwardAudio = function() {
        var currentTime = $audioPlayer.data('jPlayer')['status']['currentTime'];
        var seekTime =  currentTime + 15;
        $audioPlayer.jPlayer('play', seekTime);
    };

    var toggleAudio = function() {
        if ($playToggleBtn.hasClass('play')) {
            playAudio();
        } else {
            pauseAudio();
        }
    }

    var onTimeupdate = function() {

    }

    return {
        'setupAudio': setupAudio,
        'setMedia': setMedia,
        'rewindAudio': rewindAudio,
        'forwardAudio': forwardAudio,
        'toggleAudio': toggleAudio
    }
})();

