CREATE TABLE hygrosens (
  ReadingKey bigint UNSIGNED NOT NULL auto_increment,
  SerialNumber varchar(20) NOT NULL,
  Channel int NOT NULL,
  Type int NOT NULL,
  Family int NOT NULL,
  RecTime timestamp NOT NULL,
  Value float NOT NULL, 
  PRIMARY KEY(ReadingKey),
  KEY(SerialNumber),
  KEY(RecTime),
  KEY(Value),
  KEY(Type),
  KEY(Family)
);
