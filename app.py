from flask import Flask, request, jsonify, render_template
import sqlite3
import os
from datetime import datetime
from flask_cors import CORS
import pytz
import user_agents

app = Flask(__name__)
CORS(app, supports_credentials=True)

now = datetime.now(pytz.timezone("Asia/Bangkok")).isoformat()

DB_FILE = 'count.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS visitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE,
                createdate TEXT,
                device TEXT,
                browser TEXT,
                os TEXT
            )
        ''')

        conn.commit()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/gonenaza555+')
def dashboard():
    return render_template("dashboard.html")

@app.route('/count', methods=['POST'])
def count():
    data = request.get_json()
    uuid = data.get("uuid")
    if not uuid:
        return jsonify({"error": "UUID is required"}), 400

    user_agent_string = request.headers.get('User-Agent', '')
    ua = user_agents.parse(user_agent_string)

    device_type = "Mobile" if ua.is_mobile else "Tablet" if ua.is_tablet else "PC"
    browser = ua.browser.family
    os_name = ua.os.family

    now = datetime.now(pytz.timezone("Asia/Bangkok")).isoformat()

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM visitors WHERE uuid = ?", (uuid,))
        result = cursor.fetchone()

        if not result:
            # ถ้าไม่เคยเข้าเลย -> insert record ใหม่
            cursor.execute('''
                INSERT INTO visitors (uuid, createdate, device, browser, os)
                VALUES (?, ?, ?, ?, ?)
            ''', (uuid, now, device_type, browser, os_name))
            conn.commit()

        cursor.execute("SELECT COUNT(*) FROM visitors")
        total_visitors = cursor.fetchone()[0]

    return jsonify({"count": total_visitors})

@app.route('/count', methods=['GET'])
def get_count():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM visitors")
        total_visitors = cursor.fetchone()[0]

    return jsonify({"count": total_visitors})

@app.route('/visitor_data', methods=['GET'])
def visitor_data():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT strftime("%Y-%m-%d", createdate) AS date, COUNT(*) 
            FROM visitors
            GROUP BY date
            ORDER BY date ASC
        ''')
        data = cursor.fetchall()

    dates = [item[0] for item in data]
    counts = [item[1] for item in data]
    
    return jsonify({"dates": dates, "counts": counts})

@app.route('/visitor_detail', methods=['GET'])
def visitor_detail():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # Device
        cursor.execute('SELECT device, COUNT(*) FROM visitors GROUP BY device')
        device_data = dict(cursor.fetchall())

        # Browser
        cursor.execute('SELECT browser, COUNT(*) FROM visitors GROUP BY browser')
        browser_data = dict(cursor.fetchall())

        # OS
        cursor.execute('SELECT os, COUNT(*) FROM visitors GROUP BY os')
        os_data = dict(cursor.fetchall())

    return jsonify({
        "device": device_data,
        "browser": browser_data,
        "os": os_data
    })

if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        init_db()
    app.run(debug=True)
