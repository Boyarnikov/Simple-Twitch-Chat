const message = 'Hello' // Try edit me
var this_data = ""
var timing = 1

function applyTypingEffect(element) {
  const words = element.innerText.split(' '); // Split text into words
  element.innerHTML = ''; // Clear the content

  let index = 0;

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

function addMessagesToPage(messagesData) {
  const chatContainer = document.querySelector('.chat-container');

  messagesData.forEach(message => {
    const messageElement = document.createElement('div');
    messageElement.classList.add('other-message');

    const usernameElement = document.createElement('span');
    usernameElement.classList.add('username');
    usernameElement.textContent = message.username;

    const messageContentElement = document.createElement('span');
    messageContentElement.classList.add('message-content');
    messageContentElement.textContent = message.text;
    applyTypingEffect(messageContentElement)

    const timestampElement = document.createElement('div');
    timestampElement.classList.add('message-timestamp');
    timestampElement.textContent = message.time;

    messageElement.appendChild(usernameElement);
    messageElement.appendChild(messageContentElement);
    messageElement.appendChild(timestampElement);

    chatContainer.appendChild(messageElement);
  });

  scrollToBottom();
}

var chat = document.getElementById("chat");
async function updater() {
  var data = JSON.stringify( {"test": "test"} );
  console.log(data)

  let response = await fetch('/data', {
  method: "FETCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: data
  });
  let messages = await response.json();
  addMessagesToPage(messages)

}

updater()
setInterval(updater, 1000);