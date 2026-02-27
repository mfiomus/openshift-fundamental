from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from urllib.parse import parse_qs

DATA_FILE = "/data/data.txt"

class SimpleApp(BaseHTTPRequestHandler):

    def do_GET(self):

        # ===== MAIN PAGE (UNCHANGED) =====
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            content = """
            <html>
            <body>
                <h2>Sebutkan Nama-Nama Ikan</h2>
                <form method="POST" action="/save">
                    <input type="text" name="message" placeholder="Input something" required/>
                    <button type="submit">Save</button>
                </form>
                <br>
                <a href="/data">View Stored Data</a>
                <br><br>
                <a href="/config-env">Config ENV</a>
                <br>
                <a href="/config-file">Config FILE</a>
            </body>
            </html>
            """
            self.wfile.write(content.encode())

        # ===== VIEW STORED DATA =====
        elif self.path == "/data":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r") as f:
                    self.wfile.write(f.read().encode())
            else:
                self.wfile.write(b"No data yet.")

        # ===== CONFIG VIA ENV VAR =====
        elif self.path == "/config-env":
            config_value = os.getenv("APP_CONFIG")

            if not config_value:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"ConfigMap (env) not configured.")
                return

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(config_value.encode())

        # ===== CONFIG VIA FILE MOUNT =====
        elif self.path == "/config-file":
            try:
                with open("/config/config.txt", "r") as f:
                    content = f.read()
            except Exception:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"ConfigMap (file) not mounted.")
                return

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(content.encode())

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    # ===== SAVE DATA =====
    def do_POST(self):
        if self.path == "/save":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            parsed = parse_qs(post_data.decode())
            message = parsed.get("message", [""])[0]

            os.makedirs("/data", exist_ok=True)

            with open(DATA_FILE, "a") as f:
                f.write(message + "\n")

            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")


if __name__ == "__main__":
    os.makedirs("/data", exist_ok=True)
    server = HTTPServer(("0.0.0.0", 8080), SimpleApp)
    print("Starting server on port 8080...")
    server.serve_forever()
