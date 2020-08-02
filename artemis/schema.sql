DROP TABLE IF EXISTS pivot;


CREATE TABLE pivot (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pivot_column varchar NOT NULL,
  value_column varchar NOT NULL,
  notes varchar,
  mask int NOT NULL,
  sumGreaterThanZero int NOT NULL
);