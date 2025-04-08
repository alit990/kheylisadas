import {createPlayer, savePlayerState, getPlayer, $} from '../../scripts/playerModule.js';

$(document).ready(function () {
    const playerStorageKey = 'kplayer_state';
    const isAudioPage = window.location.pathname.includes('audio');
    let seekedDone = false;
    let kplayer = getPlayer();

    if (!kplayer) {
        const storedPlayerState = localStorage.getItem(playerStorageKey);
        if (storedPlayerState) {
            try {
                const parsedState = JSON.parse(storedPlayerState);
                if (parsedState.audio && parsedState.audio.src) {
                    kplayer = createPlayer(isAudioPage ? $('#player-main').get(0) : $('#player-floating').get(0), parsedState.audio);
                    kplayer.on('canplay', function () {
                        if (!seekedDone && typeof parsedState.currentTime === 'number' && !isNaN(parsedState.currentTime)) {
                            const currentTime = Number(parsedState.currentTime);
                            if (typeof kplayer.seek === 'function') {
                                kplayer.seek(currentTime);
                                kplayer.on('seeked', () => {
                                    seekedDone = true;
                                    if (!isAudioPage && parsedState.isPlaying) {
                                        kplayer.play();
                                    }
                                });
                            } else {
                                kplayer.currentTime = currentTime;
                                seekedDone = true;
                                if (!isAudioPage && parsedState.isPlaying) {
                                    kplayer.play();
                                }
                            }
                        } else if (!isAudioPage && parsedState.isPlaying && !seekedDone) {
                            kplayer.play();
                            seekedDone = true;
                        }
                    });
                }
            } catch (e) {
                console.log(e);
            }
        } else if (isAudioPage) {
            createAudio();
        }
    } else {
        const storedPlayerState = localStorage.getItem(playerStorageKey);
        if (storedPlayerState) {
            try {
                const parsedState = JSON.parse(storedPlayerState);
                kplayer.on('canplay', function () {
                    if (!seekedDone && typeof parsedState.currentTime === 'number' && !isNaN(parsedState.currentTime)) {
                        const currentTime = Number(parsedState.currentTime);
                        if (typeof kplayer.seek === 'function') {
                            kplayer.seek(currentTime);
                            kplayer.on('seeked', () => {
                                seekedDone = true;
                                if (!isAudioPage && parsedState.isPlaying) {
                                    kplayer.play();
                                }
                            });
                        } else {
                            kplayer.currentTime = currentTime;
                            seekedDone = true;
                            if (!isAudioPage && parsedState.isPlaying) {
                                kplayer.play();
                            }
                        }
                    } else if (!isAudioPage && parsedState.isPlaying && !seekedDone) {
                        kplayer.play();
                        seekedDone = true;
                    }
                });
            } catch (e) {
                console.log(e);
            }
        }
    }

    $(window).on('pageshow', function (event) {
        let kplayer = getPlayer();
        if (localStorage.getItem(playerStorageKey) && kplayer && !kplayer.playing) {
            const storedPlayerState = localStorage.getItem(playerStorageKey);
            try {
                const parsedState = JSON.parse(storedPlayerState);
                if (parsedState.isPlaying) {
                    kplayer.play();
                }
            } catch (error) {
                console.error("Error parsing player state from localStorage:", error);
                localStorage.removeItem(playerStorageKey);
            }
        }
    });

    // توابع کمکی
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function getCSRFToken() {
        return getCookie('csrftoken');
    }

    function getAudioUrl(csrfToken, audio_id, audio_type) {
        return $.ajax({
            url: audioGetUrl,
            method: "POST",
            data: {
                csrfToken: csrfToken,
                audio_id: audio_id,
                audio_type: audio_type,
                has_perm: hasPerm,
            },
            headers: {'X-CSRFToken': csrfToken},
            xhrFields: {withCredentials: true}
        });
    }

    function myUpdateChapter(audio_id, chapter_index) {
        console.log(audio_id, chapter_index);
        console.log(kplayers);
        var kplayer = kplayers.find(kplayer => kplayer.audio_id === audio_id);
        console.log(kplayer);
        kplayer.updateChapter(chapter_index);
        updateChapterIcons(chapter_index);
    }

    function updateChapterIcons(currentIndex) {
        $('.equalizer').hide();
        $('.ti-music').show();
        const currentIcon = $(`#chapter-icon-${currentIndex}`);
        const currentEqualizer = $(`#equalizer-${currentIndex}`);
        if (currentIcon.length && currentEqualizer.length) {
            currentIcon.hide();
            currentEqualizer.show();
        }
    }

    function convertToSeconds(time) {
        const [minutes, seconds] = time.split(':').map(Number);
        return minutes * 60 + seconds;
    }

    function pauseAnimation() {
        $('.equalizer').css('animation-play-state', 'paused');
    }

    function playAnimation() {
        $('.equalizer').css('animation-play-state', 'running');
    }

});