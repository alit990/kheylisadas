// const MANIFEST_VERSION = '1.0.19'; // شماره نسخه را اینجا تغییر دهید
// const CACHE_NAME = `my-cache-${MANIFEST_VERSION}`;
//
// // const CACHE_NAME = 'my-cache-v1';
//
// const urlsToCache = [
//     '/',
//     '/index',
//     '/statics/assets/css/styles.css',
//     '/statics/assets/css/my-custom.css',
//     '/statics/bundle.js',
//     '/statics/bundle_sweetalert.js',
//     '/statics/assets/js/player-manager.js'
// ];
// تشخیص دامنه برای تعیین محیط (لوکال یا سرور)
const isLocal = self.location.hostname === 'localhost' || self.location.hostname === '127.0.0.1';
const STATIC_PREFIX = isLocal ? '/statics/' : '/static/';

const MANIFEST_VERSION = '1.0.36';
const CACHE_NAME = `my-cache-${MANIFEST_VERSION}`;
const urlsToCache = [
  // '/',
  // '/index',
  `${STATIC_PREFIX}assets/css/styles.css`,
  `${STATIC_PREFIX}assets/css/my-custom.css`,
  `${STATIC_PREFIX}bundle.js`,
  `${STATIC_PREFIX}bundle_sweetalert.js`,
  `${STATIC_PREFIX}assets/js/player-manager.js`,
  `${STATIC_PREFIX}assets/js/main.js`
];
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
      .catch(error => console.error('Error caching resources:', error))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(name => name !== CACHE_NAME).map(name => caches.delete(name))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const url = event.request.url;
  console.log(`Fetching: ${url}`);
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          console.log(`Found in cache: ${url}`);
          return response;
        }
        console.log(`Not in cache, fetching from network: ${url}`);
        return fetch(event.request)
          .catch(error => {
            console.error(`Failed to fetch ${url}:`, error);
            // پاسخ پیش‌فرض در صورت خطا (اختیاری)
            return new Response('Network error occurred', { status: 503 });
          });
      })
      .catch(error => {
        console.error(`Error in caches.match for ${url}:`, error);
        return fetch(event.request);
      })
  );
});
// کش کردن منابع
// self.addEventListener('install', event => {
//     event.waitUntil(
//         caches.open(CACHE_NAME)
//             .then(cache => {
//                 return Promise.all(urlsToCache.map(url => {
//                     return fetch(url).then(response => {
//                         if (!response.ok) {
//                             throw new Error('Failed to fetch ' + url);
//                         }
//                         return cache.put(url, response);
//                     });
//                 }));
//             })
//     );
//     self.skipWaiting(); // فعال کردن سرویس ورکر بلافاصله بعد از نصب
// });

// مدیریت درخواست‌ها
// self.addEventListener('fetch', event => {
//     event.respondWith(
//         caches.match(event.request)
//             .then(response => {
//                 if (response) {
//                     return response; // اگر درخواست در کش بود، از کش برگردان
//                 }
//                 return fetch(event.request); // در غیر این صورت، از سرور درخواست کن
//             })
//     );
// });

// مدیریت پیام‌ها برای ذخیره‌سازی و بازیابی داده‌های پلیر
self.addEventListener('message', event => {
    if (event.data.action === 'updatePlayerData') {
        const {audioData} = event.data;
        savePlayerData(audioData).then(() => {
            console.log('Player data updated in IndexedDB');
        }).catch(error => {
            console.error('Error updating player data in IndexedDB:', error);
        });
    } else if (event.data.action === 'getPlayerStatus') {
        const audioId = event.data.audioId;
        if (audioId) {
            getPlayerData(audioId).then(audioData => {
                if (audioData) {
                    event.source.postMessage({
                        action: 'playerStatus',
                        audioData: audioData
                    });
                }
            }).catch(error => {
                console.error('Error getting player data from IndexedDB:', error);
            });
        }
    }
});

// فعال‌سازی سرویس ورکر
// self.addEventListener('activate', event => {
//     const cacheWhitelist = [`my-cache-${MANIFEST_VERSION}`]; // استفاده از شماره نسخه در نام کش
//
//     event.waitUntil(
//         caches.keys().then(cacheNames => {
//             return Promise.all(
//                 cacheNames.map(cacheName => {
//                     if (cacheWhitelist.indexOf(cacheName) === -1) {
//                         return caches.delete(cacheName);
//                     }
//                 })
//             );
//         })
//     );
//     return self.clients.claim(); // دسترسی به سرویس ورکر در تمامی تب‌های فعال
// });

// ارسال داده‌های پلیر به کلاینت
function sendPlayerDataToClient(client) {
    getLastPlayedAudio().then(audioData => {
        if (audioData) {
            client.postMessage({
                action: 'playerUpdated',
                audioData: audioData,
                currentTime: audioData.currentTime || 0,
                isPlaying: audioData.isPlaying || false
            });
        }
    }).catch(error => {
        console.error('Error getting last played audio from IndexedDB:', error);
    });
}

// توابع openDatabase, savePlayerData و getPlayerData در main.js قرار دارند
// ثبت و مدیریت sync
// ثبت و مدیریت sync
self.addEventListener('sync', event => {
    if (event.tag === 'sync-player-status') {
        event.waitUntil(syncPlayerStatus());
    }
});

function syncPlayerStatus() {
    return new Promise((resolve, reject) => {
        const messageChannel = new MessageChannel();
        messageChannel.port1.onmessage = event => {
            if (event.data.audioData) {
                self.clients.matchAll().then(clients => {
                    clients.forEach(client => {
                        client.postMessage({
                            action: 'continuePlaying',
                            audioData: event.data.audioData
                        });
                    });
                });
                resolve();
            } else {
                reject('No audio data received');
            }
        };

        self.clients.matchAll().then(clients => {
            if (clients.length > 0) {
                clients[0].postMessage({ action: 'getLastPlayedAudio' }, [messageChannel.port2]);
            } else {
                reject('No clients found');
            }
        });
    }).catch(error => {
        console.error('Error during sync player status:', error);
    });
}
