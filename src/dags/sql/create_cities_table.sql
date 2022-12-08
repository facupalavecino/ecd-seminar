CREATE TABLE IF NOT EXISTS cities (
    city_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    country VARCHAR(2) NOT NULL,
    lat float8 NOT NULL,
    lon float8 NOT NULL,
    UNIQUE (name, country)
);

GRANT ALL
ON cities
TO {{ params.user }};

CREATE TABLE IF NOT EXISTS weather_measurements (
    id SERIAL PRIMARY KEY,
    city_id INT,
    temperature float8,
    feels_like float8,
    pressure float8,
    humidity INT,
    measurement_time TIMESTAMP,
    UNIQUE(city_id, measurement_time),
    CONSTRAINT fk_city
        FOREIGN KEY(city_id) 
            REFERENCES cities(city_id)
);

GRANT ALL
ON weather_measurements
TO {{ params.user }};
