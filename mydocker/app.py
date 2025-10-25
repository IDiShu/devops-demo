import psycopg2
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

print("🚀 Запуск контейнера...", flush=True)

# Ждём готовность базы
while True:
    try:
        conn = psycopg2.connect(
            host="db",
            database="mydb",
            user="myuser",
            password="mypassword"
        )
        print("✅ Успешное подключение к PostgreSQL!", flush=True)
        conn.close()
        break
    except Exception as e:
        print("⏳ PostgreSQL ещё не готов... ждём...", flush=True)
        time.sleep(2)

print("🔥 Запускаю HTTP сервер...", flush=True)

# Мини веб-сервер
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hello! DB is connected and API is running!")

server = HTTPServer(("0.0.0.0", 8000), MyServer)
print("✅ HTTP сервер слушает на порту 8000", flush=True)
server.serve_forever()
