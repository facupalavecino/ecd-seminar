SELECT city_id, lat, lon
FROM cities
WHERE name = '{{ city_name }}' AND country = '{{ country }}';