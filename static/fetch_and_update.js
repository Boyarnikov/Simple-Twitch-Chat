const message = 'Hello' // Try edit me
var this_data = ""
var timing = 1
var last_id_requested = -1

async function applyTypingEffect(element) {
  const words = element.innerText.split(' '); // Split text into words
  element.innerHTML = ''; // Clear the content

  let index = 0;
  await new Promise(r => setTimeout(r, 200));

  const typingEffect = setInterval(() => {
    element.textContent += words[index] + ' '; // Display one word at a time
    index++;
    if (index >= words.length) {
      clearInterval(typingEffect);
    }
  }, 50);
}

function scrollToBottom() {
  const chatContainer = document.querySelector('.chat-container');
  chatContainer.scrollTop = chatContainer.scrollHeight;
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

function addMessagesToPage(messagesData) {
  const chatContainer = document.querySelector('.chat-container');

  messagesData.forEach(message => {
    last_id_requested = Math.max(last_id_requested, message.id)
    const messageElement = document.createElement('div');
    messageElement.classList.add('other-message');

    const usernameElement = document.createElement('span');
    usernameElement.classList.add('username');
    usernameElement.textContent = message.username;

    const messageContentElement = document.createElement('span');
    messageContentElement.classList.add('message-content');
    messageContentElement.textContent = message.text;
    applyTypingEffect(messageContentElement)

    const timestampElement = document.createElement('span');
    timestampElement.classList.add('message-timestamp');
    timestampElement.textContent = message.time;

    const emotes = document.createElement('span');
    emotes.classList.add('message-emotes');
    emotes.textContent = "meme";
    console.log(message.emotes)


    messageElement.appendChild(usernameElement);
    messageElement.appendChild(messageContentElement);
    messageElement.appendChild(document.createElement('br'));
    messageElement.appendChild(timestampElement);

    for (var key of Object.keys(message.emotes)) {
        messageElement.appendChild(addEmojiToPage('/get_image/' + key, message.emotes[key]));
    }

    chatContainer.appendChild(messageElement);
  });

  scrollToBottom();
}

var chat = document.getElementById("chat");
async function updater() {
  var data = JSON.stringify( {"from_id": last_id_requested} );
  console.log(data)

  let response = await fetch('/data', {
  method: "FETCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: data
  });

  let messages = await response.json();
  if (messages.reset_index != null) {
        last_id_requested = messages.reset_index
  }

  addMessagesToPage(messages.data)

}

updater()
setInterval(updater, 1000);