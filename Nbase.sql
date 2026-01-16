USE master;
GO

IF EXISTS (SELECT * FROM sys.databases WHERE name = 'AESCULAPIUS')
    ALTER DATABASE AESCULAPIUS SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE AESCULAPIUS;
GO

CREATE DATABASE AESCULAPIUS;
GO

USE AESCULAPIUS;
GO

CREATE TABLE Users (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    Username NVARCHAR(50) UNIQUE NOT NULL,
    PasswordHash NVARCHAR(255) NOT NULL,
    Role NVARCHAR(20) NOT NULL CHECK (Role IN ('Registrar', 'Admin', 'Manager')),
    DisplayName NVARCHAR(100)
);

INSERT INTO Users (Username, PasswordHash, Role, DisplayName) VALUES 
('architect', 'matrix_master', 'Manager', 'The Architect'),
('admin_wolf', 'alpha1', 'Admin', 'Dr. Wolf'),
('admin_house', 'vicodin', 'Admin', 'Dr. House'),
('admin_strange', 'dormammu', 'Admin', 'Dr. Strange'),
('nurse_joy', 'pokemon', 'Registrar', 'Nurse Joy'),
('nurse_ratched', 'cuckoo', 'Registrar', 'Nurse Ratched'),
('clerk_kent', 'superman', 'Registrar', 'Clark Kent');

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

CREATE TABLE Doctors (
    DoctorID INT PRIMARY KEY IDENTITY(1,1),
    DocName NVARCHAR(100),
    Specialty NVARCHAR(100)
);

INSERT INTO Doctors (DocName, Specialty) VALUES 
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

CREATE TABLE BioThreats (
    ThreatID INT PRIMARY KEY,
    ThreatName NVARCHAR(100),
    LethalityLevel INT,
    MortalityRate FLOAT
);

INSERT INTO BioThreats (ThreatID, ThreatName, LethalityLevel, MortalityRate) VALUES 
(1, 'Stable / Healthy', 0, 0.0),
(2, 'Common Influenza 2099', 1, 0.01),
(3, 'Viral Fatigue Syndrome', 1, 0.0),
(4, 'Synthetic Allergies', 1, 0.05),
(5, 'Neural Static', 1, 0.1),
(6, 'Mild Radiation Exposure', 2, 0.15),
(7, 'Unknown Viral Strain A', 2, 0.2),
(8, 'Unknown Viral Strain B', 2, 0.2),
(9, 'Bacterial Pneumonia', 2, 0.1),
(10, 'Sleep Deprivation Psychosis', 1, 0.0),
(11, 'Optical Nerve Degeneration', 1, 0.0),
(12, 'Cyber-Sickness', 1, 0.01),
(13, 'Muscle Atrophy', 1, 0.05),
(14, 'Respiratory Infection', 2, 0.1),
(15, 'Food Poisoning (Synthetic)', 1, 0.0),
(16, 'Dehydration', 1, 0.05),
(17, 'Minor Lacerations', 1, 0.0),
(18, 'Broken Bone', 1, 0.0),
(19, 'Concussion', 2, 0.05),
(20, 'Post-Traumatic Stress', 1, 0.0),
(21, 'Radiation Sickness (Acute)', 3, 0.4),
(22, 'Bio-Hemolytic Virus', 3, 0.5),
(23, 'Neural Rot', 3, 0.6),
(24, 'Cyber-Sepsis', 3, 0.45),
(25, 'Internal Hemorrhage', 3, 0.5),
(26, 'Organ Failure (Multiple)', 3, 0.7),
(27, 'T-Virus Strain Alpha', 3, 0.8),
(28, 'Void Sickness', 3, 0.6),
(29, 'Nanobot Rejection', 3, 0.55),
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
(41, 'Necrotic Plague (Black Code)', 4, 0.99),
(42, 'Total Brain Death', 4, 1.0),
(43, 'Z-Class Pathogen', 4, 0.95),
(44, 'Systemic Shutdown', 4, 0.9),
(45, 'Rigor Mortis Stage 1', 4, 1.0),
(46, 'Decapitation', 4, 1.0),
(47, 'Incineration', 4, 1.0),
(48, 'Genetic Disintegration', 4, 0.98),
(49, 'Hollow Shell Syndrome', 4, 1.0),
(50, 'Clinical Death', 4, 1.0);

CREATE TABLE Subjects (
    SubjectID INT PRIMARY KEY IDENTITY(1,1),
    CodeName NVARCHAR(100),
    ArrivalTimestamp DATETIME DEFAULT GETDATE(),
    AssignedThreatID INT FOREIGN KEY REFERENCES BioThreats(ThreatID),
    AssignedDoctorID INT FOREIGN KEY REFERENCES Doctors(DoctorID),
    AssignedRoomID INT FOREIGN KEY REFERENCES Rooms(RoomID),
    HeartRate INT,
    SPO2 INT,
    
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
GO