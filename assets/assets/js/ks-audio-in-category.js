function play_onclick(chapterId) {
    var player = $('#playerChapter' + chapterId);
    let a = $('#aChapter' + chapterId);
    if (isPlaying(chapterId)) {
        player.get(0).pause();
        // a.removeClass('fa-pause');
        // a.addClass('fa-play');
        // player.prop("currentTime",0);
    } else {
        player.get(0).play();
        // a.removeClass('fa-play');
        // a.addClass('fa-pause');
    }
}

function onplay_audio(chapterId) {
    document.addEventListener('play', function (e) {
        let audios = document.getElementsByTagName('audio');
        for (let i = 0, len = audios.length; i < len; i++) {
            if (audios[i] !== e.target) {
                audios[i].pause();
            }
        }
    }, true);
    let i = $('#iChapter' + chapterId);
    i.removeClass('fa-play');
    i.addClass('fa-pause');
}

function onpause_play(chapterId) {
    let i = $('#iChapter' + chapterId);
    i.removeClass('fa-pause');
    i.addClass('fa-play');
}

function isPlaying(chapterId) {
    // var player = document.getElementById(playerId);
    let player = $('#playerChapter' + chapterId);
    return !player.get(0).paused && !player.get(0).ended && 0 < player.get(0).currentTime && player.get(0).readyState > 2;
}