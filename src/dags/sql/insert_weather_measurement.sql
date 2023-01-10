INSERT INTO weather_measurements (city_id, temperature, feels_like, pressure, humidity, rain, snowfall, cloudcover, shortwave_radiation, measurement_time)
VALUES
{% for m in measurements %}
    ({{ city_id }}, {{ m.temperature_2m }}, {{ m.apparent_temperature }}, {{ m.surface_pressure }}, {{ m.relativehumidity_2m }}, {{ m.rain }}, {{ m.snowfall }}, {{ m.cloudcover }}, {{ m.shortwave_radiation }}, TIMESTAMP '{{ m.time }}'){{ "," if not loop.last else "" }}
{% endfor %}
ON CONFLICT ON CONSTRAINT weather_measurements_city_id_measurement_time_key
DO NOTHING;
