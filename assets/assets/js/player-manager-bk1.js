// document.addEventListener('DOMContentLoaded', function () {
//     const {createPlayer, getPlayer, savePlayerState, playerStorageKey} = MyLibrary;
//
//     // const playerStorageKey = 'kplayer_state';
//     const isAudioPage = window.location.pathname.includes('audio');
//     let seekedDone = false;
//     let kplayer = getPlayer();
//
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
//         // دیگر نیازی به خواندن از HTML نیست
//         return $.ajax({
//             url: audioGetUrl, // از متغیر سراسری audioGetUrl استفاده میکنیم
//             method: "POST",
//             data: {
//                 csrfToken: csrfToken,
//                 audio_id: audio_id,
//                 audio_type: audio_type,
//                 has_perm: hasPerm,
//             },
//             headers: {'X-CSRFToken': csrfToken},
//             xhrFields: {withCredentials: true}
//         }).promise();
//     }
//
//
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
//
//     // بازیابی وضعیت پلیر از localStorage (در ابتدای DOMContentLoaded)
//     try {
//         const storedPlayerState = localStorage.getItem(playerStorageKey);
//         if (storedPlayerState) {
//             const parsedState = JSON.parse(storedPlayerState);
//             if (parsedState && parsedState.audio && parsedState.audio.src) {
//                 const playerContainer = isAudioPage ? document.getElementById('player-main') : document.getElementById('player-floating');
//                 if (playerContainer) {
//                     if (kplayer && kplayer.id === parsedState.audio.id) {
//                         // اگر پلیر موجود باشد و id فایل صوتی یکی باشد
//                         kplayer.currentTime = parsedState.currentTime;
//
//                         if (!hasPerm) {
//                             kplayer.destroy();
//                             kplayer = null;
//                         } else if (typeof kplayer.seek === 'function' && !isNaN(parsedState.currentTime)) {
//                             kplayer.seek(parsedState.currentTime);
//                             kplayer.on('seeked', () => {
//                                 seekedDone = true;
//                                 if (parsedState.isPlaying && hasPerm) { // بررسی hasPerm پیش از پخش
//                                     kplayer?.play();
//                                 }
//                             });
//                         } else if (!isNaN(parsedState.currentTime)) {
//                             kplayer.currentTime = parsedState.currentTime;
//                             seekedDone = true;
//                             if (parsedState.isPlaying && hasPerm) { // بررسی hasPerm پیش از پخش
//                                 kplayer?.play();
//                             }
//                         } else if (parsedState.isPlaying && hasPerm) { // بررسی hasPerm پیش از پخش
//                             kplayer?.play();
//                             seekedDone = true;
//                         }
//                     } else {
//                         // اگر پلیر موجود نباشد یا id فایل صوتی یکی نباشد، پلیر جدید ایجاد کنید
//                         if (kplayer) {
//                             kplayer.destroy();
//                             kplayer = null;
//                         }
//                         kplayer = createPlayer(playerContainer, parsedState.audio);
//                         kplayer.id = parsedState.audio.id; // تعیین id برای kplayer
//                         kplayer.on('canplay', function () {
//                             if (!seekedDone && typeof parsedState.currentTime === 'number' && !isNaN(parsedState.currentTime)) {
//                                 const currentTime = Number(parsedState.currentTime);
//                                 if (typeof kplayer.seek === 'function') {
//                                     kplayer.seek(currentTime);
//                                     kplayer.on('seeked', () => {
//                                         seekedDone = true;
//                                         if (parsedState.isPlaying && hasPerm) { // بررسی hasPerm پیش از پخش
//                                             kplayer?.play();
//                                         }
//                                     });
//                                 } else {
//                                     kplayer.currentTime = currentTime;
//                                     seekedDone = true;
//                                     if (parsedState.isPlaying && hasPerm) { // بررسی hasPerm پیش از پخش
//                                         kplayer?.play();
//                                     }
//                                 }
//                             } else if (parsedState.isPlaying && !seekedDone && hasPerm) { // بررسی hasPerm پیش از پخش
//                                 kplayer?.play();
//                                 seekedDone = true;
//                             }
//                         });
//                     }
//                 }
//             }
//         }
//     } catch (e) {
//         console.error("Error parsing player state from localStorage:", e);
//         localStorage.removeItem(playerStorageKey);
//     }
//
//
//     if (isAudioPage) {
//         let chapterIndex = (window.chapterIndexParam >= 0 && window.chapterIndexParam < window.chapter_set.length) ? window.chapterIndexParam : null;
//         let chapterName = chapterIndex !== null ? window.chapter_set[chapterIndex].name : '';
//
//         function createAudio() {
//             const csrfToken = getCSRFToken();
//             getAudioUrl(csrfToken, window.audio.id, "CCDETAIL")
//                 .then(function (audioResponse) {
//                     if (audioResponse && audioResponse.url) {
//                         let player_chapters = window.chapter_set.map((chapter, i) => ({
//                             id: chapter.id,
//                             startTime: convertToSeconds(chapter.start_time),
//                             endTime: convertToSeconds((i < window.chapter_set.length - 1) ? window.chapter_set[i + 1].start_time : "پایان فایل صوتی"),
//                             title: `${i + 1}. ${chapter.name}`,
//                         }));
//                         const audioData = {
//                             id: window.audio.id,
//                             title: window.audio.name,
//                             artist: '« خیلی ساده‌ست »',
//                             cover: coverImageUrl,
//                             chapters: player_chapters,
//                             src: audioResponse.url,
//                         };
//                         console.log('level1',audioData);
//                         kplayer = getPlayer();
//                         const playerContainer = document.getElementById('player-main');
//
//                         if (!kplayer && playerContainer) {
//                             kplayer = createPlayer(playerContainer, audioData);
//                         } else if (kplayer && kplayer.audio && kplayer.id !== audioData.id) {
//                             kplayer.destroy(); // نابود کردن پلیر قبلی
//                             kplayer = null;
//                             console.log('level2',audioData);
//                             kplayer = createPlayer(playerContainer, audioData); // ایجاد پلیر جدید
//                         } else if (kplayer && kplayer.audio && kplayer.id === audioData.id) {
//                             // پلیر از قبل برای این فایل صوتی ساخته شده، نیازی به ساخت مجدد نیست
//                         }
//
//                         kplayer?.on('chapterchange', function () {
//                             if (kplayer && kplayer.currentChapter) {
//                                 updateChapterIcons(kplayer.currentChapter.index);
//                             }
//                         });
//
//                         if (chapterIndex !== null) {
//                             console.log(kplayer);
//                             Swal.fire({
//                                 text: `مطلبی که به دنبالش هستید در قسمت ${chapterIndex + 1} با موضوع "${chapterName}" قرار دارد. مایلید فایل را از کدام قسمت گوش کنید؟`,
//                                 icon: 'info',
//                                 showCancelButton: true,
//                                 confirmButtonText: 'پخش از قسمت ' + (chapterIndex + 1),
//                                 cancelButtonText: 'پخش از ابتدا'
//                             }).then((result) => {
//                                 if (result.isConfirmed) {
//                                     myUpdateChapter(chapterIndex);
//                                     const playPromise = kplayer?.play(); // ذخیره نتیجه kplayer?.play()
//                                     if (playPromise && typeof playPromise.catch === 'function') { // بررسی Promise بودن
//                                         playPromise.catch(error => console.error("Auto-play failed: ", error));
//                                     } else if (playPromise) {
//                                         console.warn("kplayer.play() did not return a Promise, but returned: ", playPromise);
//                                     } else {
//                                         console.warn("kplayer.play() returned nothing.")
//                                     }
//                                 } else {
//                                     const playPromise = kplayer?.play(); // ذخیره نتیجه kplayer?.play()
//                                     if (playPromise && typeof playPromise.catch === 'function') { // بررسی Promise بودن
//                                         playPromise.catch(error => console.error("Auto-play failed: ", error));
//                                     } else if (playPromise) {
//                                         console.warn("kplayer.play() did not return a Promise, but returned: ", playPromise);
//                                     } else {
//                                         console.warn("kplayer.play() returned nothing.")
//                                     }
//                                 }
//                             });
//                         } else {
//                             const playPromise = kplayer?.play(); // ذخیره نتیجه kplayer?.play()
//                             if (playPromise && typeof playPromise.catch === 'function') { // بررسی Promise بودن
//                                 playPromise.catch(error => console.error("Auto-play failed: ", error));
//                             } else if (playPromise) {
//                                 console.warn("kplayer.play() did not return a Promise, but returned: ", playPromise);
//                             } else {
//                                 console.warn("kplayer.play() returned nothing.")
//                             }
//                         }
//                     } else {
//                         console.error("URL فایل صوتی دریافت نشد.");
//                         Swal.fire({icon: 'error', title: 'خطا', text: "URL فایل صوتی دریافت نشد."});
//                     }
//                 })
//                 .catch(error => {
//                     console.error("Error fetching audio URL:", error);
//                     Swal.fire({icon: 'error', title: 'خطا', text: "خطا در برقراری ارتباط با سرور."});
//                 });
//         }
//
//         createAudio();
//         $('#player-main').css({position: 'static', display: 'block'});
//         $('#player-floating').css({display: 'none'});
//
//     } else if (kplayer && !kplayer.paused) {
//         $('#player-floating').css({position: 'fixed', bottom: 0, display: 'block'});
//         $('#player-main').hide();
//     }
//
//     function myUpdateChapter(chapter_index) { // فقط chapter_index را دریافت می‌کند
//         kplayer?.updateChapter(chapter_index);
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
//     $(window).on('pagehide', function (event) {
//         savePlayerState(!kplayer.paused);
//     });
//
//     $(window).on('pageshow', function (event) {
//         const storedPlayerState = localStorage.getItem(playerStorageKey);
//         if (storedPlayerState) {
//             try {
//                 const parsedState = JSON.parse(storedPlayerState);
//                 if (parsedState.isPlaying && kplayer) {
//                     kplayer.play();
//                 }
//             } catch (error) {
//                 console.error("Error parsing player state from localStorage:", error);
//                 localStorage.removeItem(playerStorageKey);
//             }
//         }
//     });
// });