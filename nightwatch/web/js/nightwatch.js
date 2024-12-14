// Copyright (c) 2024 iiPython

import FileHandler from "./flows/files.js";
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
const FILE_HANDLER = new FileHandler();

(async () => {
    const { username, hex, address } = await grab_data();

    // Keep track of the last message
    let last_author, last_time;

    // Connection screen
    const connection = new ConnectionManager(
        { username, hex, address },
        {
            on_problem: ({ type, data }) => {
                main.classList = "loading", main.style.width = "520px";
                switch (type) {
                    case "outdated-version":
                        main.innerHTML = `This client is too new to connect.<br>RICS version ${data.version}, client version >= ${data.supported}`;
                        break;

                    case "unknown-version":
                        main.innerHTML = `Trying to fetch the RICS version failed.<br>The server might be offline, or it might be too old.`;
                        break;

                    case "generic":
                        main.innerHTML = data;
                        break;
                }
                if (connection.websocket.readyState === WebSocket.OPEN) {
                    connection.websocket.close(1000, "The client is terminating this connection due to protocol error.");
                    connection.callbacks.on_problem = () => {};  // Silence the close message
                };
                console.error(type, data);
            },
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
                        <div class = "member-list"><p></p></div>
                        <div class = "pending-uploads"></div>
                        <hr>
                        <div class = "user-data">
                            <p>Connected as <span style = "color: #${hex};">${username}</span>.</p>
                        </div>
                    </div>
                `;

                // Handle file uploads
                FILE_HANDLER.setup(`http${connection.protocol}://${address}`, connection);

                // Handle sending
                const input = document.getElementById("actual-input");
                function send_message() {
                    FILE_HANDLER.upload_pending();

                    // Process text
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
            on_message: async (message) => {
                const current_time = TIME_FORMATTER.format(new Date(message.time * 1000));

                // Check for anything hidden
                const hide_author = message.user.name === last_author;

                // Construct text/attachment
                let attachment = message.message, classlist = "message-content";

                const file_match = attachment.match(new RegExp(`^https?:\/\/${address}\/file\/([a-zA-Z0-9_-]{21})\/.*$`));
                if (!file_match && attachment.toLowerCase().match(/^https:\/\/[\w\d./-]+.(?:avifs?|a?png|jpe?g|jfif|webp|ico|gif|svg)(?:\?.+)?$/)) {
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
                        classlist += " padded";
                        image.src = `http${connection.protocol}://${address}/api/fwd/${btoa(image.src.slice(8)).replace(/\//, "_")}`;
                        attachment = dom.body.innerHTML;
                    };
                };

                // Construct message
                const element = document.createElement("div");
                element.classList.add("message");
                element.innerHTML = `
                    <span style = "color: #${message.user.hex};${hide_author ? 'color: transparent;' : ''}">${message.user.name}</span>
                    <span class = "${classlist}">${file_match ? "Loading attachment..." : attachment}</span>
                    <span class = "timestamp"${current_time === last_time ? ' style="color: transparent;"' : ''}>${current_time}</span>
                `;

                // Push message and autoscroll
                const chat = document.querySelector(".chat");
                chat.appendChild(element);
                chat.scrollTop = chat.scrollHeight;
                last_author = message.user.name, last_time = current_time;

                // Handle notification sound
                if (!document.hasFocus()) NOTIFICATION_SFX.play();

                // Check for files
                if (file_match) {
                    function bytes_to_human(size) {
                        const i = size == 0 ? 0 : Math.floor(Math.log(size) / Math.log(1024));
                        return +((size / Math.pow(1024, i)).toFixed(2)) * 1 + " " + ["B", "kB", "MB", "GB"][i];
                    }

                    const response = await (await fetch(`http${connection.protocol}://${address}/api/file/${file_match[1]}/info`)).json();
                    if (response.code === 200) {
                        const message = element.querySelector(".message-content");
                        const mimetype = FILE_HANDLER.mimetype(response.data.name);
                        if (["avif", "avifs", "png", "apng", "jpg", "jpeg", "jfif", "webp", "ico", "gif", "svg"].includes(mimetype.toLowerCase())) {
                            message.innerHTML = `<a href = "${attachment}" target = "_blank"><img alt = "${response.data.name}" src = "${attachment}"></a>`;
                        } else {
                            message.innerHTML = `<div class = "file">
                                <div><span>${response.data.name}</span> <span>${mimetype}</span></div>
                                <div><span>${bytes_to_human(response.data.size)}</span> <button>Download</button></div>
                            </div>`;
                            message.querySelector("button").addEventListener("click", () => { window.open(attachment, "_blank"); });
                        }
                        message.classList.add("padded");
                    }
                }
            },
            handle_member: (event_type, member) => {
                const member_list = document.querySelector(".member-list");
                const existing_member = document.querySelector(`[data-member = "${member.name}"]`);

                const update = () => member_list.querySelector("p").innerText = `Members ─ ${member_list.querySelectorAll("& > span").length}`;

                if (event_type === "leave") {
                    if (existing_member) existing_member.remove();
                    return update();
                }
                if (existing_member) return;

                // Handle element
                const element = document.createElement("span");
                element.innerHTML = `→ <span style = "color: #${member.hex}">${member.name}</span>`;
                element.setAttribute("data-member", member.name);
                member_list.appendChild(element);
                update();
            }
        }
    );

    // Handle loading spinner
    main.classList.add("loading");
    main.innerHTML = `<span class = "loader"></span> Connecting to ${address}...`;
})();
