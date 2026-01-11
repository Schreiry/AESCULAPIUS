# -- import space --- 
import threading
import time
import random
import pyodbc
import csv
import io
from flask import Flask, render_template, jsonify, request, make_response

# --- --- --- --- --- --- --- 

app = Flask(__name__)

# --- Server Configuration ---
# YOUR_SERVER_NAME = r'DESKTOP-T9D302K\SQLEXPRESS' 
YOUR_SERVER_NAME = r'DGSurface\SQLEXPRESS' 

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

# --- Generation Various Patients ---
def chaos_engine():
    first_names = [
    "Jessica","Hugo","Estelle","Inès","Anny","Masha","Konstantin","Vera","Natalya","Polina","Liza","Pavel","Karamazov","Alexey","Nikolai","Nastasya","Lev","Andrey","Pyotr","Arkady","Pulcheria","Sofya","Rodion",
    "Fyodor","Evelyn","Panam","Judy","Goro","Viktor","Johnny","Jackie","Lawan","Hakon","Jade","Aiden","Kyle","Colonel","Artyom","Vesemir",
    "Yennefer","Triss","Ciri","Geralt","Victor","Zina","Makar", "Varvara", "Katerina", "Leo", 
    "Larisa","Dmitry","Sergey","Anton","Corvo","Grigori","Eli","Gordon","Lorenzo","Alex","Morgan","Ish","Riley","Marlene","Bill",
    "Frank","Jordan","Nora","Manny","Mel","Owen","Dina","Maria","Isaac","Henry","Jerry","Servopoulos","Tess",
    "Tommy","Abby","Ellie","Joel","Aline","Esquie","Sophie","Monoco","Verso","Sciel","Albert",
    "Antoine","Jean-Paul","Jean-Jacques","Gustave","Maëlle","Mikhail","Anni-Frid","Benny","Bjorn",
    "Agnetha","Tamara","Mira", "Alexandre","James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Shirley", "Eric", "Angela", "Jonathan", "Helen", "Stephen", "Anna",
    "Larry", "Brenda", "Justin", "Pamela", "Scott", "Nicole", "Brandon", "Emma"
    ]
    last_names = [
    "Barine","Rigault","Serrano","Garcin","Mercier","Roquentin","Ivanovich","Irtenyev","Levin","Vronsky","Karenin","Karenina","Rostova","Rostov","Tolstoy","Orlov","Devushkin","Alexandrovna","Zverkov","Smerdyakov","Kirillov","Verkhovensky","Stavrogin","Barashkova","Myshkin","Zosimov","Greve","Ivanovna","Marmeladov",
    "Luzhin","Svidrigailov","Razumikhin","Marmeladova","Raskolnikov","Dostoevsky","Palmer","Alvarez","Takemura","Vektor","Silverhand","Welles","Marwey",
    "Caldwell","Crane","Miller","Mel'nikova","Vengerberg","Merigold","Sechenov","Nechayev","Sokolov","Kaldwin","Attano",
    "Kleiner","Vance","Freeman","Calvino","Elazar","Yu","Dixon","Burrell","Miller","Renoir","Camus","de Saint-Exupéry",
    "Sartre","Rousseau","Verne","Borde","Gorshenev","Lyngstad","Andersson","Unveaus","Faltskog","Mizandari","Tinikashvili",
    "Putkaradze","Tsurtsumia","Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker"
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
        time.sleep(random.uniform(0.5, 2.0)) # Чуть ускорил генерацию для заполнения строк

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
    if not conn: 
        print("[MANUAL ERROR] Database connection failed")
        return jsonify({"success": False, "error": "Database unavailable"})
    
    try:
        cursor = conn.cursor()
        # Маппируем цвета на реальные ThreatID из БД:
        # Green = 1 (Mild Influenza - низкий риск)
        # Yellow = 2 (Panic Attack - средний риск)
        # Red = 3 (Fracture - высокий риск)
        # Black = 5 (Radiation Sickness - критический)
        threat_map = {'Green': 1, 'Yellow': 2, 'Red': 3, 'Black': 5}
        threat_id = threat_map.get(data.get('color'), 1)
        
        # Валидация данных
        if not data.get('name') or not data.get('name').strip():
            print("[MANUAL ERROR] Empty name provided")
            return jsonify({"success": False, "error": "Patient name cannot be empty"})
        
        try:
            doctor_id = int(data.get('doctor_id', 1))
        except (ValueError, TypeError):
            print(f"[MANUAL ERROR] Invalid doctor_id: {data.get('doctor_id')}")
            return jsonify({"success": False, "error": "Invalid doctor selection"})

        query = """
            INSERT INTO Subjects (CodeName, AssignedThreatID, AssignedDoctorID, AssignedRoomID, HeartRate, SPO2)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (data['name'].strip(), threat_id, doctor_id, 1, 80, 98))
        conn.commit()
        print(f"[MANUAL] Added: {data['name']} with ThreatID={threat_id}, DoctorID={doctor_id}")
        return jsonify({"success": True})
    except pyodbc.IntegrityError as e:
        print(f"[MANUAL ERROR] Integrity constraint: {e}")
        return jsonify({"success": False, "error": f"Database constraint error: {str(e)[:100]}"})
    except Exception as e:
        print(f"[MANUAL ERROR] {type(e).__name__}: {e}")
        return jsonify({"success": False, "error": f"Error: {str(e)[:100]}"})
    finally:
        conn.close()

# --- API ДЛЯ МОНИТОРА  ---
@app.route('/api/data')
def get_data():
    conn = get_db_connection()
    if not conn: return jsonify([])
    
    try:
        cursor = conn.cursor()
        # ЗДЕСЬ МЫ БЕРЕМ 100 СТРОК
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
        # ЗДЕСЬ МЫ БЕРЕМ 10000 СТРОК 
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