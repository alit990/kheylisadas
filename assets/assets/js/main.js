// main.js

let dbInstance = null;

function openDatabase() {
    if (dbInstance) {
        return Promise.resolve(dbInstance);
    }
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('playerDataDB', 2); // ارتقای نسخه به 2

        request.onerror = event => {
            console.error('Database error:', event.target.error);
            reject(event.target.error);
        };

        request.onsuccess = event => {
            console.log('Database opened successfully');
            dbInstance = event.target.result;
            resolve(dbInstance);
        };

        request.onupgradeneeded = event => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('playerData')) {
                db.createObjectStore('playerData', {keyPath: 'id'});
            }
            if (!db.objectStoreNames.contains('settings')) {
                db.createObjectStore('settings', {keyPath: 'id'});
            }
        };
    });
}




function savePlayerData(audioData) {
    if (!audioData.id) {
        audioData.id = audioData.audioId; // یا هر شناسه منحصربه‌فرد دیگر
    }

    return openDatabase().then(db => {
        return new Promise((resolve, reject) => {
            const transaction = db.transaction(['playerData'], 'readwrite');
            const store = transaction.objectStore('playerData');
            const request = store.put(audioData); // ذخیره با استفاده از audioData.id به عنوان کلید

            request.onsuccess = () => {
                console.log(`Player data for audio ID ${audioData.id} saved successfully`);
                resolve();
            };

            request.onerror = event => {
                console.error(`Error saving player data for audio ID ${audioData.id}:`, event.target.error);
                reject(event.target.error);
            };
        });
    });
}


function getPlayerData(id) {
    return openDatabase().then(db => {
        return new Promise((resolve, reject) => {
            const transaction = db.transaction(['playerData'], 'readonly');
            const store = transaction.objectStore('playerData');
            const request = store.get(id);

            request.onsuccess = event => {
                resolve(event.target.result);
            };

            request.onerror = event => {
                console.error('Error getting player data:', event.target.error);
                reject(event.target.error);
            };
        });
    });
}


// مثلاً این تابع می‌تواند توسط پلیر برای ذخیره‌سازی وضعیت صدا ارسال شود
function updatePlayerData(audioData) {
    navigator.serviceWorker.controller.postMessage({
        action: 'updatePlayerData',
        audioData: audioData
    });
}

// تابع جدید برای ذخیره شناسه آخرین فایل صوتی پخش شده
function saveLastPlayedAudioId(audioId) {
    console.log('Starting to save last played audio ID:', audioId); // اضافه کردن لاگ

    return openDatabase().then(db => {
        return new Promise((resolve, reject) => {
            const transaction = db.transaction(['playerData'], 'readwrite');
            const store = transaction.objectStore('playerData');
            const request = store.put({id: 'lastPlayedAudioId', audioId: audioId});

            transaction.oncomplete = () => {
                console.log('Transaction completed successfully');
            };

            transaction.onerror = event => {
                console.error('Transaction error:', event.target.error);
            };

            request.onsuccess = () => {
                console.log('Last played audio ID saved successfully in IndexedDB');
                resolve();
            };

            request.onerror = event => {
                console.error('Error saving last played audio ID in IndexedDB:', event.target.error);
                reject(event.target.error);
            };
        });
    });
}

function getLastPlayedAudio() {
    return openDatabase().then(db => {
        return new Promise((resolve, reject) => {
            const transaction = db.transaction(['playerData'], 'readonly');
            const store = transaction.objectStore('playerData');
            const request = store.get('lastPlayedAudioId');

            request.onsuccess = event => {
                const result = event.target.result;
                console.log('Last played audio ID:', result); // اضافه کردن لاگ برای بررسی شناسه آخرین فایل صوتی
                if (result && result.audioId) {
                    const audioRequest = store.get(result.audioId);
                    audioRequest.onsuccess = audioEvent => {
                        console.log('Last played audio data:', audioEvent.target.result); // اضافه کردن لاگ برای بررسی داده‌های آخرین فایل صوتی
                        resolve(audioEvent.target.result);
                    };
                    audioRequest.onerror = audioEvent => {
                        console.error('Error getting audio data:', audioEvent.target.error);
                        reject(audioEvent.target.error);
                    };
                } else {
                    resolve(null);
                }
            };

            request.onerror = event => {
                console.error('Error getting last played audio ID:', event.target.error);
                reject(event.target.error);
            };
        });
    });
}


// بازیابی وضعیت پخش‌کننده
function getPlayerStatus(audioId) {
    return new Promise((resolve, reject) => {
        navigator.serviceWorker.controller.postMessage({
            action: 'getPlayerStatus',
            audioId: audioId
        });

        navigator.serviceWorker.addEventListener('message', function handler(event) {
            if (event.data.action === 'playerStatus') {
                navigator.serviceWorker.removeEventListener('message', handler);
                resolve(event.data.audioData);
            }
        });
    });
}


// تابع برای ذخیره وضعیت نمایش پلیر
function savePlayerVisibility(isVisible) {
    return openDatabase().then(db => {
        return new Promise((resolve, reject) => {
            const transaction = db.transaction(['settings'], 'readwrite');
            const store = transaction.objectStore('settings');
            const request = store.put({ id: 'playerVisible', value: isVisible });

            request.onsuccess = () => {
                console.log('Player visibility status saved successfully');
                resolve();
            };

            request.onerror = event => {
                console.error('Error saving player visibility status:', event.target.error);
                reject(event.target.error);
            };
        });
    });
}

// تابع برای بازیابی وضعیت نمایش پلیر
function getPlayerVisibility() {
    return openDatabase().then(db => {
        return new Promise((resolve, reject) => {
            const transaction = db.transaction(['settings'], 'readonly');
            const store = transaction.objectStore('settings');
            const request = store.get('playerVisible');

            request.onsuccess = event => {
                resolve(event.target.result?.value);
            };

            request.onerror = event => {
                console.error('Error getting player visibility status:', event.target.error);
                reject(event.target.error);
            };
        });
    });
}

navigator.serviceWorker.addEventListener('message', function(event) {
    if (event.data.action === 'getLastPlayedAudio') {
        getLastPlayedAudio().then(audioData => {
            event.ports[0].postMessage({ audioData: audioData });
        }).catch(error => {
            console.error('Error getting last played audio from IndexedDB:', error);
        });
    }
});
