UUSE master;
GO

-- Удаляем старую версию, если есть
IF EXISTS (SELECT * FROM sys.databases WHERE name = 'AESCULAPIUS')
    ALTER DATABASE AESCULAPIUS SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE AESCULAPIUS;
GO

CREATE DATABASE AESCULAPIUS;
GO

USE AESCULAPIUS;
GO

-- 1. Таблица Палат (Отделения)
CREATE TABLE Rooms (
    RoomID INT PRIMARY KEY IDENTITY(1,1),
    RoomName NVARCHAR(100), -- Изолятор, Хирургия, Морг
    SecurityLevel INT -- Уровень доступа
);

INSERT INTO Rooms (RoomName, SecurityLevel) VALUES 
('General Ward A', 1),
('Surgery Unit 04', 3),
('Bio-Isolation Chamber', 5), -- Для чумы и вирусов
('Cryo-Stasis Storage', 4),
('Morgue Sector Z', 0),       -- Для черного кода
('Psychiatric Ward', 2);

-- 2. Таблица Врачей
CREATE TABLE Doctors (
    DoctorID INT PRIMARY KEY IDENTITY(1,1),
    DocName NVARCHAR(100),
    Specialty NVARCHAR(100)
);

INSERT INTO Doctors (DocName, Specialty) VALUES 
('Dr. Hannibal', 'Psychiatry'),
('Dr. Frankenstein', 'Resuscitation'),
('Dr. Strange', 'Surgery'),
('AI Unit 734', 'Diagnostics'),
('Dr. House', 'Infectious Diseases');

-- 3. Справочник Угроз (Болезни)
CREATE TABLE BioThreats (
    ThreatID INT PRIMARY KEY IDENTITY(1,1),
    ThreatName NVARCHAR(100),
    LethalityScore INT, -- 0-30: Green, 31-70: Yellow, 71-99: Red, 100: Black
    TargetRoomID INT FOREIGN KEY REFERENCES Rooms(RoomID)
);

INSERT INTO BioThreats (ThreatName, LethalityScore, TargetRoomID) VALUES
('Mild Influenza', 10, 1),           -- General Ward
('Panic Attack', 5, 6),              -- Psych Ward
('Fracture (Open)', 40, 2),          -- Surgery
('Chemical Burn', 60, 2),            -- Surgery
('Radiation Sickness', 85, 3),       -- Isolation
('Unknown Viral Strain', 90, 3),     -- Isolation
('Bubonic Plague', 95, 3),           -- Isolation
('Cardiac Arrest', 99, 2),           -- Surgery
('Biological Decomposition', 100, 5),-- Morgue (BLACK)
('Neural Collapse', 100, 5);         -- Morgue (BLACK)

-- 4. Таблица Пациентов
CREATE TABLE Subjects (
    SubjectID INT PRIMARY KEY IDENTITY(1,1),
    CodeName NVARCHAR(100),
    Age INT,
    HeartRate INT,
    SPO2 INT,
    
    -- Связи
    AssignedThreatID INT FOREIGN KEY REFERENCES BioThreats(ThreatID),
    AssignedDoctorID INT FOREIGN KEY REFERENCES Doctors(DoctorID) NULL,
    AssignedRoomID INT FOREIGN KEY REFERENCES Rooms(RoomID) NULL,
    
    ArrivalTimestamp DATETIME DEFAULT GETDATE(),
    
    -- Вычисляемые поля
    StatusColor NVARCHAR(20), -- RED, YELLOW, GREEN, BLACK
    IsManualEntry BIT DEFAULT 0 -- Флаг ручного ввода
);
GO

-- 5. Триггер "СУДЬЯ v2.0"
CREATE TRIGGER trg_AdvancedBioScan
ON Subjects
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- Обновляем статус и комнату
    UPDATE S
    SET 
        -- Логика Цветов
        StatusColor = CASE 
            -- Если это ручной ввод и цвет уже задан (через спец. болезнь), оставляем как есть.
            -- Но для автоматики:
            WHEN T.LethalityScore >= 100 OR S.HeartRate = 0 THEN 'BLACK'
            WHEN T.LethalityScore > 75 OR S.HeartRate > 150 OR S.SPO2 < 70 THEN 'RED'
            WHEN T.LethalityScore > 35 OR S.HeartRate > 110 OR S.SPO2 < 90 THEN 'YELLOW'
            ELSE 'GREEN'
        END,

        -- Логика Комнат (Если комната не задана вручную, берем из болезни)
        AssignedRoomID = ISNULL(S.AssignedRoomID, 
            CASE 
                WHEN T.LethalityScore >= 100 OR S.HeartRate = 0 THEN (SELECT RoomID FROM Rooms WHERE RoomName = 'Morgue Sector Z')
                ELSE T.TargetRoomID 
            END
        ),

        -- Назначаем случайного доктора, если не назначен
        AssignedDoctorID = ISNULL(S.AssignedDoctorID, (SELECT TOP 1 DoctorID FROM Doctors ORDER BY NEWID()))

    FROM Subjects S
    JOIN BioThreats T ON S.AssignedThreatID = T.ThreatID
    WHERE S.SubjectID IN (SELECT SubjectID FROM Inserted);
END;
GO










// wiew ////////////////////////

USE AESCULAPIUS;
GO

-- Если представление уже есть, удаляем его
IF OBJECT_ID('v_LiveMonitor', 'V') IS NOT NULL
    DROP VIEW v_LiveMonitor;
GO

-- Создаем "Виртуальную Таблицу" для красивого просмотра
CREATE VIEW v_LiveMonitor AS
SELECT TOP 100
    S.SubjectID,
    FORMAT(S.ArrivalTimestamp, 'HH:mm:ss') AS [Arrival Time], -- Время
    S.CodeName AS [Patient Name],      -- Имя
    T.ThreatName AS [Diagnosis],       -- Диагноз
    S.StatusColor AS [Priority],       -- Цвет
    S.HeartRate AS [HR],               -- Пульс
    S.SPO2,                            -- Кислород
    D.DocName AS [Doctor],             -- Врач
    R.RoomName AS [Location]           -- Палата
FROM Subjects S
JOIN BioThreats T ON S.AssignedThreatID = T.ThreatID
LEFT JOIN Doctors D ON S.AssignedDoctorID = D.DoctorID
LEFT JOIN Rooms R ON S.AssignedRoomID = R.RoomID
ORDER BY S.ArrivalTimestamp DESC; -- Самые новые сверху
GO









//////////////////////////Скрипт авто-обновления/////////////////////

USE AESCULAPIUS;
SET NOCOUNT ON; -- Отключаем технические сообщения, чтобы не засорять память

PRINT '>>> MONITORING SYSTEM STARTED <<<';
PRINT 'Press the red STOP button in the toolbar to exit.';

-- Бесконечный цикл
WHILE 1 = 1
BEGIN
    -- 1. Выбираем данные из нашего красивого вида
    SELECT TOP 20 * FROM v_LiveMonitor;

    -- 2. Ждем 2 секунды (формат чч:мм:сс)
    WAITFOR DELAY '00:00:02';
END




//////////Подготовка "Красивых данных" в SQL//////////

USE AESCULAPIUS;
GO

CREATE VIEW v_ExcelReport AS
SELECT TOP 1000
    S.SubjectID,
    S.CodeName AS [Patient Name],
    T.ThreatName AS [Diagnosis],
    S.StatusColor AS [Priority],
    S.HeartRate AS [BPM],
    S.SPO2,
    D.DocName AS [Doctor],
    R.RoomName AS [Room],
    S.ArrivalTimestamp
FROM Subjects S
JOIN BioThreats T ON S.AssignedThreatID = T.ThreatID
LEFT JOIN Doctors D ON S.AssignedDoctorID = D.DoctorID
LEFT JOIN Rooms R ON S.AssignedRoomID = R.RoomID;
GO



...------ \\\новый код, новые врачи, новая структура ... : //////

USE master;
GO

-- 1. СНЯТИЕ БЛОКИРОВОК И УДАЛЕНИЕ
-- Если база существует, мы переводим её в режим MULTI_USER (на случай если она зависла),
-- а затем резко удаляем, обрывая все соединения.
IF EXISTS (SELECT name FROM sys.databases WHERE name = 'AESCULAPIUS')
BEGIN
    PRINT '>>> Killing connections to AESCULAPIUS...';
    ALTER DATABASE AESCULAPIUS SET MULTI_USER WITH ROLLBACK IMMEDIATE;
    ALTER DATABASE AESCULAPIUS SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE AESCULAPIUS;
    PRINT '>>> Database Dropped.';
END
GO

-- 2. СОЗДАНИЕ НОВОЙ БАЗЫ
CREATE DATABASE AESCULAPIUS;
GO

USE AESCULAPIUS;
GO

-- 3. СОЗДАНИЕ ТАБЛИЦ

-- Палаты
CREATE TABLE Rooms (
    RoomID INT PRIMARY KEY IDENTITY(1,1),
    RoomName NVARCHAR(100), 
    SecurityLevel INT
);

INSERT INTO Rooms (RoomName, SecurityLevel) VALUES 
('General Ward A', 1),
('Surgery Unit 04', 3),
('Bio-Isolation Chamber', 5),
('Cryo-Stasis Storage', 4),
('Morgue Sector Z', 0),
('Psychiatric Ward', 2);

-- Врачи (20 легенд, как ты просил)
CREATE TABLE Doctors (
    DoctorID INT PRIMARY KEY IDENTITY(1,1),
    DocName NVARCHAR(100),
    Specialty NVARCHAR(100)
);

INSERT INTO Doctors (DocName, Specialty) VALUES 
('Dr. Hippocrates', 'General Medicine'),
('Dr. Avicenna', 'Virology'),
('Dr. Paracelsus', 'Toxicology'),
('Dr. Frankenstein', 'Reanimation'),
('Dr. Jekyll', 'Chemistry'),
('Dr. Hannibal Lecter', 'Psychiatry'),
('Dr. House G.', 'Diagnostics'),
('Dr. Watson J.', 'Surgery'),
('Dr. Strange S.', 'Neurosurgery'),
('Dr. Zhivago Y.', 'General Practice'),
('Dr. McCoy L.', 'Xenobiology'),
('Dr. Moreau', 'Genetics'),
('Dr. Caligari', 'Somnambulism'),
('Dr. Faust', 'Metaphysics'),
('Dr. Preobrazhensky', 'Endocrinology'),
('Dr. Aibolit', 'Veterinary'),
('Dr. Quinn', 'Traumatology'),
('Dr. Doom', 'Cybernetics'),
('Dr. Octopus', 'Prosthetics'),
('AI Unit "HAL-9000"', 'System Admin');

-- Угрозы (Важно: ThreatID задаем вручную, без IDENTITY, чтобы совпадать с Python кодом 1,2,3,4)
CREATE TABLE BioThreats (
    ThreatID INT PRIMARY KEY,
    ThreatName NVARCHAR(100),
    SeverityLevel INT, 
    InfectionRate FLOAT
);

INSERT INTO BioThreats (ThreatID, ThreatName, SeverityLevel, InfectionRate) VALUES 
(1, 'Stable / Healthy', 0, 0.0),
(2, 'Unknown Viral Strain', 2, 0.4),
(3, 'Radiation Sickness', 3, 0.0),
(4, 'Necrotic Plague (Black Code)', 4, 0.9);

-- Пациенты
-- Здесь мы используем ВЫЧИСЛЯЕМЫЙ СТОЛБЕЦ (Computed Column) для цвета.
-- Это лучше, чем Trigger, потому что работает мгновенно и не нагружает базу.
CREATE TABLE Subjects (
    SubjectID INT PRIMARY KEY IDENTITY(1,1),
    CodeName NVARCHAR(100),
    ArrivalTimestamp DATETIME DEFAULT GETDATE(),
    AssignedThreatID INT FOREIGN KEY REFERENCES BioThreats(ThreatID),
    AssignedDoctorID INT FOREIGN KEY REFERENCES Doctors(DoctorID),
    AssignedRoomID INT FOREIGN KEY REFERENCES Rooms(RoomID),
    HeartRate INT,
    SPO2 INT,
    
    -- АВТОМАТИЧЕСКАЯ ОПРЕДЕЛЕНИЕ ЦВЕТА
    StatusColor AS (
        CASE AssignedThreatID
            WHEN 1 THEN 'Green'
            WHEN 2 THEN 'Yellow'
            WHEN 3 THEN 'Red'
            WHEN 4 THEN 'Black'
            ELSE 'Green'
        END
    )
);
GO

-- 4. ПРЕДСТАВЛЕНИЕ (VIEW) ДЛЯ PYTHON
CREATE VIEW v_LiveMonitor AS
SELECT TOP 50
    S.CodeName,
    S.ArrivalTimestamp,
    S.StatusColor,
    T.ThreatName,
    S.HeartRate AS [HR],
    S.SPO2,
    D.DocName AS [Doctor],
    R.RoomName AS [Location]
FROM Subjects S
JOIN BioThreats T ON S.AssignedThreatID = T.ThreatID
LEFT JOIN Doctors D ON S.AssignedDoctorID = D.DoctorID
LEFT JOIN Rooms R ON S.AssignedRoomID = R.RoomID;
GO

PRINT '>>> SUCCESS! DATABASE REBUILT CORRECTLY.';