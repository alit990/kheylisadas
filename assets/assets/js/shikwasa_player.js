// $(document).ready(function () {
//     Player.use(Chapter);
//
//     let kplayer;
//     const playerStorageKey = 'kplayer_state';
//     const isAudioPage = window.location.pathname.includes('audio');
//     let seekedDone = false;
//
//     function savePlayerState(isPlaying) { // isPlaying به عنوان آرگومان دریافت می‌شود
//         if (kplayer && kplayer.audio) {
//             const audioData = {
//                 src: kplayer.audio.src,
//                 title: kplayer.audio.title,
//                 artist: kplayer.audio.artist,
//                 cover: kplayer.audio.cover,
//                 chapters: kplayer.audio.chapters,
//             };
//
//             localStorage.setItem(playerStorageKey, JSON.stringify({
//                 audio: audioData,
//                 currentTime: kplayer.currentTime,
//                 isPlaying: isPlaying // مقدار isPlaying به درستی ذخیره می‌شود
//             }));
//         }
//     }
//
//     // بازیابی وضعیت پلیر
//     const storedPlayerState = localStorage.getItem(playerStorageKey);
//     console.log(storedPlayerState);
//     if (storedPlayerState) {
//         try {
//             const parsedState = JSON.parse(storedPlayerState);
//             if (parsedState.audio && parsedState.audio.src) {
//                 kplayer = new Player({
//                     container: isAudioPage ? $('#player-main').get(0) : $('#player-floating').get(0),
//                     audio: parsedState.audio,
//                     themeColor: "#FFFFFFFF",
//                     theme: 'dark',
//                     fixed: {type: isAudioPage ? 'static' : 'fixed'},
//                 });
//
//                 kplayer.on('canplay', function () {
//                     if (!seekedDone && typeof parsedState.currentTime === 'number' && !isNaN(parsedState.currentTime)) {
//                         const currentTime = Number(parsedState.currentTime);
//                         if (typeof kplayer.seek === 'function') {
//                             kplayer.seek(currentTime);
//                             kplayer.on('seeked', () => {
//                                 seekedDone = true;
//                                 if (!isAudioPage && parsedState.isPlaying) {
//                                     kplayer.play();
//                                 }
//                             });
//                         } else {
//                             kplayer.currentTime = currentTime;
//                             seekedDone = true;
//                             if (!isAudioPage && parsedState.isPlaying) {
//                                 kplayer.play();
//                             }
//                         }
//                     } else if (!isAudioPage && parsedState.isPlaying && !seekedDone) {
//                         kplayer.play();
//                         seekedDone = true;
//                     }
//                 });
//
//                 kplayer.on('chapterchange', function () { /* ... */
//                 });
//                 kplayer.on('pause', function () {
//                     pauseAnimation();
//                     savePlayerState(false); // ذخیره وضعیت pause
//                 });
//
//                 kplayer.on('play', function () {
//                     playAnimation();
//                     savePlayerState(true); // ذخیره وضعیت play
//                 });
//                 kplayer.on('timeupdate', function(){ // رفع وارنینگ
//                     savePlayerState(!kplayer.paused);
//                 });
//                 kplayer.on('ended', () => localStorage.removeItem(playerStorageKey));
//
//                 if (!isAudioPage) {
//                     $('#player-main').hide();
//                 } else {
//                     $('#player-floating').hide();
//                 }
//                 if (!isAudioPage && parsedState.isPlaying) {
//                     $('#player-floating').show();
//                 }
//             }
//         } catch (error) {
//             console.error("Error parsing player state from localStorage:", error);
//             localStorage.removeItem(playerStorageKey);
//         }
//     }
//     // تعریف متغیرها فقط در صورتی که در صفحه فایل صوتی هستیم
//     let chapterIndex, chapterName;
//     if (isAudioPage) {
//         chapterIndex = (window.chapterIndexParam >= 0 && window.chapterIndexParam < window.chapter_set.length) ? window.chapterIndexParam : -1;
//         chapterName = chapterIndex >= 0 ? window.chapter_set[chapterIndex].name : '';
//     }
//
//     function createAudio() {
//         const csrfToken = getCSRFToken();
//
//         if (!kplayer && isAudioPage) {
//             getAudioUrl(csrfToken, window.audio.id, "CCDETAIL").then(function (audioResponse) {
//                 if (audioResponse.url) {
//                     let player_chapters = window.chapter_set.map((chapter, i) => ({
//                         id: chapter.id,
//                         startTime: convertToSeconds(chapter.start_time),
//                         endTime: convertToSeconds((i < window.chapter_set.length - 1) ? window.chapter_set[i + 1].start_time : "پایان فایل صوتی"),
//                         title: `${i + 1}. ${chapter.name}`,
//                     }));
//
//                     kplayer = new Player({
//                         container: $('#player-main').get(0),
//                         audio: {
//                             title: window.audio.name,
//                             artist: '« خیلی ساده‌ست »',
//                             cover: "{% static 'assets/img/audio-icon.png' %}",
//                             chapters: player_chapters,
//                             src: audioResponse.url,
//                         },
//                         themeColor: "#FFFFFFFF",
//                         theme: 'dark',
//                         fixed: {type: isAudioPage ? 'static' : 'fixed'},
//                     });
//                     console.log('create');
//                     console.log(kplayer);
//                     // ذخیره وضعیت پلیر
//
//                     kplayer.on('timeupdate', savePlayerState);
//                     kplayer.on('pause', savePlayerState);
//                     kplayer.on('ended', () => localStorage.removeItem(playerStorageKey));
//
//                     kplayer.on('chapterchange', function () {
//                         const currentChapter = kplayer.currentChapter;
//                         if (currentChapter) {
//                             updateChapterIcons(currentChapter.index);
//                         }
//                     });
//
//                     kplayer.on('pause', function () {
//                         pauseAnimation();
//                     });
//
//                     kplayer.on('play', function () {
//                         playAnimation();
//                     });
//                     if (chapterIndex !== null && chapterIndex >= 0) {
//                         Swal.fire({
//                             text: `مطلبی که به دنبالش هستید در قسمت ${chapterIndex + 1} با موضوع "${chapterName}" قرار دارد. مایلید فایل را از کدام قسمت گوش کنید؟`,
//                             icon: 'info',
//                             showCancelButton: true,
//                             confirmButtonText: 'پخش از قسمت ' + (chapterIndex + 1),
//                             cancelButtonText: 'پخش از ابتدا'
//                         }).then((result) => {
//                             if (result.isConfirmed) {
//                                 myUpdateChapter(window.audio.id, chapterIndex);
//                                 const playPromise = kplayer.play();
//                                 if (playPromise !== undefined) {
//                                     playPromise.catch(error => {
//                                         console.error("Auto-play failed: ", error);
//                                     });
//                                 }
//                             } else {
//                                 kplayer.play().catch(error => {
//                                     console.error("Auto-play failed: ", error);
//                                 });
//                             }
//                         });
//                     } else {
//                         kplayer.play().catch(error => {
//                             console.error("Auto-play failed: ", error);
//                         });
//                     }
//                 } else {
//                     console.log("audio is LOCKED!");
//                 }
//             });
//         }
//     }
//
//     if (isAudioPage) {
//         createAudio();
//         $('#player-main').css({position: 'static', display: 'block'});
//         $('#player-floating').css({display: 'none'});
//     } else if (kplayer && kplayer.paused === false) {
//         $('#player-floating').css({position: 'fixed', bottom: 0, display: 'block'});
//         $('#player-main').hide();
//     }
//
//     // *** کد مربوط به pageshow (بهبود یافته) ***
//     $(window).on('pageshow', function(event) {
//         if (localStorage.getItem(playerStorageKey)) {
//             const storedPlayerState = localStorage.getItem(playerStorageKey);
//             try {
//                 const parsedState = JSON.parse(storedPlayerState);
//                 if (parsedState.isPlaying && kplayer && !kplayer.playing) {
//                     kplayer.play();
//                 }
//             } catch (error) {
//                 // ...
//             }
//         }
//     });
//     // *** پایان کد مربوط به pagehide و pageshow ***
//
//
//     // توابع کمکی
//     function getCookie(name) {
//         let cookieValue = null;
//         if (document.cookie && document.cookie !== '') {
//             const cookies = document.cookie.split(';');
//             for (let i = 0; i < cookies.length; i++) {
//                 const cookie = cookies[i].trim();
//                 if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                     break;
//                 }
//             }
//         }
//         return cookieValue;
//     }
//
//     function getCSRFToken() {
//         return getCookie('csrftoken');
//     }
//
//     function getAudioUrl(csrfToken, audio_id, audio_type) {
//         return $.ajax({
//             url: audioGetUrl,
//             method: "POST",
//             data: {
//                 csrfToken: csrfToken,
//                 audio_id: audio_id,
//                 audio_type: audio_type,
//                 has_perm: hasPerm,
//             },
//             headers: {'X-CSRFToken': csrfToken},
//             xhrFields: {withCredentials: true}
//         });
//     }
//
//     function myUpdateChapter(audio_id, chapter_index) {
//         console.log(audio_id, chapter_index);
//         console.log(kplayers);
//         var kplayer = kplayers.find(kplayer => kplayer.audio_id === audio_id);
//         console.log(kplayer);
//         kplayer.updateChapter(chapter_index);
//         updateChapterIcons(chapter_index);
//     }
//
//     function updateChapterIcons(currentIndex) {
//         $('.equalizer').hide();
//         $('.ti-music').show();
//         const currentIcon = $(`#chapter-icon-${currentIndex}`);
//         const currentEqualizer = $(`#equalizer-${currentIndex}`);
//         if (currentIcon.length && currentEqualizer.length) {
//             currentIcon.hide();
//             currentEqualizer.show();
//         }
//     }
//
//     function convertToSeconds(time) {
//         const [minutes, seconds] = time.split(':').map(Number);
//         return minutes * 60 + seconds;
//     }
//
//     function pauseAnimation() {
//         $('.equalizer').css('animation-play-state', 'paused');
//     }
//
//     function playAnimation() {
//         $('.equalizer').css('animation-play-state', 'running');
//     }
// });
