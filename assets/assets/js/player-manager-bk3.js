// document.addEventListener('DOMContentLoaded', function () {
//     const {
//         createPlayer, getPlayer, setPlayer, savePlayerState,
//         playerStorageKey, removeAudioSrc, encryptData, decryptData
//     } = MyLibrary;
//     const isAudioPage = window.location.pathname.includes('audio');
//     let kplayer;
//     let hasPlayed;
//     let isPlayerVisible;
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
//             savePlayerState(); // ذخیره وضعیت پلیر
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
//         if (!isPlayerVisible && playerFloating) {
//             playerFloating.classList.add('show');
//             isPlayerVisible = true;
//             adjustPadding(); // تنظیم padding بلافاصله بعد از نمایش پلیر
//             adjustScroll();
//         }
//     }
//
//     function hidePlayer() {
//         if (isPlayerVisible && playerFloating) {
//             playerFloating.classList.remove('show');
//             isPlayerVisible = false;
//             adjustPadding(); // حذف padding بلافاصله بعد از پنهان شدن پلیر
//         }
//     }
//
//     function adjustScroll() {
//         if (isPlayerVisible && playerFloating) {
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
//         if (playerFloating && isPlayerVisible) { // بررسی وجود playerFloating و نمایش آن
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
//             savePlayerState(); // ذخیره وضعیت پلیر
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
//
//         if (!kplayer) {
//             kplayer = createPlayer(playerContainer, audioData);
//             window.addEventListener('scroll', adjustScroll); // اضافه کردن listener اسکرول
//             showPlayer(); // نمایش پلیر شناور
//             setPlayer(kplayer);
//
//             if (!isAudioPage) {
//                 customPlayerControls(playerContainer); // فراخوانی تابع اضافه‌کردن دکمه‌های سفارشی
//             }
//         } else if (window.audio?.id && kplayer.options.id !== window.audio.id) {
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
//         }
//         // انتقال پلیر به body بعد از ایجاد یا به‌روزرسانی
//         const playerFloating = document.getElementById('player-floating');
//         if (playerFloating && playerFloating.parentNode !== document.body) { // بررسی برای جلوگیری از انتقال مجدد
//             document.body.appendChild(playerFloating);
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
//                 setPlayerCurrentTime(parsedState.currentTime, parsedState.isPlaying);
//             }
//         });
//     }
//
//
//     function createAudio(chapterIndex, parsedState) {
//         if (!window.audio || !window.audio.id) { // بررسی وجود window.audio و window.audio.id
//             console.error("اطلاعات فایل صوتی در دسترس نیست (window.audio یا window.audio.id تعریف نشده است).");
//             return; // از اجرای ادامه تابع جلوگیری می‌کنیم
//         }
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
//                     const audioData = {
//                         id: window.audio.id,
//                         title: window.audio.name,
//                         artist: '« خیلی ساده‌ست »',
//                         cover: coverImageUrl,
//                         chapters: player_chapters,
//                         src: audioResponse.url,
//                     };
//                     updatePlayer(audioData, parsedState, chapterIndex);
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
//     function checkEverything() {
//         console.log(window.audio_duration);
//         if (hasPerm) {
//             try {
//                 const storedPlayerState = localStorage.getItem(playerStorageKey);
//                 if (storedPlayerState) {
//                     const parsedState = JSON.parse(storedPlayerState);
//                     // بررسی window.audio و window.audio.id برای جلوگیری از خطا
//                     // بررسی وجود window.audio در ابتدا
//                     if (window.audio) {
//                         // حالا که window.audio وجود دارد، id را مقایسه می‌کنیم
//                         if (window.audio.id && parsedState?.audio?.id && parsedState.audio.id === window.audio.id) {
//                             if (parsedState?.audio?.src) {
//                                 parsedState.audio.src = decryptData(parsedState.audio.src);
//                                 const audioData = {
//                                     id: parsedState.audio.id,
//                                     title: parsedState.audio.title,
//                                     artist: parsedState.audio.artist,
//                                     cover: parsedState.audio.cover,
//                                     chapters: parsedState.audio.chapters,
//                                     src: parsedState.audio.src
//                                 };
//                                 updatePlayer(audioData, parsedState, window.chapterIndexParam);
//                             }
//                         } else {
//                             localStorage.removeItem(playerStorageKey); // پاک کردن state قبلی چون مربوط به فایل دیگه است
//                             createAudio(window.chapterIndexParam, null);
//                         }
//                     } else {
//                         // اگر window.audio وجود نداشت، هیچ کاری انجام نمی‌دهیم و پلیر قبلی به کار خود ادامه می‌دهد
//                         // در واقع نیازی به نوشتن کد اضافی در اینجا نیست
//                         if (parsedState?.audio?.src) {
//                             parsedState.audio.src = decryptData(parsedState.audio.src);
//                             const audioData = {
//                                 id: parsedState.audio.id,
//                                 title: parsedState.audio.title,
//                                 artist: parsedState.audio.artist,
//                                 cover: parsedState.audio.cover,
//                                 chapters: parsedState.audio.chapters,
//                                 src: parsedState.audio.src
//                             };
//                             updatePlayer(audioData, parsedState, window.chapterIndexParam);
//                         }
//                     }
//                 } else {
//                     createAudio(window.chapterIndexParam, null);
//                 }
//             } catch (e) {
//                 console.error("Error parsing player state from localStorage:", e);
//                 localStorage.removeItem(playerStorageKey); // پاک کردن state خراب
//                 Swal.fire({
//                     icon: 'error',
//                     title: 'خطا',
//                     text: "مشکلی در بازیابی وضعیت پخش پیش آمده است."
//                 });
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
//     function setPlayerCurrentTime(time, isPlaying) {
//         if (kplayer && kplayer.currentTime !== time) { // بررسی تفاوت زمان
//             kplayer.seek(time);
//             kplayer.on('seeked', function handler() {
//                 if (isPlaying) {
//                     const playPromise = kplayer.play();
//                     if (playPromise && typeof playPromise.catch === 'function') {
//                         playPromise.catch(error => console.error("Auto-play failed: ", error));
//                     }
//                 }
//             });
//         } else {
//             console.error("kplayer not initialized");
//         }
//     }
//
//     function setupPageHistoryEvents() { // تغییر نام تابع برای وضوح بیشتر
//         $(window).on('pageshow', () => {
//             console.log('pageshow', kplayer);
//             checkEverything();
//         });
//
//         $(window).on('popstate', () => {
//             console.log('popstate', kplayer);
//             checkEverything();
//         });
//
//         $(window).on('pagehide', () => { // برای ذخیره وضعیت هنگام ترک صفحه
//             console.log('pagehide', kplayer);
//             if (kplayer) savePlayerState(!kplayer.paused);
//         });
//     }
//
// // ... در انتهای کد و داخل رویداد DOMContentLoaded
//     setupPageHistoryEvents(); // فراخوانی تابع جدید
//     checkEverything(); // فراخوانی اولیه
//
// });