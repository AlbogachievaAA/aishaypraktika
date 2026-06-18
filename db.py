import psycopg2
from datetime import date


KONFIG_BD = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "***",
    "host": "localhost",
    "port": 5432
}

def poluchit_soedinenie():
    return psycopg2.connect(**KONFIG_BD)

def init_db():
    with poluchit_soedinenie() as conn:
        with conn.cursor() as cur:
            cur.execute(open("schema.sql").read())
        conn.commit()

def dobavit_zapis(id_polzovatelya, nastroenie, chasy_ucheby, chasy_sna, kommentariy=""):
    segodnya = date.today()
    with poluchit_soedinenie() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO daily_log (user_id, date, mood, study_hours, sleep_hours, comment)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, date) DO UPDATE SET
                    mood = EXCLUDED.mood,
                    study_hours = EXCLUDED.study_hours,
                    sleep_hours = EXCLUDED.sleep_hours,
                    comment = EXCLUDED.comment
            ''', (id_polzovatelya, segodnya, nastroenie, chasy_ucheby, chasy_sna, kommentariy))
        conn.commit()

def poluchit_zapisi(id_polzovatelya, dney_nazad=30):
    with poluchit_soedinenie() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT date, mood, study_hours, sleep_hours, comment
                FROM daily_log
                WHERE user_id = %s AND date >= CURRENT_DATE - %s
                ORDER BY date
            ''', (id_polzovatelya, dney_nazad))
            stroki = cur.fetchall()
    return [{"data": r[0], "nastroenie": r[1], "chasy_ucheby": r[2], "chasy_sna": r[3], "kommentariy": r[4]} for r in stroki]

def poluchit_vse_zapisi(id_polzovatelya):
    with poluchit_soedinenie() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT date, mood, study_hours, sleep_hours, comment
                FROM daily_log
                WHERE user_id = %s
                ORDER BY date DESC
            ''', (id_polzovatelya,))
            stroki = cur.fetchall()
    return [{"data": r[0], "nastroenie": r[1], "chasy_ucheby": r[2], "chasy_sna": r[3], "kommentariy": r[4]} for r in stroki]

def ochistit_dannye_polzovatelya(id_polzovatelya):
    with poluchit_soedinenie() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM daily_log WHERE user_id = %s", (id_polzovatelya,))
        conn.commit()
get_connection = poluchit_soedinenie
