from flask import Flask, request, jsonify, render_template
import sqlite3
import os
from datetime import datetime
from flask_cors import CORS
import pytz

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
                createdate DATE
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

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # ตรวจสอบว่า UUID นี้เคยมีอยู่ใน DB หรือยัง
        cursor.execute("SELECT id FROM visitors WHERE uuid = ?", (uuid,))
        result = cursor.fetchone()

        if not result:
            now = datetime.now(pytz.timezone("Asia/Bangkok")).isoformat()
            cursor.execute("INSERT INTO visitors (uuid, createdate) VALUES (?, ?)", (uuid, now))
            conn.commit()

        # ดึงจำนวนผู้เข้าชมทั้งหมด (จำนวนแถวในตาราง visitors)
        cursor.execute("SELECT COUNT(*) FROM visitors")
        total_visitors = cursor.fetchone()[0]

    return jsonify({"count": total_visitors})

@app.route('/count', methods=['GET'])
def get_count():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # ดึงจำนวนผู้เข้าชมทั้งหมด (จำนวนแถวในตาราง visitors)
        cursor.execute("SELECT COUNT(*) FROM visitors")
        total_visitors = cursor.fetchone()[0]

    return jsonify({"count": total_visitors})

@app.route('/visitor_data', methods=['GET'])
def visitor_data():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # ดึงข้อมูลจำนวนผู้เข้าชมตามวันที่
        cursor.execute('''
            SELECT strftime("%Y-%m-%d", createdate) AS date, COUNT(*) 
            FROM visitors
            GROUP BY date
            ORDER BY date DESC
        ''')
        data = cursor.fetchall()

    # เตรียมข้อมูลในรูปแบบที่ Chart.js ต้องการ
    dates = [item[0] for item in data]
    counts = [item[1] for item in data]
    
    return jsonify({"dates": dates, "counts": counts})


if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        init_db()
    app.run(debug=True)
