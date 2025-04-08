import CryptoJS from 'crypto-js';
import { Player, Chapter } from 'shikwasa';

const playerStorageKey = 'kplayer_state';
const secretKey = 'aSdfGhjKlYuiOpmNbVcXzQwErTbnmJk';

function encryptData(data) {
    return CryptoJS.AES.encrypt(data, secretKey).toString();
}

function decryptData(encryptedData) {
    const bytes = CryptoJS.AES.decrypt(encryptedData, secretKey);
    return bytes.toString(CryptoJS.enc.Utf8);
}

function removeAudioSrc() {
    const storedPlayerState = localStorage.getItem(playerStorageKey);
    if (storedPlayerState) {
        const parsedState = JSON.parse(storedPlayerState);
        if (parsedState && parsedState.audio) {
            delete parsedState.audio.src;
            localStorage.setItem(playerStorageKey, JSON.stringify(parsedState));
        }
    }
}
console.log(Chapter); // بررسی اینکه Chapter به درستی import شده

//  named exports  به صورت زیر
export { Player, Chapter, playerStorageKey, removeAudioSrc, encryptData, decryptData };