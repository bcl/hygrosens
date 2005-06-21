CREATE TABLE hygrosens (
  SampleKey bigint UNSIGNED NOT NULL auto_increment,
  SampleTime datetime NOT NULL,
  Channel int NOT NULL,
  SerialNumber varchar(20) NOT NULL,
  Type int NOT NULL,
  Family int NOT NULL,
  Value float NOT NULL, 
  PRIMARY KEY(SampleKey),
  KEY(SerialNumber),
  KEY(SampleTime),
  KEY(Value),
  KEY(Type),
  KEY(Family)
);
