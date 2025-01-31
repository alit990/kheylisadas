// let currentAudioData;
// let currentAudioId;
// let kplayer;
// document.addEventListener('DOMContentLoaded', function () {
//     const {
//         createPlayer, getPlayer, setPlayer, saveAudioData,
//         playerStorageKey, removeAudioSrc, encryptData, decryptData
//     } = MyLibrary;
//     const isAudioPage = window.location.pathname.includes('audio');
//
//     let hasPlayed;
//     let isPlayerVisible;
//
//
//     // for player-floating scroll -----------start
//     const playerFloating = document.getElementById('player-floating');
//     const closePlayerButton = document.getElementById('close-player');
//
//     function customPlayerControls(playerContainer) {
//         const closeButton = document.createElement('button');
//         closeButton.id = 'close-player';
//         closeButton.className = 'close-btn';
//         closeButton.innerHTML = '×';
//
//         // اضافه‌کردن رویداد کلیک برای دکمه بستن
//         closeButton.addEventListener('click', function () {
//             const kplayer = getPlayer();
//             // saveAudioData(currentAudioData);
//             const audioData = JSON.parse(localStorage.getItem(`audio_${currentAudioId}`));
//             if (audioData) { // بررسی وجود audioData قبل از به‌روزرسانی
//                 audioData.currentTime = kplayer.currentTime;
//                 audioData.isPlaying = !kplayer.paused;
//                 // * saveAudioData(audioData); // استفاده از تابع saveAudioData
//             }
//             if (kplayer) {
//                 kplayer.pause(); // متوقف کردن پلیر قبل از نابود کردن
//                 kplayer.destroy(); // نابود کردن پلیر
//             }
//             hidePlayer();
//         });
//
//         // افزودن دکمه به کانتینر پلیر
//         playerContainer.appendChild(closeButton);
//     }
//
//     function showPlayer() {
//         if (!isAudioPage && !isPlayerVisible && playerFloating) {
//             playerFloating.classList.add('show');
//             isPlayerVisible = true;
//             adjustPadding(); // تنظیم padding بلافاصله بعد از نمایش پلیر
//             adjustScroll();
//         }
//     }
//
//     function hidePlayer() {
//         if (!isAudioPage && isPlayerVisible && playerFloating) {
//             playerFloating.classList.remove('show');
//             isPlayerVisible = false;
//             adjustPadding(); // حذف padding بلافاصله بعد از پنهان شدن پلیر
//         }
//     }
//
//     function adjustScroll() {
//         if (!isAudioPage && isPlayerVisible && playerFloating) {
//             const playerHeight = playerFloating.offsetHeight;
//             const windowHeight = window.innerHeight;
//             const documentHeight = document.documentElement.scrollHeight;
//             const scrollPosition = window.pageYOffset;
//
//             if (scrollPosition + windowHeight >= documentHeight) {
//                 window.scrollTo(0, documentHeight - windowHeight + playerHeight);
//             }
//         }
//     }
//
//     function adjustPadding() {
//         if (!isAudioPage && playerFloating && isPlayerVisible) { // بررسی وجود playerFloating و نمایش آن
//             const playerHeight = playerFloating.offsetHeight;
//             document.body.style.paddingBottom = playerHeight + 'px';
//         } else {
//             document.body.style.paddingBottom = '0';
//         }
//     }
//
//     // اضافه‌کردن رویداد کلیک برای دکمه بستن
//     if (closePlayerButton) {
//         closePlayerButton.addEventListener('click', function () {
//             const kplayer = getPlayer();
//             //saveAudioData(); // ذخیره وضعیت پلیر todo: check and save state
//             // saveAudioData(currentAudioData); // ذخیره اطلاعات فایل صوتی قبل از ایجاد پلیر
//             const audioData = JSON.parse(localStorage.getItem(`audio_${kplayer.options.id}`));
//             if (audioData) { // بررسی وجود audioData قبل از به‌روزرسانی
//                 audioData.currentTime = kplayer.currentTime;
//                 audioData.isPlaying = !kplayer.paused;
//                 saveAudioData(audioData); // استفاده از تابع saveAudioData
//             }
//             if (kplayer) {
//                 kplayer.pause(); // متوقف کردن پلیر قبل از نابود کردن
//                 kplayer.destroy(); // نابود کردن پلیر
//             }
//             hidePlayer();
//         });
//     }
//
//
//     // end ===================
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
//     function convertToSeconds(time) {
//         if (typeof time === 'number') return time; // اگر عدد بود، همان را برگردان
//         if (typeof time !== 'string') return 0; // اگر رشته نبود، 0 برگردان
//         const parts = time.split(':').reverse(); // جدا کردن اجزا و برعکس کردن آنها
//         let seconds = parseInt(parts[0] || 0); // ثانیه
//         seconds += parseInt(parts[1] || 0) * 60; // دقیقه
//         seconds += parseInt(parts[2] || 0) * 3600; // ساعت
//         return seconds;
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
//     function updatePlayer(audioData, parsedState, chapterIndex) {
//         if (isAudioPage) {
//             hidePlayer(); // مخفی کردن پلیر شناور در صفحه فایل صوتی
//         }
//         const playerContainer = isAudioPage ? document.getElementById('player-main') : document.getElementById('player-floating');
//         if (!playerContainer) return;
//         const lastPlayedAudioTitle = localStorage.getItem('lastPlayedAudioTitle');
//         if (!kplayer) {
//             kplayer = createPlayer(playerContainer, audioData);
//             window.addEventListener('scroll', adjustScroll); // اضافه کردن listener اسکرول
//             showPlayer(); // نمایش پلیر شناور
//             setPlayer(kplayer);
//
//             if (!isAudioPage) {
//                 customPlayerControls(playerContainer); // فراخوانی تابع اضافه‌کردن دکمه‌های سفارشی
//             }
//             // } else if (window.audio?.id && kplayer.options.id !== window.audio.id) {
//         } else if (window.audio && kplayer.options.audio.album !== window.audio.title) {
//
//             kplayer.destroy();
//             kplayer = createPlayer(playerContainer, audioData);
//             window.addEventListener('scroll', adjustScroll); // اضافه کردن listener اسکرول
//             showPlayer(); // نمایش پلیر شناور
//             setPlayer(kplayer);
//
//             if (!isAudioPage) {
//                 customPlayerControls(playerContainer); // فراخوانی تابع اضافه‌کردن دکمه‌های سفارشی
//             }
//         } else if (lastPlayedAudioTitle !== kplayer.options.audio.album) {
//
//             if (!isAudioPage) {
//                 console.log('before', kplayer);
//                 if (kplayer) {
//                     // kplayer.destroy();
//                 }
//
//                 console.log('after', kplayer);
//                 kplayer = createPlayer(playerContainer, audioData);
//                 // kplayer = createPlayer(playerContainer, audioData);
//                 window.addEventListener('scroll', adjustScroll); // اضافه کردن listener اسکرول
//                 setPlayer(kplayer);
//                 showPlayer(); // نمایش پلیر شناور
//                 customPlayerControls(playerContainer); // فراخوانی تابع اضافه‌کردن دکمه‌های سفارشی
//             }
//         }
//         try {
//             if (isAudioPage) {
//                 currentAudioId = window.audio.id;
//                 localStorage.setItem('lastPlayedAudioTitle', window.audio.title);
//                 localStorage.setItem('lastPlayedAudioId', window.audio.id);
//             } else {
//                 currentAudioId = audioData.id;
//                 localStorage.setItem('lastPlayedAudioTitle', audioData.title);
//                 localStorage.setItem('lastPlayedAudioId', audioData.id);
//             }
//         } catch (e) {
//             // console.error("Error getting Last player id from localStorage:", e);
//             console.log("Error setting Last player id to localStorage:", e);
//
//         }
//         if (!isAudioPage) {
//             // انتقال پلیر به body بعد از ایجاد یا به‌روزرسانی
//             const playerFloating = document.getElementById('player-floating');
//             if (playerFloating && playerFloating.parentNode !== document.body) { // بررسی برای جلوگیری از انتقال مجدد
//                 document.body.appendChild(playerFloating);
//             }
//         }
//         if (isAudioPage && window.chapter_set) { // بررسی isAudioPage
//             window.chapter_set.forEach((chapter, index) => {
//                 const chapterLink = document.getElementById(`chapter-link-${index}`);
//                 if (chapterLink) {
//                     chapterLink.addEventListener('click', () => {
//                         updateCurrentChapter(index);
//                     });
//                 }
//             });
//         }
//         kplayer?.on('chapterchange', () => {
//             if (kplayer?.currentChapter) {
//                 updateChapterIcons(kplayer.currentChapter.index);
//             }
//         });
//         kplayer?.on('canplay', () => {
//             if (hasPlayed) return; // اگر قبلاً اجرا شده، خارج شویم
//             hasPlayed = true; // flag را true می‌کنیم
//             let chapterIndex = (window.chapterIndexParam >= 0 && window.chapterIndexParam < window.chapter_set.length) ? window.chapterIndexParam : null;
//             let chapterName = chapterIndex !== null ? window.chapter_set[chapterIndex].name : '';
//             if (chapterIndex !== null) {
//                 Swal.fire({
//                     text: `مطلبی که به دنبالش هستید در قسمت ${chapterIndex + 1} با موضوع "${chapterName}" قرار دارد. مایلید فایل را از کدام قسمت گوش کنید؟`,
//                     icon: 'info',
//                     showCancelButton: true,
//                     confirmButtonText: 'پخش از قسمت ' + (chapterIndex + 1),
//                     cancelButtonText: 'پخش از ابتدا'
//                 }).then((result) => {
//                     if (result.isConfirmed) {
//                         myUpdateChapter(chapterIndex);
//                         const playPromise = kplayer?.play();
//                         if (playPromise && typeof playPromise.catch === 'function') {
//                             playPromise.catch(error => console.error("Auto-play failed: ", error));
//                         }
//                     } else {
//                         const playPromise = kplayer?.play();
//                         if (playPromise && typeof playPromise.catch === 'function') {
//                             playPromise.catch(error => console.error("Auto-play failed: ", error));
//                         }
//                     }
//                 });
//             } else if (parsedState) {
//                 const storedAudioData = localStorage.getItem(`audio_${currentAudioId}`);
//                 const audioData = JSON.parse(storedAudioData);
//                         currentAudioData = audioData;
//                         const parsedState = { // ساخت parsedState از اطلاعات ذخیره شده
//                             currentTime: audioData.currentTime || 0, // اگر currentTime ذخیره نشده بود، صفر در نظر می‌گیریم
//                             isPlaying: audioData.isPlaying || false // اگر isPlaying ذخیره نشده بود، false در نظر می‌گیریم
//                         };
//                 // console.log('-*a-', storedAudioData);
//                 // console.log('-*c-', currentAudioData);
//                 waitForPlayerInitialization().then(() => {
//                     setPlayerCurrentTime(parsedState.currentTime, parsedState.isPlaying);
//                 });
//             }
//         });
//
//     }
//
//
//     function createAudio(chapterIndex, parsedState) {
//         // if (!window.audio || !window.audio.id) { // بررسی وجود window.audio و window.audio.id
//         //     console.error("اطلاعات فایل صوتی در دسترس نیست (window.audio یا window.audio.id تعریف نشده است).");
//         //     return; // از اجرای ادامه تابع جلوگیری می‌کنیم
//         // }
//         const csrfToken = getCSRFToken();
//         getAudioUrl(csrfToken, window.audio.id, "CCDETAIL")
//             .done(function (audioResponse) {
//                 if (audioResponse && audioResponse.url) {
//                     const lastChapterIndex = window.chapter_set.length - 1; // index آخرین چپتر
//
//                     let player_chapters = window.chapter_set.map((chapter, i) => ({
//                         // id: chapter.id,
//                         id: i,
//                         startTime: convertToSeconds(chapter.start_time),
//                         // endTime: convertToSeconds((i < window.chapter_set.length - 1) ? window.chapter_set[i + 1].start_time : "پایان فایل صوتی"),
//                         endTime: i === lastChapterIndex ? convertToSeconds(window.audio_duration) : convertToSeconds(window.chapter_set[i + 1].start_time), // تبدیل window.audio_duration به ثانیه
//                         title: `${i + 1}. ${chapter.name}`,
//                     }));
//                     console.log('chapters ', player_chapters);
//                     currentAudioData = {
//                         id: window.audio.id,
//                         name: window.audio.name,
//                         title: window.audio.title,
//                         artist: '« خیلی ساده‌ست »',
//                         cover: coverImageUrl,
//                         chapters: player_chapters,
//                         src: audioResponse.url,
//                     };
//                     // saveAudioData(currentAudioData); // ذخیره اطلاعات فایل صوتی قبل از ایجاد پلیر
//                     // try {
//                     //     localStorage.setItem('lastPlayedAudioTitle', window.audio.title);
//                     //     localStorage.setItem('lastPlayedAudioId', window.audio.id);
//                     // } catch (e) {
//                     //     // console.error("Error getting Last player id from localStorage:", e);
//                     //     console.log("Error setting Last player id to localStorage:", e);
//                     //
//                     // }
//                     updatePlayer(currentAudioData, parsedState, chapterIndex);
//                 } else {
//                     console.error("URL فایل صوتی دریافت نشد.");
//                     Swal.fire({icon: 'error', title: 'خطا', text: "URL فایل صوتی دریافت نشد."});
//                 }
//             })
//             .fail(function (error) {
//                 console.error("Error fetching audio URL:", error);
//                 Swal.fire({icon: 'error', title: 'خطا', text: "خطا در برقراری ارتباط با سرور."});
//             });
//     }
//
//
//     function checkEverything() {
//         console.log(window.audio_duration);
//         if (hasPerm) {
//             try {
//                 const lastPlayedAudioTitle = localStorage.getItem('lastPlayedAudioTitle');
//                 const lastPlayedAudioId = localStorage.getItem('lastPlayedAudioId');
//                 let audioId = window.audio?.id || lastPlayedAudioId; // اولویت با window.audio.id، در صورت نبود از lastPlayedAudioId استفاده می‌کنیم
//                 let audioTitle = window.audio?.title || lastPlayedAudioTitle; // اولویت با window.audio.id، در صورت نبود از lastPlayedAudioId استفاده می‌کنیم
//
//                 if (audioId) { // اگر audioId وجود داشته باشد
//                     const storedAudioData = localStorage.getItem(`audio_${audioId}`);
//                     if (storedAudioData) {
//                         const audioData = JSON.parse(storedAudioData);
//                         currentAudioData = audioData;
//                         const parsedState = { // ساخت parsedState از اطلاعات ذخیره شده
//                             currentTime: audioData.currentTime || 0, // اگر currentTime ذخیره نشده بود، صفر در نظر می‌گیریم
//                             isPlaying: audioData.isPlaying || false // اگر isPlaying ذخیره نشده بود، false در نظر می‌گیریم
//                         };
//                         console.log('-------', parsedState);
//                         updatePlayer(audioData, parsedState, window.chapterIndexParam);
//                     } else {
//                         createAudio(window.chapterIndexParam, null);
//                     }
//                 }
//             } catch (e) {
//                 console.error("Error parsing player state from localStorage:", e);
//                 // localStorage.removeItem(playerStorageKey); // پاک کردن state خراب
//                 // Swal.fire({
//                 //     icon: 'error',
//                 //     title: 'خطا',
//                 //     text: "مشکلی در بازیابی وضعیت پخش پیش آمده است."
//                 // });
//             }
//         } else {
//             removeAudioSrc();
//         }
//     }
//
//     function updateCurrentChapter(chapterIndex) { // تابع داخل DOMContentLoaded
//         if (kplayer) {
//             kplayer.updateChapter(chapterIndex);
//             updateChapterIcons(chapterIndex);
//         } else {
//             console.error("Player is not initialized yet.");
//         }
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
//     function waitForPlayerInitialization() {
//         return new Promise((resolve, reject) => {
//             const checkInterval = setInterval(() => {
//                 if (kplayer) {
//                     clearInterval(checkInterval);
//                     resolve();
//                 }
//             }, 100); // چک کردن هر 100 میلی‌ثانیه
//         });
//     }
//
//     function setPlayerCurrentTime(time, isPlaying) {
//         if (kplayer) { // بررسی تفاوت زمان
//             kplayer.seek(time);
//             kplayer.on('seeked', function handler() {
//                 let playPromise;
//                 if (isPlaying) {
//                     playPromise = kplayer.play();
//                 } else {
//                     playPromise = kplayer.pause();
//                 }
//                 if (playPromise && typeof playPromise.catch === 'function') {
//                     playPromise.catch(error => console.error("Auto-play failed: ", error));
//                 }
//             });
//         } else {
//             console.error("kplayer not initialized");
//         }
//     }
//
//     function setupPageHistoryEvents() { // تغییر نام تابع برای وضوح بیشتر
//         // $(window).on('pageshow', () => {
//         //     console.log('pageshow', kplayer);
//         //     checkEverything();
//         // });
//         $(window).on('pageshow', function (event) {
//             // بررسی و تعیین flag در localStorage
//             const refreshFlag = localStorage.getItem('refreshFlag');
//
//             if (!isAudioPage) {
//                 if (!refreshFlag) {
//                     localStorage.setItem('refreshFlag', 'true'); // تعیین flag
//                     checkEverything();
//                     window.location.reload(); // رفرش صفحه فقط در صورتی که از کش بارگذاری شده باشد
//                     if (event.persisted) {
//                         // بررسی اینکه آیا صفحه از کش مرورگر بارگذاری شده است یا خیر
//                     }
//                 } else {
//                     localStorage.removeItem('refreshFlag'); // برداشتن flag بعد از یکبار رفرش
//                 }
//             }
//         });
//
//
//         $(window).on('popstate', () => {
//             console.log('popstate', kplayer);
//             checkEverything();
//         });
//
//         $(window).on('pagehide', () => {
//             // بررسی پرچم برای جلوگیری از اجرای چندباره تابع
//             const pagehideFlag = localStorage.getItem('pagehideFlag');
//             if (pagehideFlag) {
//                 return; // اگر پرچم وجود داشته باشد، از اجرای تابع جلوگیری می‌کنیم
//             }
//
//             localStorage.setItem('pagehideFlag', 'true'); // تنظیم پرچم
//
//             console.log('--pagehide', kplayer);
//             console.log('--pagehide data', currentAudioData);
//
//             // ذخیره وضعیت پخش
//             const audioData = JSON.parse(localStorage.getItem(`audio_${currentAudioId}`));
//             if (audioData) {
//                 audioData.currentTime = kplayer.currentTime;
//                 audioData.isPlaying = !kplayer.paused;
//                 saveAudioData(audioData); // استفاده از تابع saveAudioData
//             }
//
//             // حذف پرچم پس از ذخیره وضعیت
//             localStorage.removeItem('pagehideFlag');
//         });
//     }
//
// // ... در انتهای کد و داخل رویداد DOMContentLoaded
//     setupPageHistoryEvents(); // فراخوانی تابع جدید
//     checkEverything(); // فراخوانی اولیه
//
// });