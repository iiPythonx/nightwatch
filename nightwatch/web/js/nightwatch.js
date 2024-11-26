// Copyright (c) 2024 iiPython

import ConnectionManager from "./flows/connection.js";
import { main, grab_data } from "./flows/welcome.js";

// Leftmark :3
const leftmark_rules = [
    { regex: /\*\*((?:[^\\]|\\.)*?)\*\*/g, replace: "<strong>$1</strong>" },
    { regex: /__((?:[^\\]|\\.)*?)__/g, replace: "<u>$1</u>" },
    { regex: /~~((?:[^\\]|\\.)*?)~~/g, replace: "<s>$1</s>" },
    { regex: /\*((?:[^\\]|\\.)*?)\*/g, replace: "<em>$1</em>" },
    { regex: /\!\[((?:[^\\]|\\.)*?)\]\(((?:[^\\]|\\.)*?)\)/g, replace: `<a href = "$2" target = "_blank"><img alt = "$1" src = "$2"></a>` },
    { regex: /\[((?:[^\\]|\\.)*?)\]\(((?:[^\\]|\\.)*?)\)/g, replace: `<a href = "$2" target = "_blank" rel = "noreferrer">$1</a>` }
];

function leftmark(content) {
    return leftmark_rules.reduce((output, rule) => output.replace(rule.regex, rule.replace), content);
}

// Couple constants
const TIME_FORMATTER = new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true
});
const NOTIFICATION_SFX = new Audio("/audio/notification.mp3");

(async () => {
    const { username, hex, address } = await grab_data();

    // Keep track of the last message
    let last_author, last_time;

    // Connection screen
    const connection = new ConnectionManager(
        { username, hex, address },
        {
            on_connect: () => {
                main.classList.remove("loading");
                main.classList.add("full-layout");
                main.innerHTML = `
                    <div class = "chat-input">
                        <div class = "chat"></div>
                        <div class = "input-box">
                            <input type = "text" id = "actual-input" placeholder = "Share some thoughts...">
                            <button>Send →</button>
                        </div>
                    </div>
                    <div class = "sidebar">
                        <div class = "server-data">
                            <p id = "server-name"></p>
                            <button id = "leave">LEAVE SERVER</button>
                        </div>
                        <hr>
                        <div class = "member-list">
                            <p>Current member list:</p>
                        </div>
                        <hr>
                        <div class = "user-data">
                            <p>Connected as <span style = "color: #${hex};">${username}</span>.</p>
                        </div>
                    </div>
                `;

                // Handle sending
                const input = document.getElementById("actual-input");
                function send_message() {
                    if (!input.value.trim()) return;
                    connection.send({ type: "message", data: { message: input.value } });
                    input.value = "";
                }
                input.addEventListener("keydown", (e) => { if (e.key === "Enter") send_message(); });
                document.querySelector(".chat-input button").addEventListener("click", send_message);

                // Handle leaving
                document.getElementById("leave").addEventListener("click", () => {
                    window.location.reload();  // Fight me.
                });
            },
            on_message: (message) => {
                const current_time = TIME_FORMATTER.format(new Date(message.time * 1000));

                // Check for anything hidden
                const hide_author = message.user.name === last_author;
                last_author = message.user.name, last_time = current_time;

                // Construct text/attachment
                let attachment = message.message, classlist = "message-content";
                if (attachment.toLowerCase().match(/^https:\/\/[\w\d./-]+.(?:avifs?|a?png|jpe?g|jfif|webp|ico|gif|svg)(?:\?.+)?$/)) {
                    attachment = `![untitled](${attachment})`;
                }

                // Clean attachment for the love of god
                const cleaned = attachment.replace(/&/g, "&amp;")
                                .replace(/</g, "&lt;")
                                .replace(/>/g, "&gt;")
                                .replace(/"/g, "&quot;")
                                .replace(/"/g, "&#039;");
                
                // Apply leftmark
                attachment = leftmark(cleaned);
                if (cleaned !== attachment) {
                    attachment = `<span>${attachment}</span>`;
                    const dom = new DOMParser().parseFromString(attachment, "text/html");

                    // Handle image adjusting
                    const image = dom.querySelector("img");
                    if (image) {
                        classlist += " has-image";
                        image.src = `http${connection.protocol}://${address}/api/fwd/${btoa(image.src.slice(8))}`;
                        attachment = dom.body.innerHTML;
                    };
                };

                // Construct message
                const element = document.createElement("div");
                element.classList.add("message");
                element.innerHTML = `
                    <span style = "color: #${message.user.hex};${hide_author ? 'color: transparent;' : ''}">${message.user.name}</span>
                    <span class = "${classlist}">${attachment}</span>
                    <span class = "timestamp"${current_time !== last_time ? ' style="color: transparent;"' : ''}>${current_time}</span>
                `;

                // Push message and autoscroll
                const chat = document.querySelector(".chat");
                chat.appendChild(element);
                chat.scrollTop = chat.scrollHeight;

                // Handle notification sound
                if (!document.hasFocus()) NOTIFICATION_SFX.play();
            },
            handle_member: (event_type, member) => {
                const member_list = document.querySelector(".member-list");
                const existing_member = document.querySelector(`[data-member = "${member.name}"]`);
                if (event_type === "leave") {
                    if (existing_member) existing_member.remove();
                    return;
                }
                if (existing_member) return;

                // Handle element
                const element = document.createElement("span");
                element.innerHTML = `→ <span style = "color: #${member.hex}">${member.name}</span>`;
                element.setAttribute("data-member", member.name);
                member_list.appendChild(element);
            }
        }
    );

    // Handle loading spinner
    main.classList.add("loading");
    main.innerHTML = `<span class = "loader"></span> Connecting to ${address}...`;
})();
