import threading
import time
import random
import pyodbc
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# --- КОНФИГУРАЦИЯ ---
# Вставь сюда имя своего сервера!
YOUR_SERVER_NAME = r'DESKTOP-T9D302K\SQLEXPRESS' 

CONN_STR = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={YOUR_SERVER_NAME};'
    r'DATABASE=AESCULAPIUS;'
    r'Trusted_Connection=yes;'
)

SIMULATION_ACTIVE = False

def get_db_connection():
    try:
        return pyodbc.connect(CONN_STR)
    except Exception as e:
        print(f"DB CONNECTION ERROR: {e}")
        return None

# --- УЛУЧШЕННЫЙ ГЕНЕРАТОР ХАОСА ---
def chaos_engine():
    first_names = ["John", "Sarah", "Kyle", "Ellen", "Rick", "Morty", "Neo", "Trinity", "Arthur", "Ford", "Desmond", "Gordon"]
    last_names = ["Connor", "Ripley", "Deckard", "Stark", "Wayne", "Freeman", "Doe", "Smith", "Anderson", "Vader", "Skywalker"]
    
    while True:
        if SIMULATION_ACTIVE:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                
                # Генерация интересного имени
                code_name = f"{random.choice(first_names)} {random.choice(last_names)}"
                if random.random() < 0.2: # 20% шанс на "неизвестного"
                    code_name = f"Unknown Subject-{random.randint(1000,9999)}"

                age = random.randint(18, 90)
                
                # Баланс веротяностей (чтобы были разные цвета)
                roll = random.random()
                
                if roll < 0.05: # 5% BLACK (Смерть)
                    hr = 0
                    spo2 = 0
                    threat_id = 9 # Biological Decomposition
                elif roll < 0.30: # 25% RED (Критический)
                    hr = random.randint(140, 190)
                    spo2 = random.randint(60, 85)
                    threat_id = random.choice([5, 6, 7, 8]) 
                elif roll < 0.60: # 30% YELLOW (Средний)
                    hr = random.randint(90, 130)
                    spo2 = random.randint(88, 94)
                    threat_id = random.choice([3, 4])
                else: # 40% GREEN (Норма)
                    hr = random.randint(60, 90)
                    spo2 = random.randint(95, 100)
                    threat_id = random.choice([1, 2])

                try:
                    cursor.execute("""
                        INSERT INTO Subjects (CodeName, Age, HeartRate, SPO2, AssignedThreatID)
                        VALUES (?, ?, ?, ?, ?)
                    """, (code_name, age, hr, spo2, threat_id))
                    conn.commit()
                    print(f"[AUTO] New Subject: {code_name} (HR: {hr})")
                except Exception as e:
                    print(f"Insert Error: {e}")
                finally:
                    conn.close()
            
            # Рандомная пауза (от 1 до 4 секунд)
            time.sleep(random.uniform(1.0, 4.0))
        else:
            time.sleep(1)

threading.Thread(target=chaos_engine, daemon=True).start()

# --- МАРШРУТЫ (ROUTES) ---

@app.route('/')
def index():
    return render_template('terminal.html')

@app.route('/api/toggle_chaos', methods=['POST'])
def toggle_chaos():
    global SIMULATION_ACTIVE
    SIMULATION_ACTIVE = not SIMULATION_ACTIVE
    status = "ONLINE" if SIMULATION_ACTIVE else "OFFLINE"
    return jsonify({"status": status})

@app.route('/api/doctors')
def get_doctors():
    conn = get_db_connection()
    if not conn: return jsonify([])
    cursor = conn.cursor()
    cursor.execute("SELECT DoctorID, DocName FROM Doctors")
    doctors = [{"id": row.DoctorID, "name": row.DocName} for row in cursor.fetchall()]
    conn.close()
    return jsonify(doctors)

@app.route('/api/manual_entry', methods=['POST'])
def manual_entry():
    data = request.json
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Error"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Определяем параметры на основе выбранного цвета карты
        color = data.get('color')
        hr, spo2, threat_id = 80, 98, 1 # Default Green
        
        if color == 'BLACK':
            hr, spo2, threat_id = 0, 0, 9 # Death
        elif color == 'RED':
            hr, spo2, threat_id = 160, 70, 7 # Plague
        elif color == 'YELLOW':
            hr, spo2, threat_id = 115, 92, 3 # Fracture
        
        cursor.execute("""
            INSERT INTO Subjects (CodeName, Age, HeartRate, SPO2, AssignedThreatID, AssignedDoctorID, IsManualEntry)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (data['name'], 30, hr, spo2, threat_id, data['doctor_id']))
        
        conn.commit()
        print(f"[MANUAL] Added: {data['name']} as {color}")
        return jsonify({"success": True})
    except Exception as e:
        print(e)
        return jsonify({"success": False})
    finally:
        conn.close()

@app.route('/api/data')
def get_data():
    conn = get_db_connection()
    if not conn: return jsonify([])
    cursor = conn.cursor()
    
    # Берем ТОП 50 для скроллинга
    query = """
        SELECT TOP 50 
            S.CodeName, 
            T.ThreatName, 
            S.HeartRate, 
            S.StatusColor,
            D.DocName,
            R.RoomName,
            FORMAT(S.ArrivalTimestamp, 'HH:mm:ss') as TimeStr
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
            "name": row.CodeName,
            "diagnosis": row.ThreatName,
            "hr": row.HeartRate,
            "color": row.StatusColor,
            "doctor": row.DocName,
            "room": row.RoomName,
            "time": row.TimeStr
        })
    conn.close()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)