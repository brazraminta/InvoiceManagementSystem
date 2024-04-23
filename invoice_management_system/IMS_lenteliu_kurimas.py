import psycopg2

conn_params = {
    "host": "localhost",
    "database": "invoiceManagementSystem",  #pakeisti
    "user": "postgres",
    "password": "riko789",
    "port": "5432"
}

def delete_table(conn_params):
    try:
        with psycopg2.connect(**conn_params) as connection:
            with connection.cursor() as cursor:
                delete_query = """
                    DROP TABLE if EXISTS israsomos_saskaitos, gaunamos_saskaitos, klientai, tiekejai, projektai
        """
            cursor.execute(delete_query)
            print("Tables deleted successfuly")
            connection.commit()

    except Exception as e:
            print(f"Error from check_registry_of_invoices: {e}")

delete_table(conn_params)


def create_table(conn_params):
    try:
        connection = psycopg2.connect(**conn_params)
        cursor = connection.cursor()

        # išrašomų sąskaitų lentelės sukūrimas
        create_query1 = """
            CREATE TABLE IF NOT EXISTS israsomos_saskaitos(
                saskaitos_id SERIAL PRIMARY KEY,
                kliento_id INTEGER REFERENCES klientai(kliento_id),
                projekto_id INTEGER REFERENCES projektai(projekto_id)
                saskaitos_numeris VARCHAR(255),                
                dokumento_data DATE,
                apmoketi_iki DATE,
                suma_be_PVM DECIMAL,
                pvm_21 DECIMAL,
                suma_suPVM DECIMAL,
                moketina_suma DECIMAL,
                PVM96_str VARCHAR(50))
        """

        # gautų sąskaitų registracijos lentelės sukūrimas
        create_query2 = """
            CREATE TABLE IF NOT EXISTS gaunamos_saskaitos(
                saskaitos_id SERIAL PRIMARY KEY,
                projekto_id INTEGER REFERENCES projektai(projekto_id),
                tiekejo_id INTEGER REFERENCES tiekejai(tiekejo_id),
                saskaitos_nr VARCHAR(255),
                saskaitos_data DATE,
                apmoketi_iki DATE,
                apmokejimo_skubumas TEXT,
                apmokejimo_busena TEXT,
                kada_apmoketa DATE,
                pastabos TEXT)
            """

        # tiekėjų lentelės sukūrimas
        create_query3 = """
        CREATE TABLE IF NOT EXISTS tiekejai(
            tiekejo_id SERIAL PRIMARY KEY,
            tiekejo_pavadinimas VARCHAR(255),
            tiekejo_adresas VARCHAR(255),
            tel_nr VARCHAR(50),
            saskaitos_nr VARCHAR(50))
            """

        # klientų lentelės sukūrimas
        create_query4 = """
        CREATE TABLE IF NOT EXISTS klientai(
            kliento_id SERIAL PRIMARY KEY,
            projekto_id INTEGER REFERENCES projektai(projekto_id),
            kliento_pavadinimas VARCHAR(255),
            kliento_adresas VARCHAR(255),
            tel_nr. VARCHAR(50))            
        """

        # projektų lentelės sukūrimas
        create_query5 = """
        CREATE TABLE IF NOT EXISTS projektai(
            projekto_id SERIAL PRIMARY KEY,
            kliento_id INTEGER REFERENCES klientai(kliento_id),
            projekto_nr VARCHAR(50),
            projekto_aprašymas TEXT,
            projekto_adresas VARCHAR(255),
            atlikimo_pradzia DATE,
            atlikimo_terminas DATE
        )
        """

        cursor.execute(create_query1)
        cursor.execute(create_query2)
        cursor.execute(create_query3)
        cursor.execute(create_query4)
        cursor.execute(create_query5)

        print("Tables created successfuly")

        connection.commit()
        cursor.close()
        connection.close()

    except Exception as e:
        print(f"Error from create_table: {e}")

create_table(conn_params)

