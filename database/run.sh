docker rm -f astro-sandbox-dw
docker run --name astro-sandbox-dw -p 5433:5432 -e POSTGRES_PASSWORD=postgres --network=astro_c02597_airflow -d postgres