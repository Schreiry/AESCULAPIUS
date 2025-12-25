import threading
import time
import random
import pyodbc
import csv
import io
from flask import Flask, render_template, jsonify, request, make_response

app = Flask(__name__)

# --- КОНФИГУРАЦИЯ ---
YOUR_SERVER_NAME = r'DESKTOP-T9D302K\SQLEXPRESS' 

CONN_STR = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={YOUR_SERVER_NAME};'
    r'DATABASE=AESCULAPIUS;'
    r'Trusted_Connection=yes;'
    r'TrustServerCertificate=yes;' 
)

SIMULATION_ACTIVE = False

def get_db_connection():
    try:
        return pyodbc.connect(CONN_STR, timeout=5)
    except Exception as e:
        print(f"[SQL ERROR] Connection failed: {e}")
        return None

# --- ГЕНЕРАТОР ХАОСА ---
def chaos_engine():
    first_names = [
        "John", "Sarah", "Kyle", "Ellen", "Rick", "Morty", "Neo", "Trinity", "Arthur", "Ford", 
        "Desmond", "Gordon", "Alyx", "Lara", "Nathan", "Geralt", "Yennefer", "Triss", "Cirilla", "Vesemir",
        "Isaac", "Clarke", "Ripley", "Dutch", "Dillon", "Tyler", "Marla", "Jack", "Rose", "Forrest"
    ]
    last_names = [
        "Connor", "Ripley", "Deckard", "Stark", "Wayne", "Freeman", "Doe", "Smith", "Anderson", "Vader", 
        "Skywalker", "Potter", "Granger", "Weasley", "Durden", "Gump", "Bond", "Holmes", "Watson", "Moriarty"
    ]
    
    while True:
        if SIMULATION_ACTIVE:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    f_name = random.choice(first_names)
                    l_name = random.choice(last_names)
                    full_name = f"{f_name} {l_name}"
                    
                    threat_id = random.choices([1, 2, 3, 4], weights=[50, 30, 15, 5])[0]
                    doctor_id = random.randint(1, 20) 
                    room_id = random.randint(1, 6)
                    
                    if threat_id == 4:
                        hr = random.randint(0, 20); spo2 = random.randint(0, 50)
                    elif threat_id == 3:
                        hr = random.randint(140, 220); spo2 = random.randint(70, 85)
                    else:
                        hr = random.randint(60, 100); spo2 = random.randint(95, 100)

                    query = """
                        INSERT INTO Subjects (CodeName, AssignedThreatID, AssignedDoctorID, AssignedRoomID, HeartRate, SPO2)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(query, (full_name, threat_id, doctor_id, room_id, hr, spo2))
                    conn.commit()
                    print(f"[CHAOS] Generated: {full_name}")
                except Exception as e:
                    print(f"[CHAOS ERROR] {e}")
                finally:
                    conn.close()
        time.sleep(random.uniform(0.5, 2.0)) # Чуть ускорил генерацию для заполнения 1000 строк

chaos_thread = threading.Thread(target=chaos_engine, daemon=True)
chaos_thread.start()

@app.route('/')
def index():
    return render_template('terminal.html')

@app.route('/api/toggle_chaos', methods=['POST'])
def toggle_chaos():
    global SIMULATION_ACTIVE
    SIMULATION_ACTIVE = not SIMULATION_ACTIVE
    return jsonify({"status": SIMULATION_ACTIVE})

@app.route('/api/manual_entry', methods=['POST'])
def manual_entry():
    data = request.json
    conn = get_db_connection()
    if not conn: return jsonify({"success": False})
    
    try:
        cursor = conn.cursor()
        threat_map = {'Green': 1, 'Yellow': 2, 'Red': 3, 'Black': 4}
        threat_id = threat_map.get(data.get('color'), 1)

        query = """
            INSERT INTO Subjects (CodeName, AssignedThreatID, AssignedDoctorID, AssignedRoomID, HeartRate, SPO2)
            VALUES (?, ?, ?, 1, 80, 98)
        """
        cursor.execute(query, (data['name'], threat_id, data['doctor_id']))
        conn.commit()
        return jsonify({"success": True})
    except Exception:
        return jsonify({"success": False})
    finally:
        conn.close()

# --- API ДЛЯ МОНИТОРА (Показывает последние 100 для скорости) ---
@app.route('/api/data')
def get_data():
    conn = get_db_connection()
    if not conn: return jsonify([])
    
    try:
        cursor = conn.cursor()
        # Показываем 100 последних на экране, чтобы браузер не тормозил
        query = """
            SELECT TOP 100 
                S.CodeName, T.ThreatName, S.HeartRate, S.StatusColor,
                D.DocName, R.RoomName, FORMAT(S.ArrivalTimestamp, 'HH:mm:ss') as TimeStr
            FROM Subjects S
            JOIN BioThreats T ON S.AssignedThreatID = T.ThreatID
            LEFT JOIN Doctors D ON S.AssignedDoctorID = D.DoctorID
            LEFT JOIN Rooms R ON S.AssignedRoomID = R.RoomID
            ORDER BY S.ArrivalTimestamp DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "name": row.CodeName, "diagnosis": row.ThreatName, "hr": row.HeartRate,
                "color": row.StatusColor, "doctor": row.DocName or "UNKNOWN",
                "room": row.RoomName or "CORRIDOR", "time": row.TimeStr
            })
        return jsonify(results)
    finally:
        conn.close()

# --- НОВЫЙ МАРШРУТ: ЭКСПОРТ В EXCEL (CSV) ---
@app.route('/api/export')
def export_data():
    conn = get_db_connection()
    if not conn: return "Database Error", 500
    
    try:
        cursor = conn.cursor()
        # ЗДЕСЬ МЫ БЕРЕМ 1000 СТРОК (Или даже больше, если хочешь)
        query = """
            SELECT TOP 1000 
                S.SubjectID, S.CodeName, T.ThreatName, S.StatusColor, 
                S.HeartRate, S.SPO2, D.DocName, R.RoomName, S.ArrivalTimestamp
            FROM Subjects S
            JOIN BioThreats T ON S.AssignedThreatID = T.ThreatID
            LEFT JOIN Doctors D ON S.AssignedDoctorID = D.DoctorID
            LEFT JOIN Rooms R ON S.AssignedRoomID = R.RoomID
            ORDER BY S.ArrivalTimestamp DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Создаем CSV файл в памяти
        si = io.StringIO()
        cw = csv.writer(si)
        # Заголовки для Excel
        cw.writerow(['ID', 'Patient Name', 'Diagnosis', 'Threat Level', 'HR (BPM)', 'SPO2 (%)', 'Assigned Doctor', 'Location', 'Timestamp'])
        
        for row in rows:
            cw.writerow(row)

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=aesculapius_logs_1000.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    finally:
        conn.close()

if __name__ == '__main__':
    print(">>> AESCULAPIUS v2.1 (STORAGE EXPANDED)")
    app.run(debug=True, port=5000)