import CryptoJS from 'crypto-js';
import {Player, Chapter} from 'shikwasa';
//v1 clean
let kplayer;
const playerStorageKey = 'kplayer_state'; // تعریف playerStorageKey در اینجا

// کلید قوی برای رمزگذاری و رمزگشایی
const secretKey = 'aSdfGhjKlYuiOpmNbVcXzQwErTbnmJk';

function encryptData(data) {
    return CryptoJS.AES.encrypt(data, secretKey).toString();
}

function decryptData(encryptedData) {
    const bytes = CryptoJS.AES.decrypt(encryptedData, secretKey);
    return bytes.toString(CryptoJS.enc.Utf8);
}

function createPlayer(container, audio) {

    Player.use(Chapter);
    if (kplayer) {
        kplayer.update({
            // id: audio.id,
            title: audio.name, /*persian*/
            album: audio.title, /*english*/
            artist: audio.artist,
            cover: audio.cover,
            src: audio.src,
            chapters: audio.chapters, // چپترها جداگانه
        });
    } else {
        kplayer = new Player({
            id: audio.id,
            container: container,
            audio: { // فیلدهای audio به صورت جداگانه
                id: audio.id,
                title: audio.name, /*persian*/
                album: audio.title, /*english*/
                artist: audio.artist,
                cover: audio.cover,
                src: audio.src,
                chapters: audio.chapters, // چپترها جداگانه
            },
            themeColor: "#FFFFFFFF",
            theme: 'dark',
            fixed: {type: 'static'},
        });
    }
    // kplayer = new Player({
    //     id: audio.id,
    //     container: container,
    //     audio: { // فیلدهای audio به صورت جداگانه
    //         id: audio.id,
    //         title: audio.title,
    //         artist: audio.artist,
    //         cover: audio.cover,
    //         src: audio.src,
    //         chapters: audio.chapters, // چپترها جداگانه
    //     },
    //     themeColor: "#FFFFFFFF",
    //     theme: 'dark',
    //     fixed: {type: 'static'},
    // });
    kplayer?.on('timeupdate', function () {
        if (kplayer && kplayer.audio) {
            const audioData = JSON.parse(localStorage.getItem(`audio_${kplayer.options.id}`));
            if (audioData) { // بررسی وجود audioData قبل از به‌روزرسانی
                audioData.currentTime = kplayer.currentTime;
                audioData.isPlaying = !kplayer.paused;
                saveAudioData(audioData); // استفاده از تابع saveAudioData

                // localStorage.setItem(`audio_${kplayer.options.id}`, JSON.stringify(audioData));
                // localStorage.setItem('lastPlayedAudioId', kplayer.options.id);
            }
        }
    });

    kplayer?.on('pause', function () {
        if (kplayer && kplayer.audio) {
            const audioData = JSON.parse(localStorage.getItem(`audio_${kplayer.options.id}`));
            if (audioData) {
                audioData.isPlaying = false;
                saveAudioData(audioData); // استفاده از تابع saveAudioData

            }
        }
    });

    kplayer?.on('play', function () {
        if (kplayer && kplayer.audio) {
            const audioData = JSON.parse(localStorage.getItem(`audio_${kplayer.options.id}`));
            if (audioData) {
                audioData.isPlaying = true;
                saveAudioData(audioData); // استفاده از تابع saveAudioData
            }
        }
    });

    kplayer?.on('ended', () => {
        if (kplayer && kplayer.audio) {
            const audioData = JSON.parse(localStorage.getItem(`audio_${kplayer.options.id}`));
            if (audioData) {
                audioData.isPlaying = false; // تنظیم isPlaying به false بعد از اتمام پخش
                saveAudioData(audioData); // استفاده از تابع saveAudioData
            }
        }
    });
    return kplayer;
}

function setPlayer(player) {
    kplayer = player;
}

function getPlayer() {
    return kplayer;
}

function saveAudioData(audioData) {

    localStorage.setItem(`audio_${audioData.id}`, JSON.stringify(audioData));
    // localStorage.setItem('lastPlayedAudioId', kplayer.options.id);
    // // رمزنگاری src
    // const encryptedSrc = encryptData(audioData.src);
    // // ایجاد یک کپی از audioData و تغییر src به encryptedSrc
    // const dataToSave = { ...audioData, src: encryptedSrc };
    // // ذخیره dataToSave در localStorage
    // localStorage.setItem(`audio_${audioData.id}`, JSON.stringify(dataToSave));
}

// function savePlayerState(isPlaying) {
//     if (kplayer && kplayer.audio) {
//         const newState = JSON.stringify({ // ایجاد مقدار جدید
//             audio: {
//                 id: kplayer.options.id,
//                 src: encryptData(kplayer.audio.src),
//                 title: kplayer.audio.title,
//                 artist: kplayer.options.audio.artist,
//                 cover: kplayer.options.audio.cover,
//                 chapters: kplayer.options.audio.chapters,
//             },
//             currentTime: kplayer.currentTime,
//             isPlaying: isPlaying
//         });
//
//         const oldState = localStorage.getItem(playerStorageKey); // دریافت مقدار قبلی از localStorage
//
//         if (newState !== oldState) { // مقایسه مقدار جدید و قبلی
//             localStorage.setItem(playerStorageKey, newState); // فقط در صورت تفاوت، به‌روزرسانی localStorage
//         }
//     }
// }

// function savePlayerState(isPlaying) {
//     if (kplayer && kplayer.audio) {
//         const encryptedSrc = encryptData(kplayer.audio.src);
//         localStorage.setItem(playerStorageKey, JSON.stringify({
//             audio: {
//                 id: kplayer.options.id,
//                 src: encryptedSrc, // ذخیره آدرس رمزگذاری شده
//                 title: kplayer.audio.title,
//                 artist: kplayer.audio.artist,
//                 cover: kplayer.audio.cover,
//                 chapters: kplayer.audio.chapters,
//             },
//             currentTime: kplayer.currentTime,
//             isPlaying: isPlaying
//         }));
//     }
// }

function removeAudioSrc() {
    const storedPlayerState = localStorage.getItem(playerStorageKey);
    if (storedPlayerState) {
        const parsedState = JSON.parse(storedPlayerState);
        if (parsedState && parsedState.audio) {
            delete parsedState.audio.src; // حذف آدرس از حافظه ذخیره شده
            localStorage.setItem(playerStorageKey, JSON.stringify(parsedState));
        }
    }
}

// صادر کردن توابع برای استفاده در سایر فایل‌ها
export {
    Player, Chapter, createPlayer, setPlayer, getPlayer, saveAudioData,
    playerStorageKey, removeAudioSrc, encryptData, decryptData
};
