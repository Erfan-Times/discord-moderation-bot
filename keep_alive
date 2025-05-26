from flask import Flask, request
from threading import Thread
from datetime import datetime

app = Flask('')

@app.route('/')
def home():
    ip = request.remote_addr
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] Ping received from {ip}")

    return '✅ Times Bot is alive!'

def run():
    app.run(host='0.0.0.0', port=3000)

def keep_alive():
    t = Thread(target=run)
    t.start()
