const titleDatabase = new Map();
const avatarCache = new Map();
let configData = {};
let last_id_requested = -1;

// Загрузка конфигурации
(async function loadConfig() {
    try {
        const response = await fetch('/static/data.json');
        configData = await response.json();
    } catch (error) {
        console.error('Ошибка загрузки конфига:', error);
    }
})();

// Генератор СТАБИЛЬНЫХ аватарок
function generateStableAvatar(username) {
    if (!avatarCache.has(username)) {
        // Генерируем seed на основе ника
        const seed = username.split('').reduce((acc, char) =>
            acc + char.charCodeAt(0), 0);

        // thispersondoesnotexist.com с уникальным seed
        avatarCache.set(username,
            `https://thispersondoesnotexist.com?seed=${seed}&t=${Date.now()}`
        );
    }
    return avatarCache.get(username);
}

// Фиксированные титулы
function getStableTitle(username) {
    if (!titleDatabase.has(username)) {
        const index = username.split('').reduce((sum, char) => sum + char.charCodeAt(0), 0) % configData.titles.length;
        titleDatabase.set(username, configData.titles[index]);
    }
    return titleDatabase.get(username);
}

// Пивные эмодзи для своих
function addBeerEmoji(username, element) {
    const beerLovers = ['blin_sema', 'eshi9774'];
    if (beerLovers.includes(username.toLowerCase())) {
        const beer = document.createElement('img');
        beer.src = 'https://cdn-icons-png.flaticon.com/512/761/761767.png';
        beer.className = 'beer-emoji';
        element.appendChild(beer);
    }
}

function addEmojiToPage(url, count) {
    const container = document.createElement('span');
    container.classList.add('emoji-container');

    const thumbnail = document.createElement('img');
    thumbnail.src = url;
    thumbnail.classList.add('emoji-thumbnail');

    const numberSpan = document.createElement('span');
    numberSpan.textContent = count;
    numberSpan.classList.add('emoji-number');

    container.appendChild(thumbnail);
    container.appendChild(numberSpan);

    return container;
}

// Добавление сообщений
function addMessagesToPage(messages) {
    const chatContainer = document.querySelector('.chat-container');

    messages.forEach(msg => {
        last_id_requested = Math.max(last_id_requested, msg.id);

        const messageEl = document.createElement('div');
        messageEl.className = 'message';

        // Аватарка
        const avatar = document.createElement('img');
        avatar.className = 'user-avatar';
        avatar.src = generateStableAvatar(msg.username);
        avatar.onerror = () => avatar.src = '/static/default-avatar.png';

        // Блок сообщения
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        // Шапка
        const header = document.createElement('div');
        header.className = 'message-header';

        // Ник + титул
        const usernameEl = document.createElement('span');
        usernameEl.className = 'username';
        usernameEl.textContent = msg.username;

        const titleEl = document.createElement('span');
        titleEl.className = 'user-title';
        titleEl.textContent = getStableTitle(msg.username);

        // Пиво
        addBeerEmoji(msg.username, header);

        // Текст
        const textEl = document.createElement('div');
        textEl.className = 'message-text';
        textEl.textContent = msg.text + getFooterPhrase(msg.text);

        // Время
        const timeEl = document.createElement('span');
        timeEl.className = 'timestamp';
        timeEl.textContent = msg.time;

        // Сборка
        header.append(usernameEl, titleEl);
        bubble.append(header, textEl, timeEl);
        messageEl.append(avatar, bubble);
        chatContainer.appendChild(messageEl);

        for (var key of Object.keys(msg.emotes)) {
            bubble.appendChild(addEmojiToPage('/get_image/' + key, msg.emotes[key]));
        }

    });

    // Remove old messages if more than 10
    const allMessages = document.querySelectorAll('.message');
    if (allMessages.length > 10) {
        const removeCount = allMessages.length - 10;
        for (let i = 0; i < removeCount; i++) {
            allMessages[i].remove();
        }
    }

    scrollToBottom();
}

// Футер-фразы
function getFooterPhrase(originalText) {
    if (Math.random() > 0.3) return '';
    const lastChar = originalText.trim().slice(-1);
    const phrases = configData.footerPhrases;
    return phrases.length > 0 ? phrases[Math.floor(Math.random() * phrases.length)].text : '';
}

// Скролл
function scrollToBottom() {
    const chat = document.querySelector('.chat-container');
    chat.scrollTop = chat.scrollHeight;
}

// Обновление данных
async function fetchUpdates() {
    try {
        const response = await fetch('/data', {
            method: 'FETCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({from_id: last_id_requested})
        });
        const data = await response.json();
        if (data.reset_index !== undefined) last_id_requested = data.reset_index;
        if (data.data?.length > 0) addMessagesToPage(data.data);
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

// Запуск
document.addEventListener('DOMContentLoaded', () => {
    fetchUpdates();
    setInterval(fetchUpdates, 1500);
});