from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from urllib.parse import parse_qs

DATA_FILE = "/data/data.txt"

class SimpleApp(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            content = f"""
            <html>
            <body>
                <h2>Dummy Storage App</h2>
                <form method="POST" action="/save">
                    <input type="text" name="message" placeholder="Input something" required/>
                    <button type="submit">Save</button>
                </form>
                <br>
                <a href="/data">View Stored Data</a>
            </body>
            </html>
            """
            self.wfile.write(content.encode())

        elif self.path == "/data":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r") as f:
                    self.wfile.write(f.read().encode())
            else:
                self.wfile.write(b"No data yet.")

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
    print("Starting server on port 8080...")
    server.serve_forever()
