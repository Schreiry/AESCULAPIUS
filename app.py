import threading
import time
import random
import pyodbc
import csv
import io
import datetime
from functools import wraps
from flask import Flask, render_template, jsonify, request, make_response, session, redirect, url_for

# --- Локальные импорты для безопасности ---
from config import SECRET_KEY
from security_utils import verify_password, encrypt_data, decrypt_data

app = Flask(__name__)
app.secret_key = SECRET_KEY 

# --- КОНФИГУРАЦИЯ СЕРВЕРА ---
# YOUR_SERVER_NAME = r'DESKTOP-T9D302K\SQLEXPRESS' 
YOUR_SERVER_NAME = r'DGSurface\SQLEXPRESS' 

CONN_STR = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={YOUR_SERVER_NAME};'
    r'DATABASE=AESCULAPIUS;'
    r'Trusted_Connection=yes;'
    r'TrustServerCertificate=yes;'
)

SIMULATION_ACTIVE = True 

# --- СПИСКИ ИМЕН ---
FIRST_NAMES = [
    "Giordano","Michel","Erasmus","Niccolò","Marsilio","Ibn Rushd ","Al-Farabi","Al-Kindi","Duns","Bonaventure","Roger","Anaxagoras","Tommaso","Blaise","Gottfried","Francis",
    "Empedocles","Pythagoras","Heraclitus","Anaximenes","Anaximander","Thales","Leni","Salomon","Nasty","Heinrich","Goetz","Franz","Karsky","René","Baruch","Nicolas",
    "Georges","Olga","Louis","Fred","Lizzie","Clochet","Landrieu","François","Canoris","Henri","Érinye","Clytemnestre","Égisthe","Mars","Jupiter","Électre","Oreste","Moses",
    "Lubéron","Pinette","Charlota","Pierre","Maurice","Millon","Jacques","Lola","Sorbier","Slick","Edmund","Elena","Werner","Johanna","Pablo","Ramon","Ève","Epicurus","Pyrrho","Chrysippus","Epictetus",
    "Boris","Mathieu","Marquis","Françoise","Auguste","Adolphe","Drusilla","Lucienne","Raymond","Marie","Meursault","Titus","Monty","Stephanie","Thaddeus","Lee","Sadie","Barb","Norm","Hank","Lucy","Yefim","Marthe","Rose",
    "Vadim","Irma","Murphy","Cait","Nick","Piper","Preston","Lasha","Valeri","Elene","Gvanca","Vaxtang","Usain","Keanu","Leopold","Flamma","Fides","Maximus","Max","Protagoras","Marcus",
    "Maxima","Caecilia","Fausta","Serena","Luna","Aurora","Vesta","Minerva","Constantia","Sapientia","Aemilia","Cooper","Catherine","Balducci","Rirette","Leucippus","Aristotle","Diogenes","Euclid",
    "Octavia","Domitia","Antonia","Livia","Valeria","Flavia","Cornelia","Claudia","Brunet","Daru","Fernand","Yvars","Scipion","Fernande","Gilbert","Democritus","Socrates","Platon","Aristippus",
    "Marcel","Janine","Lucie","Zagreus","Patrice","Victoria","Diego","Anya","Dora","Stephan","Stepan","Ianus","Jan","Martha","Metellus","Helicon","Caesonia","Scipio","Cherea","Rudolf",
    "Caligula","Jean-Baptiste","Sisyphus","Cottard","Jean","Raymond","Marie","Meursault","","Lepidus","Nada","Elisabeth","Germaine","Seneca","Cicero","Porphyry","Proclus","Boethius",
    "Hugo","Estelle","Inès","Anny","Masha","Konstantin","Vera","Natalya","Polina","Liza","Pavel","Alexey","Nikolai","Nastasya","Lev","Andrey","Pyotr","Arkady","Pulcheria","Sofya","Rodion",
    "Fyodor","Evelyn","Panam","Judy","Goro","Viktor","Johnny","Jackie","Lawan","Hakon","Jade","Aiden","Kyle","Colonel","Artyom","Vesemir","Julien Offray","Jean-François",
    "Yennefer","Triss","Ciri","Geralt","Victor","Zina","Makar", "Varvara", "Katerina", "Leo", "Esposito", "Socrate","Lemordant","Paul-Henri"," Immanuel","Derek",
    "Larisa","Dmitry","Sergey","Anton","Corvo","Grigori","Eli","Gordon","Lorenzo","Alex","Morgan","Ish","Riley","Marlene","Bill","Gilles","Dōgen","Nishida",
    "Frank","Jordan","Nora","Manny","Mel","Owen","Dina","Maria","Isaac","Henry","Jerry","Servopoulos","Tess","Anne-Marie","Roland","Nishitani",
    "Tommy","Abby","Ellie","Joel","Aline","Esquie","Sophie","Monoco","Verso","Sciel","Albert","Marcou","Franchot","Ferdinand",
    "Antoine","Jean-Paul","Jean-Jacques","Gustave","Maëlle","Mikhail","Anni-Frid","Benny","Bjorn","Tom","Voltaire","Gabriel",
    "Agnetha","Tamara","Mira", "Alexandre","James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica","Tetzel","Denis","Sergei",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa","Karl","Lulu","Arthur","Claude",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley","Léa","Friedrich","Simone",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle","Maud","Georg","Martin",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa","Jeremy ","Ludwig",
    "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon","Hans-Georg",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy","Herbert",
    "Nicholas", "Shirley", "Eric", "Angela", "Jonathan", "Helen", "Stephen", "Anna",
    "Larry", "Brenda", "Justin", "Pamela", "Scott", "Nicole", "Brandon", "Emma"
]

LAST_NAMES = [
    "Bruno","de Montaigne","More","Machiavelli","Ficino","of Ockham","Scotus","Bacon","Aquinas","of Miletus","Von Gerlach","Damby","Spinoza","Berkeley","de La Mettrie","Carnap",
    "Galles","Kean","Von Berlichingen","Hoederer","Clarke","Schneider","Montero","Serguine","Ivich","Campanella","Descartes","Pascal","Leibniz","Hume"," Montesquieu","Quine",
    "Delarue","De Rollebon","Salamano","Cardona","Clementine","Harper","Moldaver","Pearson","Howard","MacLean","Fleurier","Berliac","Diderot","Mendelssohn","Ryle","Rorty",
    "Bobrov","Codsworth","MacCready","Hancock","Deacon","Curie","Valentine","Garvey","Maxima","Sereno", "Ibbieta","Gris","Darbédat","Kant","Foucault","Lyotard","Dennett",
    "Torquatus","Silvanus","Varro","Lentulus","Agrippa","bolt","Reeves","Mersault","Skouratov","Doulebov","Mirbal","Malebranche","d'Holbach","Deleuze","Frege",
    "Kaliayev","Clamence","Grand","Tarrou","Sintès","Cardona","Karamazov","Barine","Sink","Wilzig","Jonas","Hilbert","Hobbes","Ingarden","Derrida","Althusser",
    "Rigault","Serrano","Garcin","Mercier","Roquentin","Ivanovich","Irtenyev","Levin","Vronsky","Paneloux","Aurelius","Locke","Lévi-Strauss","Lacan","Baudrillard",
    "Karenin","Karenina","Rostova","Rostov","Tolstoy","Orlov","Devushkin","Alexandrovna","Zverkov","Smerdyakov","Kirillov","Verkhovensky","Stavrogin","Barashkova",
    "Myshkin","Zosimov","Greve","Ivanovna","Marmeladov","Voinov", "Livius", "Fabius", "Cassius", "Augustus", "Regulus", "Princeps","Barthes","Kitarō",
    "Luzhin","Svidrigailov","Razumikhin","Marmeladova","Raskolnikov","Dostoevsky","Palmer","Alvarez","Takemura","Vektor","Silverhand","Welles","Marwey",
    "Caldwell","Crane","Miller","Mel'nikova","Vengerberg","Merigold","Sechenov","Nechayev","Sokolov","Kaldwin","Attano","Heidegger","Austin","Keiji",
    "Kleiner","Vance","Freeman","Calvino","Elazar","Yu","Dixon","Burrell","Miller","Renoir","Camus","de Saint-Exupéry","Husserl","Wittgenstein",
    "Sartre","Rousseau","Verne","Borde","Gorshenev","Lyngstad","Andersson","Unveaus","Faltskog","Mizandari","Tinikashvili","de Saussure",
    "Putkaradze","Tsurtsumia","Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis","Schelling","Dilthey",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Pérez","Bentham","Schopenhauer","Ricoeur",
    "Taylor", "Moore", "Jackson", "Jaspers", "Lee", "Perez", "Thompson", "White","Rambert","Fichte","Nietzsche","de Beauvoir",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young","Hartley","Comte","Marx","Bulgakov",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores","Reid","Hegel","Mill","Engels","Gadamer",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell","Spencer","Scheler","Merleau-Ponty","Ponty",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker"
]

# --- СЛОВАРЬ БОЛЕЗНЕЙ ---
FULL_THREAT_DICT = {
    1: "Mild Influenza",
    2: "Chronic Bronchitis", 3: "Fractured Rib", 4: "Concussion (Grade 1)", 5: "Severe Dehydration",
    6: "Heat Exhaustion", 7: "Hypothermia (Stage 1)", 8: "Food Poisoning", 9: "Allergic Reaction",
    10: "Sleep Deprivation Psychosis", 11: "Panic Attack", 12: "Laceration (Non-Arterial)",
    13: "Sprained Ankle", 14: "Migraine (Cluster)", 15: "Vertigo", 16: "Hyperventilation",
    17: "Low Blood Sugar", 18: "High Blood Pressure", 19: "Vitamin Deficiency", 20: "Exhaustion",
    21: "Arterial Bleeding", 22: "Punctured Lung", 23: "Neural Rot", 24: "Cyber-Psychosis",
    25: "Radiation Sickness (Acute)", 26: "Bio-Plague (Early Stage)", 27: "Internal Hemorrhage",
    28: "Compound Fracture", 29: "Kidney Failure", 30: "Cardiac Arrest Risk",
    31: "Severe Burns (3rd Degree)", 32: "Toxic Chemical Exposure", 33: "Blood Toxicity",
    34: "Cerebral Edema", 35: "Lung Collapse", 36: "Spinal Severance", 37: "Brain Aneurysm",
    38: "Flesh-Eating Bacteria", 39: "Parasitic Host", 40: "Cryo-Burn",
    41: "Necrotic Plague (Black Code)", 42: "Total Brain Death", 43: "Z-Class Pathogen",
    44: "Systemic Shutdown", 45: "Rigor Mortis Stage 1", 46: "Decapitation",
    47: "Incineration", 48: "Genetic Unraveling", 49: "Soul Fragmentation", 50: "Void Exposure"
}

def get_db_connection():
    try:
        conn = pyodbc.connect(CONN_STR, timeout=5)
        return conn
    except Exception as e:
        print(f"[SQL ERROR] Connection failed: {e}")
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page')) # Перенаправляем на страницу входа
        return f(*args, **kwargs)
    return decorated_function

# --- CHAOS ENGINE ---
all_doctor_ids = []
all_room_ids = []

def chaos_engine():
    global SIMULATION_ACTIVE, all_doctor_ids, all_room_ids
    print(">>> CHAOS ENGINE: ONLINE & RUNNING <<<")
    
    # Fetch all doctor and room IDs once at startup
    initial_conn = get_db_connection()
    if initial_conn:
        try:
            initial_cursor = initial_conn.cursor()
            initial_cursor.execute("SELECT DoctorID FROM Doctors")
            all_doctor_ids = [row.DoctorID for row in initial_cursor.fetchall()]
            initial_cursor.execute("SELECT RoomID FROM Rooms")
            all_room_ids = [row.RoomID for row in initial_cursor.fetchall()]
            print(f">>> CHAOS ENGINE: Loaded {len(all_doctor_ids)} Doctors and {len(all_room_ids)} Rooms <<<")
        except Exception as e:
            print(f"[CHAOS ERROR] Failed to load initial Doctors/Rooms: {e}")
        finally:
            initial_conn.close()

    while True:
        if SIMULATION_ACTIVE:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    roll = random.random()
                    
                    threat_id = 1
                    heart_rate = 80
                    spo2 = 98
                    
                    if roll < 0.35: 
                        threat_id = 1
                        heart_rate = random.randint(60, 90)
                        spo2 = random.randint(95, 100)
                    elif roll < 0.65:
                        threat_id = random.randint(2, 20)
                        heart_rate = random.randint(90, 130)
                        spo2 = random.randint(88, 95)
                    elif roll < 0.90:
                        threat_id = random.randint(21, 40)
                        heart_rate = random.randint(135, 170)
                        spo2 = random.randint(70, 85)
                    else:
                        threat_id = random.randint(41, 50)
                        if random.random() > 0.5:
                            heart_rate = 0 
                            spo2 = 0
                        else:
                            heart_rate = random.randint(180, 220)
                            spo2 = random.randint(40, 60)

                    fname = random.choice(FIRST_NAMES)
                    lname = random.choice(LAST_NAMES)
                    full_name = f"{fname} {lname}"
                    encrypted_name = encrypt_data(full_name) # Шифруем имя перед вставкой
                    
                    threat_name = FULL_THREAT_DICT.get(threat_id, "Unknown Threat")
                    print(f"[CHAOS] Spawning: {full_name} | ID: {threat_id} ({threat_name}) | Roll: {roll:.2f}")

                    # Randomly assign a doctor and room
                    assigned_doctor_id = random.choice(all_doctor_ids) if all_doctor_ids else None
                    assigned_room_id = random.choice(all_room_ids) if all_room_ids else None

                    cursor.execute("""
                        INSERT INTO Subjects (CodeName, AssignedThreatID, HeartRate, SPO2, AssignedDoctorID, AssignedRoomID, ArrivalTimestamp)
                        VALUES (?, ?, ?, ?, ?, ?, GETDATE())
                    """, (encrypted_name, threat_id, heart_rate, spo2, assigned_doctor_id, assigned_room_id))
                    conn.commit()
                except Exception as e:
                    print(f"[CHAOS ERROR] {e}")
                finally:
                    conn.close()
            time.sleep(random.uniform(2, 6))
        else:
            time.sleep(2)

threading.Thread(target=chaos_engine, daemon=True).start()

# --- МАРШРУТЫ (ИСПРАВЛЕНЫ) ---

@app.route('/', methods=['GET'])
def login_page():
    # Главная страница теперь рендерит LOGIN.HTML, а не терминал
    return render_template('login.html')

@app.route('/login_action', methods=['POST'])
def login_action():
    # Получаем данные из формы
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = get_db_connection()
    if not conn:
        return render_template('login.html', error="DATABASE OFFLINE")
    
    try:
        cursor = conn.cursor()
        # Шаг 1: Найти пользователя по логину
        cursor.execute("SELECT UserID, Role, DisplayName, PasswordHash FROM Users WHERE Username=?", (username,))
        user_record = cursor.fetchone()
        
        # Шаг 2: Проверить хеш пароля, если пользователь найден
        if user_record and verify_password(user_record.PasswordHash, password):
            session['user_id'] = user_record.UserID
            session['role'] = user_record.Role
            session['name'] = user_record.DisplayName
            # При успехе перенаправляем на монитор
            return redirect(url_for('monitor'))
        else:
            # Пользователь не найден или пароль неверный
            return render_template('login.html', error="INVALID CREDENTIALS")
    finally:
        conn.close()

@app.route('/monitor')
@login_required
def monitor():
    # Терминал доступен только после входа
    return render_template('terminal.html', user_name=session.get('name'), user_role=session.get('role'))

@app.route('/logout', methods=['GET'])
def logout():
    # Очищаем сессию и перенаправляем на страницу входа
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/api/subjects')
@login_required
def get_subjects():
    """
    Возвращает JSON со списком пациентов.
    Берет данные из VIEW или JOIN таблиц.
    """
    conn = get_db_connection()
    if not conn: return jsonify([])
    
    try:
        cursor = conn.cursor()
        # Выбираем последние 20 пациентов
        query = """
            SELECT TOP 20 
                S.SubjectID, 
                S.CodeName, 
                T.ThreatName, 
                S.StatusColor, 
                S.HeartRate, 
                S.SPO2, 
                S.ArrivalTimestamp
            FROM Subjects S
            JOIN BioThreats T ON S.AssignedThreatID = T.ThreatID
            ORDER BY S.ArrivalTimestamp DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        subjects = []
        for row in rows:
            subjects.append({
                'id': row.SubjectID,
                'name': decrypt_data(row.CodeName), # Расшифровываем имя для отображения
                'diagnosis': row.ThreatName,
                'status_color': row.StatusColor, # Вычисляется в SQL
                'hr': row.HeartRate,
                'spo2': row.SPO2,
                'arrival': row.ArrivalTimestamp.strftime('%H:%M:%S')
            })
        return jsonify(subjects)
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify([])
    finally:
        conn.close()

@app.route('/api/data')
@login_required
def get_all_data():
    conn = get_db_connection()
    if not conn:
        return jsonify({
            'patients': [],
            'doctors': [],
            'rooms': [],
            'threats': [],
            'total_patients': 0
        })

    try:
        cursor = conn.cursor()
        
        # Get pagination parameters
        offset = request.args.get('offset', 0, type=int)
        limit = request.args.get('limit', 100, type=int)  # 100 records per page

        # Fetch total count of all patients
        cursor.execute("SELECT COUNT(*) FROM Subjects")
        total_count = cursor.fetchone()[0]

        # Fetch paginated Subjects
        query_subjects = """
            SELECT 
                S.SubjectID,
                S.CodeName,
                T.ThreatName,
                S.StatusColor,
                S.HeartRate,
                S.SPO2,
                D.DocName,
                R.RoomName,
                S.ArrivalTimestamp,
                T.ThreatID,
                D.DoctorID,
                R.RoomID
            FROM Subjects S
            JOIN BioThreats T ON S.AssignedThreatID = T.ThreatID
            LEFT JOIN Doctors D ON S.AssignedDoctorID = D.DoctorID
            LEFT JOIN Rooms R ON S.AssignedRoomID = R.RoomID
            ORDER BY S.SubjectID DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """
        cursor.execute(query_subjects, (offset, limit))
        rows_subjects = cursor.fetchall()

        patients = []
        for row in rows_subjects:
            patients.append([
                row.SubjectID,
                decrypt_data(row.CodeName),
                row.ThreatName,
                row.StatusColor,
                row.HeartRate,
                row.SPO2,
                row.DocName,
                row.RoomName,
                row.ArrivalTimestamp.isoformat(),
                row.ThreatID,
                row.DoctorID,
                row.RoomID
            ])

        # Fetch Doctors
        query_doctors = "SELECT DoctorID, DocName FROM Doctors ORDER BY DocName"
        cursor.execute(query_doctors)
        rows_doctors = cursor.fetchall()
        doctors = [{'id': row.DoctorID, 'name': row.DocName} for row in rows_doctors]

        # Fetch Rooms
        query_rooms = "SELECT RoomID, RoomName FROM Rooms ORDER BY RoomName"
        cursor.execute(query_rooms)
        rows_rooms = cursor.fetchall()
        rooms = [{'id': row.RoomID, 'name': row.RoomName} for row in rows_rooms]

        # Fetch Threats
        query_threats = "SELECT ThreatID, ThreatName FROM BioThreats ORDER BY ThreatID"
        cursor.execute(query_threats)
        rows_threats = cursor.fetchall()
        threats = [{'id': row.ThreatID, 'name': row.ThreatName} for row in rows_threats]

        return jsonify({
            'patients': patients,
            'doctors': doctors,
            'rooms': rooms,
            'threats': threats,
            'total_patients': total_count,
            'offset': offset,
            'limit': limit
        })

    finally:
        conn.close()

@app.route('/api/add_patient', methods=['POST'])
@login_required
def add_patient():
    data = request.json
    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': 'Database Offline'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Subjects (CodeName, AssignedThreatID, HeartRate, SPO2, AssignedDoctorID, AssignedRoomID, ArrivalTimestamp)
            VALUES (?, ?, ?, ?, ?, ?, GETDATE())
        """, (
            encrypt_data(data['name']), # Шифруем имя
            data['threat_id'],
            data['hr'],
            data['spo2'],
            data['doctor_id'] if data['doctor_id'] else None, # Allow NULL if not selected
            data['room_id'] if data['room_id'] else None      # Allow NULL if not selected
        ))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error adding patient: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/update_patient', methods=['POST'])
@login_required
def update_patient():
    data = request.json
    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': 'Database Offline'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Subjects
            SET CodeName = ?, AssignedThreatID = ?, HeartRate = ?, SPO2 = ?, AssignedDoctorID = ?, AssignedRoomID = ?
            WHERE SubjectID = ?
        """, (
            encrypt_data(data['name']), # Шифруем имя
            data['threat_id'],
            data['hr'],
            data['spo2'],
            data['doctor_id'] if data['doctor_id'] else None,
            data['room_id'] if data['room_id'] else None,
            data['subject_id']
        ))
        conn.commit()
        return jsonify({'success': True})
    finally:
        conn.close()

@app.route('/api/delete_patient', methods=['POST'])
@login_required
def delete_patient():
    data = request.json
    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': 'Database Offline'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Subjects WHERE SubjectID = ?", (data['subject_id'],))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error deleting patient: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/toggle_sim', methods=['POST'])
@login_required
def toggle_sim():
    global SIMULATION_ACTIVE
    SIMULATION_ACTIVE = not SIMULATION_ACTIVE
    return jsonify({'status': SIMULATION_ACTIVE})

@app.route('/api/resolve_subject', methods=['POST'])
@login_required
def resolve_subject():
    data = request.json
    conn = get_db_connection()
    if not conn: return jsonify({'success': False}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Subjects WHERE SubjectID = ?", (data['subject_id'],))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception:
        return jsonify({'success': False}), 500

@app.route('/api/search', methods=['POST'])
@login_required
def search_patients():
    """
    Search for patients by name or code.
    Request JSON:
    {
        "query": "search_string",
        "search_type": "name" or "code"
    }
    """
    data = request.get_json()
    query = data.get('query', '').strip()
    search_type = data.get('search_type', 'name')  # 'name' or 'code'
    
    if not query or len(query) < 1:
        return jsonify([])
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database Error"}), 500
    
    try:
        cursor = conn.cursor()
        
        if search_type == 'code':
            # Search by code (SubjectID) - partial match
            # Get all patients and filter by code
            cursor.execute("""
                SELECT SubjectID, CodeName, AssignedDoctorID, AssignedRoomID
                FROM Subjects
                ORDER BY ArrivalTimestamp DESC
            """)
            rows = cursor.fetchall()
            results = []
            
            query_lower = query.lower()
            for row in rows:
                subject_id = row.SubjectID
                # Match code as string
                if query_lower in str(subject_id).lower():
                    encrypted_name = row.CodeName
                    try:
                        decrypted_name = decrypt_data(encrypted_name)
                    except:
                        decrypted_name = "[ERROR_DECRYPT]"
                    
                    results.append({
                        'id': subject_id,
                        'name': decrypted_name,
                        'doctor_id': row.AssignedDoctorID,
                        'room_id': row.AssignedRoomID,
                        'search_type': 'code'
                    })
            
            return jsonify(results)
        
        else:  # search_type == 'name'
            # Search by name (CodeName) - fuzzy matching
            cursor.execute("""
                SELECT SubjectID, CodeName, AssignedDoctorID, AssignedRoomID
                FROM Subjects
                ORDER BY ArrivalTimestamp DESC
            """)
            rows = cursor.fetchall()
            results = []
            
            for row in rows:
                subject_id = row.SubjectID
                encrypted_name = row.CodeName
                try:
                    decrypted_name = decrypt_data(encrypted_name)
                    # Fuzzy matching on name/surname
                    if _fuzzy_match(query, decrypted_name.lower()):
                        results.append({
                            'id': subject_id,
                            'name': decrypted_name,
                            'doctor_id': row.AssignedDoctorID,
                            'room_id': row.AssignedRoomID,
                            'search_type': 'name'
                        })
                except:
                    continue
            
            return jsonify(results)  # Return all matches, not limited
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

def _fuzzy_match(query, target):
    """Simple fuzzy matching algorithm."""
    # Direct substring match
    if query in target:
        return True
    
    # Check if query matches start of name
    if target.startswith(query):
        return True
    
    # Check if query matches after space (surname matching)
    parts = target.split()
    for part in parts:
        if part.lower().startswith(query):
            return True
    
    # Levenshtein-like distance (simplified)
    if len(query) >= 2:
        for i in range(len(target) - len(query) + 1):
            substring = target[i:i+len(query)]
            if _similarity(query, substring) >= 0.75:
                return True
    
    return False

def _similarity(s1, s2):
    """Calculate simple similarity score (0-1)."""
    if len(s1) != len(s2):
        return 0
    
    matches = sum(c1 == c2 for c1, c2 in zip(s1, s2))
    return matches / len(s1)

@app.route('/api/export')
@login_required
def export_data():
    conn = get_db_connection()
    if not conn: return "Database Error", 500
    try:
        cursor = conn.cursor()
        query = """
            SELECT S.SubjectID, S.CodeName, T.ThreatName, S.StatusColor, S.HeartRate, S.SPO2, D.DocName, R.RoomName, S.ArrivalTimestamp
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
        for row in rows:
            row_list = list(row)
            row_list[1] = decrypt_data(row_list[1])  # Decrypt CodeName
            cw.writerow(row_list)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=export_logs.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    except Exception as e:
        return f"Export failed: {e}", 500
    finally:
        conn.close()

if __name__ == '__main__':
    print(">>> SYSTEM STARTUP INITIATED <<<")
    # Исправлено: host удален, чтобы запускалось только на localhost (127.0.0.1)
    app.run(debug=True, use_reloader=False, port=5000)