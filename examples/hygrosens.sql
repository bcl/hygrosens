CREATE TABLE hygrosens (
  SampleKey int NOT NULL  auto_increment,
  SerialNumber varchar(20),
  Channel int,
  Type int,
  Family int,
  SampleTime timestamp,
  Value real,
  PRIMARY KEY (SampleKey),
  KEY SerialIndex (SerialNumber(20))
);

