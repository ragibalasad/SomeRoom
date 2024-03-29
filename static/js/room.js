var socketio = io();

const outputDiv = document.querySelector(".output");
const messages = document.getElementById("messages");

function scrollToBottom() {
  outputDiv.scrollTop = outputDiv.scrollHeight;
}
function getCurrentTime() {
const now = new Date();

// Get hours and minutes
let hours = now.getHours();
let minutes = now.getMinutes();

// Add leading zeros if needed
hours = hours < 10 ? '0' + hours : hours;
minutes = minutes < 10 ? '0' + minutes : minutes;

// Format the time as "HH:mm"
const formattedTime = hours + ':' + minutes;

return formattedTime;
}

// listen for messages and printout
const createMessage = (name, msg, decoration) => {
  if (decoration === "join") {
    const content = `
      <div class="message">
      <span class="green"> ${name} ${msg}</span>
      </div>
    `;
    messages.innerHTML += content;
  } else if (decoration === "leave") {
    const content = `
      <div class="message">
      <span class="orange"> ${name} ${msg}</span>
      </div>
    `;
    messages.innerHTML += content;
  } else {
    const promptDiv = document.createElement("div");
    promptDiv.classList.add("message");
    promptDiv.textContent = name + " : " + msg;
    outputDiv.appendChild(promptDiv);
    const dateSpan = document.createElement("span");
    dateSpan.classList.add("date");
    dateSpan.textContent = getCurrentTime();
    promptDiv.appendChild(dateSpan);
  }
  // Scroll to bottom after adding new content
  scrollToBottom();
};

socketio.on("message", (data) => {
  createMessage(data.nickname, data.message, data.decoration);
});

// send messages
const sendMessage = () => {
  const message = document.getElementById("message");
  if (message.value == "") return;
  socketio.emit("message", { data: message.value });
  message.value = "";
};

document.addEventListener("DOMContentLoaded", function () {
  const inputField = document.getElementById("message");

  inputField.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && inputField.value != "") {
      sendMessage();
      inputField.value = "";

      // Scroll to bottom after adding new content
      scrollToBottom();
    }
  });

  // Close button functionality
  const closeButton = document.querySelector(".close-button");
  closeButton.addEventListener("click", function () {
    if (confirm("You're about to leave!")) {
      window.location.href = "/";
    }
  });
});