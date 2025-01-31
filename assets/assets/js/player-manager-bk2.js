// document.addEventListener('DOMContentLoaded', function () {
//         const {
//             createPlayer, getPlayer, setPlayer, savePlayerState,
//             playerStorageKey, removeAudioSrc, encryptData, decryptData
//         } = MyLibrary;
//         // const playerStorageKey = 'kplayer_state';
//         const isAudioPage = window.location.pathname.includes('audio');
//         let seekedDone = false;
//
//         let kplayer = getPlayer();
//
//         function getCookie(name) {
//             let cookieValue = null;
//             if (document.cookie && document.cookie !== '') {
//                 const cookies = document.cookie.split(';');
//                 for (let i = 0; i < cookies.length; i++) {
//                     const cookie = cookies[i].trim();
//                     if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                         break;
//                     }
//                 }
//             }
//             return cookieValue;
//         }
//
//         function getCSRFToken() {
//             return getCookie('csrftoken');
//         }
//
//         function getAudioUrl(csrfToken, audio_id, audio_type) {
//             // دیگر نیازی به خواندن از HTML نیست
//             return $.ajax({
//                 url: audioGetUrl, // از متغیر سراسری audioGetUrl استفاده میکنیم
//                 method: "POST",
//                 data: {
//                     csrfToken: csrfToken,
//                     audio_id: audio_id,
//                     audio_type: audio_type,
//                     has_perm: hasPerm,
//                 },
//                 headers: {'X-CSRFToken': csrfToken},
//                 xhrFields: {withCredentials: true}
//             }).promise();
//         }
//
//
//         function convertToSeconds(time) {
//             const [minutes, seconds] = time.split(':').map(Number);
//             return minutes * 60 + seconds;
//         }
//
//         function pauseAnimation() {
//             $('.equalizer').css('animation-play-state', 'paused');
//         }
//
//         function playAnimation() {
//             $('.equalizer').css('animation-play-state', 'running');
//         }
//
//         function checkEverything() {
//             if (hasPerm) {
//                 let kplayer = getPlayer();
//                 if (isAudioPage) {
//                     let chapterIndex = (window.chapterIndexParam >= 0 && window.chapterIndexParam < window.chapter_set.length) ? window.chapterIndexParam : null;
//                     let chapterName = chapterIndex !== null ? window.chapter_set[chapterIndex].name : '';
//
//                     try {
//                         const storedPlayerState = localStorage.getItem(playerStorageKey);
//                         if (storedPlayerState) {
//                             const parsedState = JSON.parse(storedPlayerState);
//                             if (parsedState && parsedState.audio && parsedState.audio.src) {
//                                 parsedState.audio.src = decryptData(parsedState.audio.src); // رمزگشایی آدرس
//                                 const playerContainer = document.getElementById('player-main');
//                                 if (playerContainer) {
//                                     let kplayer = getPlayer();
//                                     if (kplayer && kplayer.options.id === parsedState.audio.id) {
//                                         // اگر پلیر موجود باشد و id فایل صوتی یکی باشد
//                                         if (chapterIndex !== null) {
//                                             Swal.fire({
//                                                 text: `مطلبی که به دنبالش هستید در قسمت ${chapterIndex + 1} با موضوع "${chapterName}" قرار دارد. مایلید فایل را از کدام قسمت گوش کنید؟`,
//                                                 icon: 'info',
//                                                 showCancelButton: true,
//                                                 confirmButtonText: 'پخش از قسمت ' + (chapterIndex + 1),
//                                                 cancelButtonText: 'پخش از ابتدا'
//                                             }).then((result) => {
//                                                 if (result.isConfirmed) {
//                                                     myUpdateChapter(chapterIndex);
//                                                     const playPromise = kplayer?.play();
//                                                     if (playPromise && typeof playPromise.catch === 'function') {
//                                                         playPromise.catch(error => console.error("Auto-play failed: ", error));
//                                                     }
//                                                 } else {
//                                                     const playPromise = kplayer?.play();
//                                                     if (playPromise && typeof playPromise.catch === 'function') {
//                                                         playPromise.catch(error => console.error("Auto-play failed: ", error));
//                                                     }
//                                                 }
//                                             });
//                                         } else {
//                                             setPlayerCurrentTime(parsedState.currentTime, parsedState.isPlaying);
//                                         }
//                                     } else {
//                                         // اگر id یکی نبود یا پلیر موجود نباشد، createAudio
//                                         createAudio(chapterIndex, parsedState);
//                                         // if (chapterIndex !== null) {
//                                         //     Swal.fire({
//                                         //         text: `مطلبی که به دنبالش هستید در قسمت ${chapterIndex + 1} با موضوع "${chapterName}" قرار دارد. مایلید فایل را از کدام قسمت گوش کنید؟`,
//                                         //         icon: 'info',
//                                         //         showCancelButton: true,
//                                         //         confirmButtonText: 'پخش از قسمت ' + (chapterIndex + 1),
//                                         //         cancelButtonText: 'پخش از ابتدا'
//                                         //     }).then((result) => {
//                                         //         if (result.isConfirmed) {
//                                         //             myUpdateChapter(chapterIndex);
//                                         //             let kplayer = getPlayer();
//                                         //             const playPromise = kplayer?.play();
//                                         //             if (playPromise && typeof playPromise.catch === 'function') {
//                                         //                 playPromise.catch(error => console.error("Auto-play failed: ", error));
//                                         //             }
//                                         //         } else {
//                                         //             let kplayer = getPlayer();
//                                         //             const playPromise = kplayer?.play();
//                                         //             if (playPromise && typeof playPromise.catch === 'function') {
//                                         //                 playPromise.catch(error => console.error("Auto-play failed: ", error));
//                                         //             }
//                                         //         }
//                                         //     });
//                                         // } else {
//                                         //     setPlayerCurrentTime(parsedState.currentTime, parsedState.isPlaying);
//                                         // }
//                                     }
//                                 }
//                             }
//                         } else {
//                             // اگر چیزی ذخیره نبود، createAudio
//                             createAudio(chapterIndex, null);
//                             // if (chapterIndex !== null) {
//                             //     Swal.fire({
//                             //         text: `مطلبی که به دنبالش هستید در قسمت ${chapterIndex + 1} با موضوع "${chapterName}" قرار دارد. مایلید فایل را از کدام قسمت گوش کنید؟`,
//                             //         icon: 'info',
//                             //         showCancelButton: true,
//                             //         confirmButtonText: 'پخش از قسمت ' + (chapterIndex + 1),
//                             //         cancelButtonText: 'پخش از ابتدا'
//                             //     }).then((result) => {
//                             //         if (result.isConfirmed) {
//                             //             myUpdateChapter(chapterIndex);
//                             //             let kplayer = getPlayer();
//                             //             const playPromise = kplayer?.play();
//                             //             if (playPromise && typeof playPromise.catch === 'function') {
//                             //                 playPromise.catch(error => console.error("Auto-play failed: ", error));
//                             //             }
//                             //         } else {
//                             //             let kplayer = getPlayer();
//                             //             const playPromise = kplayer?.play();
//                             //             if (playPromise && typeof playPromise.catch === 'function') {
//                             //                 playPromise.catch(error => console.error("Auto-play failed: ", error));
//                             //             }
//                             //         }
//                             //     });
//                             // } else {
//                             //     setPlayerCurrentTime(parsedState.currentTime, parsedState.isPlaying);
//                             // }
//                         }
//                     } catch (e) {
//                         console.error("Error parsing player state from localStorage:", e);
//                         localStorage.removeItem(playerStorageKey);
//                     }
//
//                 } else {
//                     // مسیر برای سایر صفحات
//                     try {
//                         const storedPlayerState = localStorage.getItem(playerStorageKey);
//                         console.log('try ', storedPlayerState);
//                         if (storedPlayerState) {
//                             const parsedState = JSON.parse(storedPlayerState);
//                             if (parsedState && parsedState.audio && parsedState.audio.src) {
//                                 parsedState.audio.src = decryptData(parsedState.audio.src); // رمزگشایی آدرس
//                                 const playerContainer = document.getElementById('player-floating');
//                                 if (playerContainer) {
//                                     let kplayer = getPlayer();
//                                     if (kplayer && kplayer.options.id === parsedState.audio.id) {
//                                         setPlayerCurrentTime(parsedState.currentTime, parsedState.isPlaying);
//                                     } else {
//                                         console.log('stored currentTime2 ', parsedState.currentTime);
//                                         // اگر پلیر موجود نباشد یا id فایل صوتی یکی نباشد، پلیر جدید ایجاد کنید
//                                         const csrfToken = getCSRFToken();
//                                         // استفاده از done و fail به جای then و catch
//                                         getAudioUrl(csrfToken, parsedState.audio.id, "CCDETAIL")
//                                             .done(function (audioResponse) {
//                                                 if (audioResponse && audioResponse.url) {
//                                                     parsedState.audio.src = audioResponse.url;
//                                                     let kplayer = getPlayer();
//                                                     if (kplayer) {
//                                                         kplayer.destroy();
//                                                         kplayer = null;
//                                                     }
//                                                     kplayer = createPlayer(playerContainer, parsedState.audio);
//                                                     setPlayer(kplayer); // به‌روزرسانی kplayer
//                                                     kplayer.options.id = parsedState.audio.id; // تعیین id برای kplayer
//                                                     setPlayerCurrentTime(parsedState.currentTime, parsedState.isPlaying);
//                                                 }
//                                             })
//                                             .fail(function (error) {
//                                                 console.error("Error fetching audio URL:", error);
//                                                 Swal.fire({
//                                                     icon: 'error',
//                                                     title: 'خطا',
//                                                     text: "خطا در برقراری ارتباط با سرور."
//                                                 });
//                                             });
//                                     }
//                                 }
//                             }
//                         }
//                     } catch (e) {
//                         console.error("Error parsing player state from localStorage:", e);
//                         localStorage.removeItem(playerStorageKey);
//                     }
//                 }
//             } else {
//                 // اگر hasPerm ندارد، فقط آدرس‌ها را از storage حذف کنیم
//                 removeAudioSrc();
//             }
//             setPlayer(kplayer); // به‌روزرسانی kplayer
//         }
//
//
//         function createAudio(chapterIndex, parsedState) {
//             const csrfToken = getCSRFToken();
//             getAudioUrl(csrfToken, window.audio.id, "CCDETAIL")
//                 .done(function (audioResponse) {
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
//                         let kplayer = getPlayer();
//                         const playerContainer = document.getElementById('player-main');
//
//                         if (!kplayer && playerContainer) {
//                             kplayer = createPlayer(playerContainer, audioData);
//                             setPlayer(kplayer);
//                         } else if (kplayer && kplayer.audio && kplayer.options.id !== audioData.id) {
//                             kplayer.destroy(); // نابود کردن پلیر قبلی
//                             kplayer = null;
//                             kplayer = createPlayer(playerContainer, audioData); // ایجاد پلیر جدید
//                             setPlayer(kplayer);
//                         } else if (kplayer && kplayer.audio && kplayer.options.id === audioData.id) {
//                             // پلیر از قبل برای این فایل صوتی ساخته شده، نیازی به ساخت مجدد نیست
//                             setPlayer(kplayer);
//                         }
//                         kplayer?.on('chapterchange', function () {
//                             if (kplayer && kplayer.currentChapter) {
//                                 updateChapterIcons(kplayer.currentChapter.index);
//                                 setPlayer(kplayer);
//                             }
//                         });
//                         kplayer?.on('canplay', function () {
//                             if (chapterIndex !== null) {
//                                 Swal.fire({
//                                     text: `مطلبی که به دنبالش هستید در قسمت ${chapterIndex + 1} با موضوع "${chapterName}" قرار دارد. مایلید فایل را از کدام قسمت گوش کنید؟`,
//                                     icon: 'info',
//                                     showCancelButton: true,
//                                     confirmButtonText: 'پخش از قسمت ' + (chapterIndex + 1),
//                                     cancelButtonText: 'پخش از ابتدا'
//                                 }).then((result) => {
//                                     if (result.isConfirmed) {
//                                         myUpdateChapter(chapterIndex);
//                                         let kplayer = getPlayer();
//                                         const playPromise = kplayer?.play();
//                                         if (playPromise && typeof playPromise.catch === 'function') {
//                                             playPromise.catch(error => console.error("Auto-play failed: ", error));
//                                         }
//                                     } else {
//                                         let kplayer = getPlayer();
//                                         const playPromise = kplayer?.play();
//                                         if (playPromise && typeof playPromise.catch === 'function') {
//                                             playPromise.catch(error => console.error("Auto-play failed: ", error));
//                                         }
//                                     }
//                                 });
//                             } else {
//                                 if (parsedState){
//                                     setPlayerCurrentTime(parsedState.currentTime, parsedState.isPlaying);
//                                 }
//                             }
//                         });
//                     } else {
//                         console.error("URL فایل صوتی دریافت نشد.");
//                         Swal.fire({icon: 'error', title: 'خطا', text: "URL فایل صوتی دریافت نشد."});
//                     }
//                 })
//                 .fail(function (error) {
//                     console.error("Error fetching audio URL:", error);
//                     Swal.fire({icon: 'error', title: 'خطا', text: "خطا در برقراری ارتباط با سرور."});
//                 });
//
//         }
//
//
//         function myUpdateChapter(chapter_index) { // فقط chapter_index را دریافت می‌کند
//             let kplayer = getPlayer();
//             kplayer?.updateChapter(chapter_index);
//             updateChapterIcons(chapter_index);
//             setPlayer(kplayer);
//         }
//
//         function updateChapterIcons(currentIndex) {
//             $('.equalizer').hide();
//             $('.ti-music').show();
//             const currentIcon = $(`#chapter-icon-${currentIndex}`);
//             const currentEqualizer = $(`#equalizer-${currentIndex}`);
//             if (currentIcon.length && currentEqualizer.length) {
//                 currentIcon.hide();
//                 currentEqualizer.show();
//             }
//         }
//
//         function setPlayerCurrentTime(time, isPlaying) {
//             let kplayer = getPlayer();
//             let seekedDone = false;
//             if (kplayer) {
//                 if (typeof kplayer.seek === 'function') {
//                     kplayer.seek(time);
//                     kplayer.on('seeked', function handler() {
//                         if (!seekedDone) {
//                             seekedDone = true;
//                             if (isPlaying) {
//                                 const playPromise = kplayer.play();
//                                 if (playPromise && typeof playPromise.catch === 'function') {
//                                     playPromise.catch(error => console.error("Auto-play failed: ", error));
//                                 }
//                             }
//                         }
//                     });
//                 } else {
//                     kplayer.currentTime = time;
//                     if (isPlaying && !seekedDone) {
//                         seekedDone = true;
//                         const playPromise = kplayer.play();
//                         if (playPromise && typeof playPromise.catch === 'function') {
//                             playPromise.catch(error => console.error("Auto-play failed: ", error));
//                         }
//                     }
//                 }
//             } else {
//                 console.error("kplayer not initialized");
//             }
//             setPlayer(kplayer);
//         }
//
//         // function setPlayerCurrentTime(time, isPlaying) {
//         //     let kplayer = getPlayer();
//         //     let seekedDone = false;
//         //
//         //     if (kplayer) {
//         //         kplayer.on('canplay', function () {
//         //             if (!seekedDone && typeof time === 'number' && !isNaN(time)) {
//         //                 const currentTime = Number(time);
//         //                 if (typeof kplayer.seek === 'function') {
//         //                     kplayer.seek(currentTime);
//         //                     kplayer.on('seeked', function handler() {
//         //                         if (!seekedDone) {
//         //                             seekedDone = true;
//         //                             if (isPlaying) {
//         //                                 const playPromise = kplayer.play();
//         //                                 if (playPromise && typeof playPromise.catch === 'function') {
//         //                                     playPromise.catch(error => console.error("Auto-play failed: ", error));
//         //                                 }
//         //                             }
//         //                         }
//         //                     });
//         //                 } else {
//         //                     kplayer.currentTime = currentTime;
//         //                     seekedDone = true;
//         //                     if (isPlaying) {
//         //                         const playPromise = kplayer.play();
//         //                         if (playPromise && typeof playPromise.catch === 'function') {
//         //                             playPromise.catch(error => console.error("Auto-play failed: ", error));
//         //                         }
//         //                     }
//         //                 }
//         //             } else if (isPlaying && !seekedDone) {
//         //                 kplayer.play();
//         //                 seekedDone = true;
//         //             }
//         //         });
//         //     } else {
//         //         console.error("kplayer not initialized");
//         //     }
//         //     setPlayer(kplayer);
//         // }
//
//
//         function setupPageHideShowEvents() {
//             $(window).on('pagehide', function (event) {
//                 let kplayer = getPlayer();
//                 console.log('Page is hiding. kplayer:', kplayer);
//                 if (kplayer) {
//                     savePlayerState(!kplayer.paused);
//                 } else {
//                     checkEverything();
//                 }
//             });
//             $(window).on('pageshow', function (event) {
//                 let kplayer = getPlayer();
//                 console.log('Page is showing. kplayer:', kplayer);
//                 checkEverything();
//                 kplayer = getPlayer();
//                 console.log('Page is showed. kplayer:', kplayer);
//                 // const storedPlayerState = localStorage.getItem(playerStorageKey);
//                 // console.log('pageshow ', storedPlayerState);
//                 // if (storedPlayerState) {
//                 //     try {
//                 //         const parsedState = JSON.parse(storedPlayerState);
//                 //         let kplayer = getPlayer();
//                 //         if (parsedState && kplayer) {
//                 //             kplayer.currentTime = parsedState.currentTime || 0; // آپدیت کردن تایم پلیر
//                 //             if (parsedState.isPlaying) {
//                 //                 const playPromise = kplayer.play();
//                 //                 if (playPromise && typeof playPromise.catch === 'function') {
//                 //                     playPromise.catch(error => console.error("Auto-play failed: ", error));
//                 //                 }
//                 //             }
//                 //         }
//                 //     } catch (error) {
//                 //         console.error("Error parsing player state from localStorage:", error);
//                 //         localStorage.removeItem(playerStorageKey);
//                 //     }
//                 // }
//             });
//         }
//
//         setupPageHideShowEvents();
//     }
// )
// ;