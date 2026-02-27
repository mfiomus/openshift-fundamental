from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from urllib.parse import parse_qs

# === HARD REQUIREMENT SECRET (WILL CRASH IF MISSING) ===
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

DATA_FILE = "/data/data.txt"

class SimpleApp(BaseHTTPRequestHandler):

    def do_GET(self):

        # ===== MAIN PAGE =====
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            content = """
            <html>
            <body>
                <h2>Sebutkan Hewan Berkaki 2</h2>
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

        # ===== VIEW DATA =====
        elif self.path == "/data":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r") as f:
                    self.wfile.write(f.read().encode())
            else:
                self.wfile.write(b"No data yet.")

        # ===== CONFIG VIA ENV =====
        elif self.path == "/config-env":
            value = os.getenv("APP_CONFIG")

            if not value:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"ConfigMap ENV not configured.")
                return

            self.send_response(200)
            self.end_headers()
            self.wfile.write(value.encode())

        # ===== CONFIG VIA FILE =====
        elif self.path == "/config-file":
            try:
                with open("/config/config.txt", "r") as f:
                    content = f.read()
            except Exception:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"ConfigMap FILE not mounted.")
                return

            self.send_response(200)
            self.end_headers()
            self.wfile.write(content.encode())

        else:
            self.send_response(404)
            self.end_headers()

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

if __name__ == "__main__":
    os.makedirs("/data", exist_ok=True)
    server = HTTPServer(("0.0.0.0", 8080), SimpleApp)
    server.serve_forever()
