USE master;
GO

-- 1. СБРОС БАЗЫ ДАННЫХ (Если существует - удаляем и создаем заново)
IF EXISTS (SELECT * FROM sys.databases WHERE name = 'AESCULAPIUS')
BEGIN
    ALTER DATABASE AESCULAPIUS SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE AESCULAPIUS;
END
GO

CREATE DATABASE AESCULAPIUS;
GO

USE AESCULAPIUS;
GO

-- 2. ТАБЛИЦА ПОЛЬЗОВАТЕЛЕЙ (ПЕРСОНАЛ)
-- ПРИМЕЧАНИЕ: Структура обновлена -  (PasswordHash NVARCHAR(500)).
-- теперь у нас хеши вместо паролей, которые прсото так лежат. теперь же особоой ценности у хешей - случайных солей для злоумышленика нет.
CREATE TABLE Users (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    Username NVARCHAR(50) UNIQUE NOT NULL,
    PasswordHash NVARCHAR(500) NOT NULL, -- Увеличено для хранения длинных PBKDF2 хешей
    Role NVARCHAR(20) NOT NULL CHECK (Role IN ('Registrar', 'Admin', 'Manager')),
    DisplayName NVARCHAR(100)
);

-- ПЕРСОНАЛ - (ХЕШИ)
INSERT INTO Users (Username, PasswordHash, Role, DisplayName) VALUES 
-- Обновленный хеш для ChiefArchi
('ChiefArchi', 'pbkdf2:sha256:1000000$rV7LEC2c$78befa1fe17c7568bd93780a25684f7932478a8364c32e6b1fb234b3a132795c', 'Manager', 'The Architect'),
-- Обновленный хеш для admin_wolf
('admin_wolf', 'pbkdf2:sha256:1000000$OAJWZ1Ec$7340df782c4f7059d06ae1f84b72d6b9ed52475a8a38716577920addc821280c', 'Admin', 'Dr. Wolf'),
-- Обновленный хеш для admin_house
('admin_house', 'pbkdf2:sha256:1000000$pGEDDK0l$4096ace494fe003e157f9f40a4b29f26c6aeb14c108fcd33ec2ec3c7f7d7ef9c', 'Admin', 'Dr. House'),
-- Обновленный хеш для admin_strange
('admin_strange', 'pbkdf2:sha256:1000000$SrioZDEQ$b60d18103a26d52319da9db508a63840caa392cdd2ea907096b41ef33d7d214c', 'Admin', 'Dr. Strange'),
-- Обновленный хеш для nurse_joy
('nurse_joy', 'pbkdf2:sha256:1000000$KZA67Ok9$d4e0ec769d5fa23cb5a5ec1f691e17083d14e9475264b01d8856dd59b79a2419', 'Registrar', 'Nurse Joy'),
-- Для следующих пользователей хешей нет.Оставлены старые значения.
('nurse_ratched', 'cuckoo', 'Registrar', 'Nurse Ratched'),
('clerk_kent', 'superman', 'Registrar', 'Clark Kent');

-- 3. ТАБЛИЦА КОМНАТ (ЛОКАЦИИ)
CREATE TABLE Rooms (
    RoomID INT PRIMARY KEY IDENTITY(1,1),
    RoomName NVARCHAR(100),
    SecurityLevel INT 
);

INSERT INTO Rooms (RoomName, SecurityLevel) VALUES 
('General Ward A-01', 1), ('General Ward A-02', 1), ('General Ward A-03', 1), ('General Ward A-04', 1), ('General Ward A-05', 1),
('General Ward B-01', 1), ('General Ward B-02', 1), ('General Ward B-03', 1), ('General Ward B-04', 1), ('General Ward B-05', 1),
('Emergency Unit E-1', 2), ('Emergency Unit E-2', 2), ('Emergency Unit E-3', 2), ('Trauma Center Alpha', 2), ('Trauma Center Beta', 2),
('ICU Pod 01', 3), ('ICU Pod 02', 3), ('ICU Pod 03', 3), ('Resuscitation Bay 1', 3), ('Resuscitation Bay 2', 3),
('Surgery Unit 01', 3), ('Surgery Unit 02', 3), ('Surgery Unit 03', 3), ('Surgery Unit 04', 3), ('Surgery Unit 05', 3),
('Neuro-Surgery Lab', 4), ('Cyber-Implant Lab', 4), ('Organ Transplant Unit', 4), ('Robotic Surgery A', 3), ('Robotic Surgery B', 3),
('Bio-Isolation Chamber 1', 5), ('Bio-Isolation Chamber 2', 5), ('Viral Containment Unit', 5), ('Hazardous Waste Storage', 5), ('Decontamination Zone', 4),
('Quarantine Sector Q1', 4), ('Quarantine Sector Q2', 4), ('Radiation Shielded Room', 5), ('Cryo-Stasis Storage A', 4), ('Cryo-Stasis Storage B', 4),
('Psychiatric Ward P-1', 2), ('Psychiatric Ward P-2', 2), ('Behavioral Control Unit', 3), ('Sleep Disorder Lab', 1), ('Neural Mapping Room', 2),
('Morgue Sector Z-1', 0), ('Morgue Sector Z-2', 0), ('Autopsy Room A', 0), ('Autopsy Room B', 0), ('Mass Casualty Storage', 0);

-- 4. ТАБЛИЦА ВРАЧЕЙ
CREATE TABLE Doctors (
    DoctorID INT PRIMARY KEY IDENTITY(1,1),
    DocName NVARCHAR(100),
    Specialization NVARCHAR(100),
    IsAvailable BIT DEFAULT 1
);

INSERT INTO Doctors (DocName, Specialization) VALUES 
('Dr. Dayo Igwe', 'Neurology / Prosthetics'),
('Dr. Annalise Gallegos', 'Psychiatry'),
('Dr. Bernard Rieux', 'Epidemiology'),
('Dr. Hannibal', 'Forensic Psychiatry'),
('Dr. Frankenstein', 'Resuscitation'),
('Dr. Strange', 'Surgery'),
('AI Unit 734', 'Diagnostics'),
('Dr. Plague', 'Virology'),
('Dr. Otto Octavius', 'Cybernetics'),
('Dr. Leonard McCoy', 'General Medicine'),
('Dr. Mordin Solus', 'Genetics'),
('Dr. Beverly Crusher', 'Space Medicine');


-- 5. ТАБЛИЦА БИО-УГРОЗ (СЛОВАРЬ БОЛЕЗНЕЙ)
CREATE TABLE BioThreats (
    ThreatID INT PRIMARY KEY, -- ID задаем вручную, без IDENTITY
    ThreatName NVARCHAR(100),
    ThreatLevel INT, -- 1=Green, 2=Yellow, 3=Red, 4=Black
    LethalityRate FLOAT
);

-- ВАЖНО: Мы заполняем все 50 уровней угроз
-- Диапазоны для справки:
-- 1: Green
-- 2-20: Yellow
-- 21-40: Red
-- 41-50: Black

INSERT INTO BioThreats (ThreatID, ThreatName, ThreatLevel, LethalityRate) VALUES 
-- GREEN (1)
(1, 'Mild Influenza', 1, 0.0),

-- YELLOW (2-20)
(2, 'Chronic Bronchitis', 2, 0.05),
(3, 'Fractured Rib', 2, 0.02),
(4, 'Concussion (Grade 1)', 2, 0.01),
(5, 'Severe Dehydration', 2, 0.1),
(6, 'Heat Exhaustion', 2, 0.05),
(7, 'Hypothermia (Stage 1)', 2, 0.15),
(8, 'Food Poisoning', 2, 0.02),
(9, 'Allergic Reaction', 2, 0.05),
(10, 'Sleep Deprivation Psychosis', 2, 0.0),
(11, 'Panic Attack', 2, 0.0),
(12, 'Laceration (Non-Arterial)', 2, 0.1),
(13, 'Sprained Ankle', 2, 0.0),
(14, 'Migraine (Cluster)', 2, 0.0),
(15, 'Vertigo', 2, 0.0),
(16, 'Hyperventilation', 2, 0.0),
(17, 'Low Blood Sugar', 2, 0.05),
(18, 'High Blood Pressure', 2, 0.1),
(19, 'Vitamin Deficiency', 2, 0.02),
(20, 'Exhaustion', 2, 0.0),

-- RED (21-40)
(21, 'Arterial Bleeding', 3, 0.6),
(22, 'Punctured Lung', 3, 0.5),
(23, 'Neural Rot', 3, 0.7),
(24, 'Cyber-Psychosis', 3, 0.4),
(25, 'Radiation Sickness (Acute)', 3, 0.8),
(26, 'Bio-Plague (Early Stage)', 3, 0.65),
(27, 'Internal Hemorrhage', 3, 0.7),
(28, 'Compound Fracture', 3, 0.3),
(29, 'Kidney Failure', 3, 0.55),
(30, 'Cardiac Arrest Risk', 3, 0.6),
(31, 'Severe Burns (3rd Degree)', 3, 0.4),
(32, 'Toxic Chemical Exposure', 3, 0.5),
(33, 'Blood Toxicity', 3, 0.55),
(34, 'Cerebral Edema', 3, 0.7),
(35, 'Lung Collapse', 3, 0.4),
(36, 'Spinal Severance', 3, 0.3),
(37, 'Brain Aneurysm', 3, 0.8),
(38, 'Flesh-Eating Bacteria', 3, 0.6),
(39, 'Parasitic Host', 3, 0.7),
(40, 'Cryo-Burn', 3, 0.3),

-- BLACK (41-50) - ИНТЕГРИРОВАННЫЕ ДАННЫЕ
(41, 'Necrotic Plague (Black Code)', 4, 0.99),
(42, 'Total Brain Death', 4, 1.0),
(43, 'Z-Class Pathogen', 4, 0.95),
(44, 'Systemic Shutdown', 4, 0.9),
(45, 'Rigor Mortis Stage 1', 4, 1.0),
(46, 'Decapitation', 4, 1.0),
(47, 'Incineration', 4, 1.0),
(48, 'Genetic Unraveling', 4, 0.9),
(49, 'Soul Fragmentation', 4, 1.0),
(50, 'Void Exposure', 4, 1.0);

-- 6. ТАБЛИЦА ПАЦИЕНТОВ (СУБЪЕКТОВ)
-- ПРИМЕЧАНИЕ: CodeName NVARCHAR(1000) согласно требованиям.
CREATE TABLE Subjects (
    SubjectID INT PRIMARY KEY IDENTITY(1,1),
    CodeName NVARCHAR(1000), -- Увеличено до 1000
    
    -- Связь с таблицей угроз
    AssignedThreatID INT FOREIGN KEY REFERENCES BioThreats(ThreatID),
    
    HeartRate INT,
    SPO2 INT,
    
    AssignedDoctorID INT FOREIGN KEY REFERENCES Doctors(DoctorID),
    AssignedRoomID INT FOREIGN KEY REFERENCES Rooms(RoomID),
    
    ArrivalTimestamp DATETIME DEFAULT GETDATE(),
    
    -- АВТОМАТИЧЕСКОЕ ОПРЕДЕЛЕНИЕ ЦВЕТА
    StatusColor AS (
        CASE 
            WHEN AssignedThreatID = 1 THEN 'Green'
            WHEN AssignedThreatID BETWEEN 2 AND 20 THEN 'Yellow'
            WHEN AssignedThreatID BETWEEN 21 AND 40 THEN 'Red'
            WHEN AssignedThreatID > 40 THEN 'Black'
            ELSE 'Yellow'
        END
    )
);

-- Тестовая вставка одного пациента для проверки
INSERT INTO Subjects (CodeName, AssignedThreatID, HeartRate, SPO2) 
VALUES ('TEST-SUBJECT-ZERO', 41, 0, 0);

GO

-- ФИНАЛЬНАЯ ПРОВЕРКА: Вывод количества загруженных угроз
SELECT 'Database Created Successfully' as Status, COUNT(*) as Total_Threats_Loaded FROM BioThreats;