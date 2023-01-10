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
    rain float8,
    snowfall float8,
    cloudcover float8,
    shortwave_radiation float8,
    measurement_time TIMESTAMP,
    UNIQUE(city_id, measurement_time),
    CONSTRAINT fk_city
        FOREIGN KEY(city_id) 
            REFERENCES cities(city_id)
);
comment on column weather_measurements.temperature is '	Air temperature at 2 meters above ground (ºC)';
comment on column weather_measurements.feels_like is 'The perceived feels-like temperature';
comment on column weather_measurements.pressure is 'Pressure at surface';
comment on column weather_measurements.humidity is 'Relative humidity at 2 meters above ground';
comment on column weather_measurements.rain is 'Rain of the preceding hour in millimeter';
comment on column weather_measurements.snowfall is 'Snowfall amount of the preceding hour in centimeters';
comment on column weather_measurements.cloudcover is 'Total cloud cover as an area fraction';
comment on column weather_measurements.shortwave_radiation is 'Shortwave solar radiation as average of the preceding hour';
GRANT ALL
ON weather_measurements
TO {{ params.user }};
