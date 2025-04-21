from flask import Flask, request, jsonify, make_response, render_template
import sqlite3
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True) 
DB_FILE = 'visits.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS counter (
                id INTEGER PRIMARY KEY,
                count INTEGER
            )
        ''')
        c.execute('INSERT OR IGNORE INTO counter (id, count) VALUES (1, 0)')
        conn.commit()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/count', methods=['GET'])
def count():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE counter SET count = count + 1 WHERE id = 1")
        conn.commit()
        cursor.execute("SELECT count FROM counter WHERE id = 1")
        updated_count = cursor.fetchone()[0]
        return jsonify({"count": updated_count})

if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        init_db()
    app.run(debug=True)
