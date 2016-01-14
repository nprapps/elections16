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

    var playAudio = function(url) {
        $audioPlayer.jPlayer('setMedia', {
            'mp3': url
        }).jPlayer('play');
    }

    var onTimeupdate = function() {

    }

    return {
        'setupAudio': setupAudio,
        'playAudio': playAudio
    }
})();

