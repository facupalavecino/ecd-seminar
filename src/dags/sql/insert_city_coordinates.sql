INSERT INTO cities (name, country, lat, lon)
VALUES ('{{ city_name }}', '{{ country }}', {{ lat }}, {{ lon }})
ON CONFLICT ON CONSTRAINT cities_name_country_key
DO NOTHING
RETURNING city_id;
