DROP TABLE Caregivers;
--DROP TABLE Patient;
DROP TABLE Availabilities;
DROP TABLE Vaccines;



CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Administrator varchar(255) REFERENCES Caregivers(Username) NOT NULL,
    PRIMARY KEY (Time, Administrator)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Appointments (
    Time date,
    uid varchar(255),
    Patient varchar(255) REFERENCES Patients(Username) NOT NULL,
    Administrator varchar(255) REFERENCES Caregivers(Username) NOT NULL,
    Vaccine varchar(255) REFERENCES
    Vaccines(Name) NOT NULL,
    PRIMARY KEY (uid)
)
