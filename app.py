import threading
import time
import random
import pyodbc
import csv
import io
from functools import wraps
from flask import Flask, render_template, jsonify, request, make_response, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'OMEGA_PROTOCOL_SECRET_KEY_XY99' 

# --- Server Configuration ---
YOUR_SERVER_NAME = r'DESKTOP-T9D302K\SQLEXPRESS' 
# YOUR_SERVER_NAME = r'DGSurface\SQLEXPRESS' 

CONN_STR = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={YOUR_SERVER_NAME};'
    r'DATABASE=AESCULAPIUS;'
    r'Trusted_Connection=yes;'
    r'TrustServerCertificate=yes;' 
)

SIMULATION_ACTIVE = True  # Auto-start data generation

def get_db_connection():
    try:
        conn = pyodbc.connect(CONN_STR, timeout=5)
        print("[SQL] Connection successful")
        return conn
    except Exception as e:
        print(f"[SQL ERROR] Connection failed: {e}")
        return None

# --- Security Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] not in allowed_roles:
                return jsonify({'error': 'ACCESS DENIED: Insufficient Clearance Level'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- CHAOS ENGINE (UPDATED WITH FULL NAMES) ---
def chaos_engine():
    print("[CHAOS ENGINE] Started successfully")
    first_names = [
        "Lasha","Valeri","Elene","Gvanca","Vaxtang","Usain","Keanu","Leopold","Flamma","Fides","Maximus","Max",
        "Maxima","Caecilia","Fausta","Serena","Luna","Aurora","Vesta","Minerva","Constantia","Sapientia","Aemilia",
        "Octavia","Domitia","Antonia","Livia","Valeria","Flavia","Cornelia","Claudia","Jonas","Daru","Fernand","Yvars",
        "Marcel","Janine","Lucie","Zagreus","Patrice","Victoria","Diego","Anya","Dora","Stephan","Stepan","Ianus","Jan","Martha","Metellus","Helicon","Caesonia","Scipio","Cherea",
        "Caligula","Jean-Baptiste","Sisyphus","Cottard","Jean","Raymond","Marie","Meursault","Jessica",
        "Hugo","Estelle","Inès","Anny","Masha","Konstantin","Vera","Natalya","Polina","Liza","Pavel","Alexey","Nikolai","Nastasya","Lev","Andrey","Pyotr","Arkady","Pulcheria","Sofya","Rodion",
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
        "Maxima","Torquatus","Silvanus","Varro","Lentulus","Agrippa","bolt","Reeves","Mersault","Skouratov","Doulebov","Kaliayev","Clamence","Grand","Tarrou","Sintès","Cardona","Karamazov","Barine",
        "Rigault","Serrano","Garcin","Mercier","Roquentin","Ivanovich","Irtenyev","Levin","Vronsky",
        "Karenin","Karenina","Rostova","Rostov","Tolstoy","Orlov","Devushkin","Alexandrovna","Zverkov","Smerdyakov","Kirillov","Verkhovensky","Stavrogin","Barashkova",
        "Myshkin","Zosimov","Greve","Ivanovna","Marmeladov","Voinov", "Livius", "Fabius", "Cassius", "Augustus", "Regulus", "Princeps",
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
                    
                    if random.random() < 0.3:
                        fname = random.choice(first_names)
                        lname = random.choice(last_names)
                        name = f"{fname} {lname}" 
                        
                        # 35% GREEN (ThreatID 1-2), 30% YELLOW (ThreatID 3-4), 25% RED (ThreatID 5-7), 10% BLACK (ThreatID 8-10)
                        threat_roll = random.random()
                        if threat_roll < 0.35:
                            threat = random.choice([1, 2])  # Green threats
                            hr = random.randint(60, 100)  # Normal heart rate
                            spo2 = random.randint(95, 100)  # High oxygen saturation
                        elif threat_roll < 0.65:
                            threat = random.choice([3, 4])  # Yellow threats
                            hr = random.randint(100, 130)  # Elevated heart rate
                            spo2 = random.randint(85, 95)  # Moderate oxygen
                        elif threat_roll < 0.90:
                            threat = random.choice([5, 6, 7])  # Red threats
                            hr = random.randint(140, 160)  # High heart rate - TRIGGERS RED
                            spo2 = random.randint(65, 75)  # Low oxygen - TRIGGERS RED
                        else:
                            threat = random.choice([8, 9, 10])  # Black threats
                            hr = random.randint(0, 40) if random.random() < 0.3 else random.randint(160, 180)  # Cardiac arrest or extreme HR
                            spo2 = random.randint(40, 65)  # Critical oxygen levels
                        
                        doc = random.randint(1, 5)  # 5 doctors in DB
                        room = random.randint(1, 6)  # 6 rooms in DB
                        
                        cursor.execute("""
                            INSERT INTO Subjects (CodeName, AssignedThreatID, AssignedDoctorID, AssignedRoomID, HeartRate, SPO2)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (name, threat, doc, room, hr, spo2))
                        conn.commit()
                        threat_names = {1:"Mild Influenza", 2:"Panic Attack", 3:"Fracture", 4:"Chemical Burn", 5:"Radiation", 6:"Viral", 7:"Plague", 8:"Arrest", 9:"Decomp", 10:"Neural"}
                        print(f"[CHAOS ENGINE] Inserted: {name} (Threat: {threat_names.get(threat, 'Unknown')}) HR:{hr} SPO2:{spo2}")
                    
                    cursor.execute("UPDATE Subjects SET HeartRate = HeartRate + CAST((RAND()*10)-5 AS INT), SPO2 = SPO2 + CAST((RAND()*4)-2 AS INT)")
                    conn.commit()
                    conn.close()
                except Exception as e:
                    print(f"[CHAOS ENGINE ERROR] {e}")
                    if conn: conn.close()
            else:
                print("[CHAOS ENGINE WARNING] Could not connect to database")
        time.sleep(3) 

t = threading.Thread(target=chaos_engine, daemon=True)
t.start()

# --- ROUTES ---

@app.route('/')
def index():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT UserID, Role, DisplayName FROM Users WHERE Username=? AND PasswordHash=?", (username, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user.UserID
                session['role'] = user.Role
                session['name'] = user.DisplayName
                return redirect(url_for('dashboard'))
            else:
                error = "INVALID CREDENTIALS. ACCESS DENIED."
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('terminal.html', user_role=session['role'], user_name=session['name'])

# --- API ---

@app.route('/api/toggle_sim', methods=['POST'])
@login_required
@role_required(['Manager'])
def toggle_sim():
    global SIMULATION_ACTIVE
    SIMULATION_ACTIVE = not SIMULATION_ACTIVE
    return jsonify({'status': SIMULATION_ACTIVE})

@app.route('/api/data')
@login_required
def get_data():
    conn = get_db_connection()
    if not conn: return jsonify({'error': 'DB Connection Lost'}), 500
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 50 
            S.SubjectID, S.CodeName, T.ThreatName, S.StatusColor, S.HeartRate, S.SPO2, 
            D.DocName, R.RoomName, S.ArrivalTimestamp,
            S.AssignedThreatID, S.AssignedDoctorID, S.AssignedRoomID
        FROM Subjects S
        JOIN BioThreats T ON S.AssignedThreatID = T.ThreatID
        LEFT JOIN Doctors D ON S.AssignedDoctorID = D.DoctorID
        LEFT JOIN Rooms R ON S.AssignedRoomID = R.RoomID
        ORDER BY S.ArrivalTimestamp DESC
    """)
    rows = cursor.fetchall()
    patients = [list(row) for row in rows] 
    
    cursor.execute("SELECT DoctorID, DocName FROM Doctors")
    doctors = [{'id': r[0], 'name': r[1]} for r in cursor.fetchall()]
    
    cursor.execute("SELECT RoomID, RoomName FROM Rooms")
    rooms = [{'id': r[0], 'name': r[1]} for r in cursor.fetchall()]
    
    cursor.execute("SELECT ThreatID, ThreatName FROM BioThreats")
    threats = [{'id': r[0], 'name': r[1]} for r in cursor.fetchall()]

    conn.close()
    return jsonify({
        'patients': patients, 
        'doctors': doctors,
        'rooms': rooms,
        'threats': threats,
        'sim_status': SIMULATION_ACTIVE,
        'user_role': session['role']
    })

@app.route('/api/add_patient', methods=['POST'])
@login_required
@role_required(['Registrar', 'Manager'])
def add_patient():
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Subjects (CodeName, AssignedDoctorID, AssignedThreatID, AssignedRoomID, HeartRate, SPO2)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.get('name', 'Unknown Subject'), 
            data.get('doctor_id'), 
            data.get('threat_id'),
            data.get('room_id'),
            data.get('hr', 80),
            data.get('spo2', 98)
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Add Patient Error: {e}")
        return jsonify({'success': False}), 500

@app.route('/api/update_patient', methods=['POST'])
@login_required
@role_required(['Admin', 'Manager'])
def update_patient():
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Subjects
            SET CodeName = ?, AssignedDoctorID = ?, AssignedThreatID = ?, AssignedRoomID = ?, HeartRate = ?, SPO2 = ?
            WHERE SubjectID = ?
        """, (data['name'], data['doctor_id'], data['threat_id'], data['room_id'], data['hr'], data['spo2'], data['subject_id']))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False}), 500

@app.route('/api/delete_patient', methods=['POST'])
@login_required
@role_required(['Admin', 'Manager'])
def delete_patient():
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Subjects WHERE SubjectID = ?", (data['subject_id'],))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False}), 500

@app.route('/api/export')
@login_required
def export_data():
    conn = get_db_connection()
    if not conn: return "Database Error", 500
    try:
        cursor = conn.cursor()
        query = """
            SELECT TOP 1000 S.SubjectID, S.CodeName, T.ThreatName, S.StatusColor, S.HeartRate, S.SPO2, D.DocName, R.RoomName, S.ArrivalTimestamp
            FROM Subjects S JOIN BioThreats T ON S.AssignedThreatID = T.ThreatID
            LEFT JOIN Doctors D ON S.AssignedDoctorID = D.DoctorID
            LEFT JOIN Rooms R ON S.AssignedRoomID = R.RoomID
            ORDER BY S.ArrivalTimestamp DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['ID', 'Patient Name', 'Diagnosis', 'Threat Level', 'HR', 'SPO2', 'Doctor', 'Location', 'Time'])
        for row in rows: cw.writerow(row)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=bio_logs.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)