DROP TABLE IF EXISTS pivot;


CREATE TABLE pivot (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  Indices varchar NOT NULL,
  Row_Name varchar NOT NULL,
  Column_Name varchar NOT NULL,
  Mask int NOT NULL,
  SumGreaterThanZero int NOT NULL,
  Notes varchar
);