// // import {
// //     Player, Chapter, playerStorageKey,
// //     removeAudioSrc, encryptData, decryptData
// // } from '/statics/bundle.js';
// const {
//     Player, Chapter, playerStorageKey,
//     removeAudioSrc, encryptData, decryptData
// } = MyLibrary;
//
// let kplayer = null;
// let currentAudioData = null;
// let playerContainer = null; // بعداً در هر صفحه مقداردهی می‌شود
// let isAudioPage = window.location.pathname.includes('audio');
// let hasPlayed = false;
// let isPlayerVisible = false;
// let playerFloating = document.getElementById('player-floating');
//
// function handleServiceWorkerMessage(event) {
//     if (event.data.action === 'executeFunction') {
//         const functionName = event.data.functionName;
//         if (typeof window[functionName] === 'function') {
//             window[functionName](event.data.args); // ارسال آرگومان‌ها به تابع
//         } else {
//             console.error(`Function ${functionName} not found.`);
//         }
//     } else if (event.data.action === 'playerUpdated') {
//         const {audioData, currentTime, isPlaying} = event.data;
//         currentAudioData = audioData; // ذخیره اطلاعات صوتی
//         updatePlayer(audioData, {currentTime, isPlaying}, window.chapterIndexParam);
//     } else if (event.data.action === 'updateChapterIcons') {
//         updateChapterIcons(event.data.currentIndex);
//     }
// }
//
// function sendServiceWorkerMessage(message) {
//     if (navigator.serviceWorker.controller) { // بررسی وجود سرویس ورکر فعال
//         navigator.serviceWorker.controller.postMessage(message);
//     } else {
//         console.error('No active service worker found.');
//     }
// }
//
// function setPlayerContainer() {
//     playerContainer = document.getElementById('player-floating'); // شناور
//     isAudioPage = window.location.pathname.includes('audio');
//     if (isAudioPage) {
//         playerContainer = document.getElementById('player-main'); // صفحه فایل صوتی
//     }
// }
//
// function createPlayer(container, audio) {
//
//     Player.use(Chapter);
//     if (kplayer) {
//         kplayer.update({
//             // id: audio.id,
//             title: audio.name, /*persian*/
//             album: audio.title, /*english*/
//             artist: audio.artist,
//             cover: audio.cover,
//             src: audio.src,
//             chapters: audio.chapters, // چپترها جداگانه
//         });
//     } else {
//         kplayer = new Player({
//             id: audio.id,
//             container: container,
//             audio: { // فیلدهای audio به صورت جداگانه
//                 id: audio.id,
//                 title: audio.name, /*persian*/
//                 album: audio.title, /*english*/
//                 artist: audio.artist,
//                 cover: audio.cover,
//                 src: audio.src,
//                 chapters: audio.chapters, // چپترها جداگانه
//             },
//             themeColor: "#FFFFFFFF",
//             theme: 'dark',
//             fixed: {type: 'static'},
//         });
//     }
//     let lastTime = 0; // تعریف و مقداردهی اولیه lastTime
//
//     kplayer?.on('timeupdate', function () {
//         if (kplayer && kplayer.audio) {
//             const audioData = JSON.parse(localStorage.getItem(`audio_${kplayer.options.id}`));
//             if (audioData) { // بررسی وجود audioData قبل از به‌روزرسانی
//                 audioData.currentTime = kplayer.currentTime;
//                 audioData.isPlaying = !kplayer.paused;
//                 saveAudioData(audioData); // استفاده از تابع saveAudioData
//
//                 // localStorage.setItem(`audio_${kplayer.options.id}`, JSON.stringify(audioData));
//                 // localStorage.setItem('lastPlayedAudioId', kplayer.options.id);
//             }
//             //  مثلا هر 3 ثانیه یک بار یا وقتی تغییر قابل توجه باشه پیام بفرستیم
//             if (Math.abs(kplayer.currentTime - lastTime) >= 3) { // بررسی تغییر حداقل 3 ثانیه
//                 sendServiceWorkerMessage({
//                     action: 'playerStatusUpdated',
//                     playerStatus: {currentTime: kplayer.currentTime}
//                 });
//                 lastTime = kplayer.currentTime;
//             }
//         }
//     });
//
//     kplayer?.on('pause', function () {
//         if (kplayer && kplayer.audio) {
//             const audioData = JSON.parse(localStorage.getItem(`audio_${kplayer.options.id}`));
//             if (audioData) {
//                 audioData.isPlaying = false;
//                 saveAudioData(audioData); // استفاده از تابع saveAudioData
//
//             }
//             sendServiceWorkerMessage({
//                 action: 'playerStatusUpdated',
//                 playerStatus: {isPlaying: false, currentTime: kplayer.currentTime}
//             }); // ارسال پیام به Service Worker
//
//         }
//     });
//
//     kplayer?.on('play', function () {
//         if (kplayer && kplayer.audio) {
//             const audioData = JSON.parse(localStorage.getItem(`audio_${kplayer.options.id}`));
//             if (audioData) {
//                 audioData.isPlaying = true;
//                 saveAudioData(audioData); // استفاده از تابع saveAudioData
//             }
//             sendServiceWorkerMessage({
//                 action: 'playerStatusUpdated',
//                 playerStatus: {isPlaying: true, currentTime: kplayer.currentTime}
//             }); // ارسال پیام به Service Worker
//
//         }
//     });
//
//     kplayer?.on('ended', () => {
//         if (kplayer && kplayer.audio) {
//             const audioData = JSON.parse(localStorage.getItem(`audio_${kplayer.options.id}`));
//             if (audioData) {
//                 audioData.isPlaying = false; // تنظیم isPlaying به false بعد از اتمام پخش
//                 saveAudioData(audioData); // استفاده از تابع saveAudioData
//             }
//             sendServiceWorkerMessage({
//                 action: 'playerStatusUpdated',
//                 playerStatus: {isPlaying: false, currentTime: kplayer.currentTime}
//             }); // ارسال پیام به Service Worker
//
//         }
//     });
//
//     kplayer?.on('chapterchange', function () {
//         if (kplayer && kplayer.audio && kplayer.options && kplayer.options.id && kplayer.currentChapter) { // بررسی وجود kplayer.currentChapter
//             sendServiceWorkerMessage({
//                 action: 'playerStatusUpdated',
//                 playerStatus: {currentChapter: kplayer.currentChapter.index}
//             }); // ارسال index فصل به جای خود فصل
//         }
//     });
//     return kplayer;
// }
//
// function updatePlayer(audioData, parsedState, chapterIndex) {
//     setPlayerContainer();
//
//     if (isAudioPage) {
//         hidePlayer();
//     }
//     const decryptedAudioData = {...audioData, src: decryptData(audioData.src)};
//
//     if (!kplayer) {
//         kplayer = createPlayer(playerContainer, decryptedAudioData);
//         window.addEventListener('scroll', adjustScroll);
//         showPlayer();
//         setPlayer(kplayer);
//
//         if (!isAudioPage) {
//             customPlayerControls(playerContainer);
//         }
//     } else {
//         kplayer.update(decryptedAudioData);
//     }
//
//     try {
//         localStorage.setItem('lastPlayedAudioTitle', audioData.title);
//         localStorage.setItem('lastPlayedAudioId', audioData.id);
//     } catch (e) {
//         console.log("Error setting Last player id to localStorage:", e);
//     }
//
//     if (!isAudioPage && playerFloating && playerFloating.parentNode !== document.body) {
//         document.body.appendChild(playerFloating);
//     }
//
//     if (isAudioPage && window.chapter_set) {
//         window.chapter_set.forEach((chapter, index) => {
//             const chapterLink = document.getElementById(`chapter-link-${index}`);
//             if (chapterLink) {
//                 chapterLink.addEventListener('click', () => {
//                     updateCurrentChapter(index);
//                 });
//             }
//         });
//     }
//
//     kplayer?.on('chapterchange', () => {
//         if (kplayer?.currentChapter) {
//             updateChapterIcons(kplayer.currentChapter.index);
//         }
//     });
//
//     kplayer?.on('canplay', () => {
//         if (hasPlayed) return;
//         hasPlayed = true;
//
//         if (chapterIndex !== null && chapterIndex >= 0 && chapterIndex < window.chapter_set.length) {
//             const chapterName = window.chapter_set[chapterIndex].name;
//             Swal.fire({
//                 text: `مطلبی که به دنبالش هستید در قسمت ${chapterIndex + 1} با موضوع "${chapterName}" قرار دارد. مایلید فایل را از کدام قسمت گوش کنید؟`,
//                 icon: 'info',
//                 showCancelButton: true,
//                 confirmButtonText: 'پخش از قسمت ' + (chapterIndex + 1),
//                 cancelButtonText: 'پخش از ابتدا'
//             }).then((result) => {
//                 if (result.isConfirmed) {
//                     updateCurrentChapter(chapterIndex);
//                     const playPromise = kplayer?.play();
//                     if (playPromise && typeof playPromise.catch === 'function') {
//                         playPromise.catch(error => console.error("Auto-play failed: ", error));
//                     }
//                 } else {
//                     const playPromise = kplayer?.play();
//                     if (playPromise && typeof playPromise.catch === 'function') {
//                         playPromise.catch(error => console.error("Auto-play failed: ", error));
//                     }
//                 }
//             });
//         } else if (parsedState) {
//             waitForPlayerInitialization().then(() => {
//                 setPlayerCurrentTime(parsedState.currentTime, parsedState.isPlaying);
//             });
//         }
//     });
// }
//
// function setPlayer(player) {
//     kplayer = player;
// }
//
// function getPlayer() {
//     return kplayer;
// }
//
// function saveAudioData(isPlaying = null) {
//     if (kplayer && currentAudioData) {
//         currentAudioData.currentTime = kplayer.currentTime;
//         currentAudioData.isPlaying = isPlaying !== null ? isPlaying : !kplayer.paused;
//         localStorage.setItem(`audio_${currentAudioData.id}`, JSON.stringify(currentAudioData));
//         localStorage.setItem('lastPlayedAudioId', currentAudioData.id); // ذخیره شناسه فایل صوتی آخرین پخش شده
//         sendServiceWorkerMessage({action: 'updatePlayerData', audioData: currentAudioData});
//     }
// }
//
// function loadAudioData() {
//     const lastPlayedAudioId = localStorage.getItem('lastPlayedAudioId');
//     if (lastPlayedAudioId) {
//         return JSON.parse(localStorage.getItem(`audio_${lastPlayedAudioId}`));
//     }
//     return null;
// }
//
//
// function customPlayerControls(playerContainer) {
//     const closeButton = document.createElement('button');
//     closeButton.id = 'close-player';
//     closeButton.className = 'close-btn';
//     closeButton.innerHTML = '×';
//
//     closeButton.addEventListener('click', function () {
//         saveAudioData(false);
//         if (kplayer) {
//             kplayer.pause();
//             kplayer.destroy();
//         }
//         hidePlayer();
//     });
//
//     playerContainer.appendChild(closeButton);
// }
//
// function showPlayer() {
//     if (!isAudioPage && !isPlayerVisible && playerFloating) {
//         playerFloating.classList.add('show');
//         isPlayerVisible = true;
//         adjustPadding();
//         adjustScroll();
//     }
// }
//
// function hidePlayer() {
//     if (!isAudioPage && isPlayerVisible && playerFloating) {
//         playerFloating.classList.remove('show');
//         isPlayerVisible = false;
//         adjustPadding();
//     }
// }
//
// function adjustScroll() {
//     if (!isAudioPage && isPlayerVisible && playerFloating) {
//         const playerHeight = playerFloating.offsetHeight;
//         const windowHeight = window.innerHeight;
//         const documentHeight = document.documentElement.scrollHeight;
//         const scrollPosition = window.pageYOffset;
//
//         if (scrollPosition + windowHeight >= documentHeight) {
//             window.scrollTo(0, documentHeight - windowHeight + playerHeight);
//         }
//     }
// }
//
// function adjustPadding() {
//     if (!isAudioPage && playerFloating && isPlayerVisible) {
//         const playerHeight = playerFloating.offsetHeight;
//         document.body.style.paddingBottom = playerHeight + 'px';
//     } else {
//         document.body.style.paddingBottom = '0';
//     }
// }
//
// function convertToSeconds(time) {
//     if (typeof time === 'number') return time;
//     if (typeof time !== 'string') return 0;
//     const parts = time.split(':').reverse();
//     let seconds = parseInt(parts[0] || 0);
//     seconds += parseInt(parts[1] || 0) * 60;
//     seconds += parseInt(parts[2] || 0) * 3600;
//     return seconds;
// }
//
// function pauseAnimation() {
//     $('.equalizer').css('animation-play-state', 'paused');
// }
//
// function playAnimation() {
//     $('.equalizer').css('animation-play-state', 'running');
// }
//
// function updateCurrentChapter(chapterIndex) {
//     if (kplayer) {
//         kplayer.updateChapter(chapterIndex);
//         updateChapterIcons(chapterIndex);
//     } else {
//         console.error("Player is not initialized yet.");
//     }
// }
//
// function updateChapterIcons(currentIndex) {
//     $('.equalizer').hide();
//     $('.ti-music').show();
//     const currentIcon = $(`#chapter-icon-${currentIndex}`);
//     const currentEqualizer = $(`#equalizer-${currentIndex}`);
//     if (currentIcon.length && currentEqualizer.length) {
//         currentIcon.hide();
//         currentEqualizer.show();
//     }
// }
//
// function waitForPlayerInitialization() {
//     return new Promise(resolve => {
//         const checkInterval = setInterval(() => {
//             if (kplayer) {
//                 clearInterval(checkInterval);
//                 resolve();
//             }
//         }, 100);
//     });
// }
//
// function setPlayerCurrentTime(time, isPlaying) {
//     if (kplayer) {
//         kplayer.seek(time);
//         let hasSeeked = false; // متغیر برای بررسی اینکه آیا seek شده است
//         const handler = function() {
//             if (!hasSeeked) {
//                 hasSeeked = true; // علامت گذاری به عنوان اجرا شده
//                 let playPromise;
//                 if (isPlaying) {
//                     playPromise = kplayer.play();
//                 } else {
//                     playPromise = kplayer.pause();
//                 }
//                 if (playPromise && typeof playPromise.catch === 'function') {
//                     playPromise.catch(error => console.error("Auto-play failed: ", error));
//                 }
//             }
//         };
//         kplayer.on('seeked', handler);
//     } else {
//         console.error("kplayer not initialized");
//     }
// }
//
//
// // ******* بخش مهم اضافه شده *******
// navigator.serviceWorker.addEventListener('message', event => {
//     if (event.data.action === 'updateChapterIcons') {
//         updateChapterIcons(event.data.currentIndex);
//     } else if (event.data.action === 'playerUpdated') {
//         const {audioData, currentTime, isPlaying} = event.data;
//         currentAudioData = audioData;
//         updatePlayer(audioData, {currentTime, isPlaying}, window.chapterIndexParam);
//     } else if (event.data.action === 'playerStatusUpdated') {
//         const {currentTime, isPlaying} = event.data.playerStatus;
//         setPlayerCurrentTime(currentTime, isPlaying);
//     }
// });
//
//
// document.addEventListener('visibilitychange', () => {
//     if (document.hidden && kplayer && !kplayer.paused) {
//         saveAudioData();
//     }
// });
//
// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }
//
// function getCSRFToken() {
//     return getCookie('csrftoken');
// }
//
// function getAudioUrl(csrfToken, audio_id, audio_type) {
//     return $.ajax({
//         url: audioGetUrl,
//         method: "POST",
//         data: {
//             csrfToken: csrfToken,
//             audio_id: audio_id,
//             audio_type: audio_type,
//             has_perm: hasPerm,
//         },
//         headers: {'X-CSRFToken': csrfToken},
//         xhrFields: {withCredentials: true}
//     }).promise();
// }
//
// function createAudio(chapterIndex, parsedState) {
//     const csrfToken = getCSRFToken();
//     getAudioUrl(csrfToken, window.audio.id, "CCDETAIL")
//         .done(function (audioResponse) {
//             if (audioResponse && audioResponse.url) {
//                 const lastChapterIndex = window.chapter_set.length - 1;
//                 let player_chapters = window.chapter_set.map((chapter, i) => ({
//                     id: i,
//                     startTime: convertToSeconds(chapter.start_time),
//                     endTime: i === lastChapterIndex ? convertToSeconds(window.audio_duration) : convertToSeconds(window.chapter_set[i + 1].start_time),
//                     title: `${i + 1}. ${chapter.name}`,
//                 }));
//                 const encryptedSrc = encryptData(audioResponse.url);
//
//                 currentAudioData = {
//                     id: window.audio.id,
//                     name: window.audio.name,
//                     title: window.audio.title,
//                     artist: '« خیلی ساده‌ست »',
//                     cover: coverImageUrl,
//                     chapters: player_chapters,
//                     src: encryptedSrc,
//                 };
//                 updatePlayer(currentAudioData, parsedState, chapterIndex);
//             } else {
//                 console.error("URL فایل صوتی دریافت نشد.");
//                 Swal.fire({icon: 'error', title: 'خطا', text: "URL فایل صوتی دریافت نشد."});
//             }
//         })
//         .fail(function (error) {
//             console.error("Error fetching audio URL:", error);
//             Swal.fire({icon: 'error', title: 'خطا', text: "خطا در برقراری ارتباط با سرور."});
//         });
// }
//
// // تابع راه‌انداز
// function initializePlayer() {
//     setPlayerContainer();
//
//     if (isAudioPage && hasPerm && window.audio && window.audio.id) { // بررسی وجود window.audio و window.audio.id
//         createAudio(window.chapterIndexParam, null); // فراخوانی createAudio در صفحه فایل صوتی
//     } else if (hasPerm) {
//         const lastAudioData = loadAudioData();
//         if (lastAudioData) {
//             updatePlayer(lastAudioData, {
//                 currentTime: lastAudioData.currentTime,
//                 isPlaying: lastAudioData.isPlaying
//             }, window.chapterIndexParam);
//         }
//     }
// }
//
// // اجرای تابع راه‌انداز در زمان لود شدن صفحه
// document.addEventListener('DOMContentLoaded', initializePlayer);
