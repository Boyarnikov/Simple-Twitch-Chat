# Simple-Twitch-Chat

Визуализация twitch чата в стиле "консольного приложения"

Запрашивает информацию о чате через twitchAPI, отправляет её на flask бэкенд и позволяет клиентам
подключаться через локальный хост для рендеринга стилизованного чата. 

Смайлики подгружаются при отправке сообщений и отображаются под сообщением

Поддержка TTS через награды за очки на базе pyttsx4 (на данный момент аудио проигрывается через серверное приложение)

![](/bin/demo.gif)

# Как использовать

```commandline
git clone https://github.com/Boyarnikov/Simple-Twitch-Chat
pip install -r requirements.txt
echo twitchAppId="Ваш twitch app id" twitchAppToken="Ваш twitch app токен" > Tokens.py 
python main.py
```
По умолчанию хост - http://127.0.0.1:5000. Можно использовать в OBS через браузер-источник.
