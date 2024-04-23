import psycopg2

db_params = {
    "host": "localhost",
    "database": "invoiceManagementSystem",  #pakeisti
    "user": "postgres",
    "password": "riko789",
    "port": "5432"
}

def create_table(db_params):
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # sąskaitų registravimo lentlės sukūrimas
        create_query = """CREATE TABLE IF NOT EXISTS saskaitos(
        saskaitos_id SERIAL PRIMARY KEY,
        projekto_numeris VARCHAR(255),
        tiekejo_pavadinimas VARCHAR(255),
        saskaitos_nr VARCHAR(255),
        saskaitos_data DATE,
        apmoketi_iki DATE,
        apmokejimo_skubumas VARCHAR(255),
        apmokejimo_busena VARCHAR(255),
        kada_apmoketa DATE,
        pastabos VARCHAR(255))
        """

        cursor.execute(create_query)
        print("Lentelė sukurta sėkmingai")

        connection.commit()
        cursor.close()
        connection.close()

    except Exception as e:
        print(f'Error in create_table: {e}')

create_table(db_params)