CREATE TABLE IF NOT EXISTS DIM_types (
    type_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    type_desc TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS DIM_trucks (
    truck_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    truck_name TEXT NOT NULL UNIQUE,
    truck_desc TEXT,
    truck_has_card_reader BOOLEAN NOT NULL,
    truck_fsa_rating INT
);

CREATE TABLE IF NOT EXISTS FACT_transactions (
    transaction_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    total FLOAT NOT NULL,
    type_id INT NOT NULL,
    truck_id INT NOT NULL,
    transaction_time TIMESTAMP NOT NULL,
    FOREIGN KEY (type_id) REFERENCES DIM_types (type_id),
    FOREIGN KEY (truck_id) REFERENCES DIM_trucks (truck_id)
);
