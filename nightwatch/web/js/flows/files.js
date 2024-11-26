// Copyright (c) 2024 iiPython

export default class FileHandler {
    constructor() {
        this.mimetypes = {
            "js": "Javascript",
            "jpg": "JPEG",
            "py": "Python",
            "rs": "Rust",
            "zip": "Archive",
            "gz": "Gzip",
            "tar.gz": "Gzip Archive",
            "tar.xz": "XZ Archive",
            "7z": "7-zip Archive"
        };
        this.pending_uploads = [];
    }
    mimetype(filename) {
        const extension = filename.match(/\.([a-z0-9]+(?:\.[a-z0-9]+)*)$/i);
        if (!extension) return "binary";
        return this.mimetypes[extension[0].slice(1).toLowerCase()] || extension[0].slice(1).toUpperCase();
    }
    setup(address, connection) {
        this.address = address, this.connection = connection;

        // Fetch elements
        const pending_element = document.querySelector(".pending-uploads");

        // Handle pasting
        document.addEventListener("paste", (e) => {
            const files = e.clipboardData?.items;
            if (!files) return;
        
            // Select first file
            const item = files[0];
            if (item.kind === "string") return;
            // if (!item.type.startsWith("image/"))
                // return;  // Yes, I support non-image uploads but for now pasting is image only.
        
            const file = item.getAsFile();
            
            // Add to pending list
            const pending_div = document.createElement("div");
            const upload_data = { file, div: pending_div };

            pending_div.innerHTML = `<div><span></span><button>x</button></div><em>Prepared to send</em>`;
            pending_div.querySelector("span").innerText = file.name;
            pending_div.querySelector("button").addEventListener("click", () => {
                this.pending_uploads.splice(this.pending_uploads.indexOf(upload_data), 1);
                pending_div.remove();
            });
            this.pending_uploads.push(upload_data);
            pending_element.appendChild(pending_div);
        });
    }
    async upload_pending() {
        const CHUNK_SIZE = 5 * (1024 ** 2);  // 5MB for the time being...
        for (const { file, div } of this.pending_uploads) {
            const response = await (await fetch(
                `${this.address}/api/file`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name: file.name, size: file.size })
                }
            )).json();
            if (response.code !== 200) { console.error(response); continue; }

            // Start sending file
            let total_sent = 0;
            for (let start = 0; start < file.size; start += CHUNK_SIZE) {
                await new Promise((resolve, reject) => {
                    const loader = new FileReader();
                    loader.addEventListener("load", async (e) => {
                        const form = new FormData();
                        form.append("upload", new Blob([e.target.result]));

                        // Setup XHR request
                        const xhr = new XMLHttpRequest();
                        xhr.upload.addEventListener("progress", (e) => {
                            div.querySelector("em").innerText = `${Math.min(Math.round(((total_sent + e.loaded) / file.size) * 100), 100)}%`;
                            if (e.loaded / e.total === 1) total_sent += e.total;
                        });
                        xhr.addEventListener("load", resolve);
                        xhr.addEventListener("error", reject);
                        xhr.addEventListener("error", reject);
                        xhr.addEventListener("loadend", (e) => { if (e.target.status !== 200) reject(); });
                        
                        // Send to RICS
                        xhr.open("POST", `${this.address}/api/file/${response.data.file_id}`, true);
                        xhr.send(form);
                    });
                    loader.readAsArrayBuffer(file.slice(start, start + CHUNK_SIZE));
                });
            }

            // Handle results
            this.pending_uploads.splice(this.pending_uploads.indexOf({ file, div }, 1));
            const result = await (await fetch(`${this.address}/api/file/${response.data.file_id}/finalize`, { method: "POST" })).json();
            setTimeout(() => div.remove(), 1000);
            if (result.code !== 200) return console.error(result);
            await this.connection.send({ type: "message", data: { message: `${this.address}/file/${result.data.path}` } });
        }
    }
}
