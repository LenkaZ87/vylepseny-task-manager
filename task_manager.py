import mysql.connector

def pripojeni_db(nazev_db):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password"
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {nazev_db}")
        conn.commit()
        conn.database = nazev_db

    except mysql.connector.Error as err:
        print(f"Chyba při připojení k databázi: {err}")
        exit(1)

    return (conn, cursor)

def vytvoreni_tabulky(conn, cursor):
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(100),
            popis TEXT,
            stav VARCHAR(20) DEFAULT 'Nezahájeno',
            datum_vytvoreni DATE
            )
        ''')
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Chyba pri vytvářeni tabulky: {err}")
        exit(1)

def hlavni_menu(conn, cursor):
    while True:
        print()
        print("Správce úkolů - Hlavní menu")
        print("1. Přidat nový úkol")
        print("2. Zobrazit všechny úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Konec programu")
        moznost = input("Vyberte možnost (1-5):")

        if moznost == "1":
            while True:
                try:
                    pridat_ukol(conn, cursor)
                    break
                except ValueError as e:
                    print(e)
        elif moznost == "2":
            zobrazit_ukoly(conn, cursor)
        elif moznost == "3":
            while True:
                try:
                    aktualizovat_ukol(conn, cursor)
                    break
                except ValueError as e:
                    print(e)
        elif moznost == "4":
            while True:
                try:
                    odstranit_ukol(conn, cursor)
                    break
                except ValueError as e:
                    print(e)
        elif moznost == "5":
            print("Pápá")
            break
        else:
            print("Neplatná volba.  Opakujte volbu.")

def pridat_ukol(conn, cursor, nazev=None, popis=None):
    if nazev is None:
        nazev = input("Zadejte název úkolu:")
    if nazev == "":
        raise ValueError("Zadán prázdný název úkolu. Opakujte zadání.")

    if popis is None:
        popis = input("Zadejte popis úkolu:")
    if popis == "":
        raise ValueError("Zadán prázdný popis úkolu. Opakujte zadání.")
    
    cursor.execute('''
        INSERT INTO ukoly (nazev, popis, datum_vytvoreni)
        VALUES (%s, %s, CURDATE())
    ''', (nazev, popis))
    conn.commit()

def zobrazit_ukoly(conn, cursor):
    cursor.execute("SELECT id, nazev, popis, stav FROM ukoly WHERE stav IN ('Nezahájeno', 'Probíhá')")
    ukoly = cursor.fetchall()
    if not ukoly:
        print("Seznam úkolů je prázdný.")
        return
    print("Seznam úkolů:")
    for ukol in ukoly:
        print(f"{ukol[0]}. {ukol[1]} - {ukol[2]} (Stav: {ukol[3]})")

def aktualizovat_ukol(conn, cursor, vybrane_id=None, nova_volba=None):
    zobrazit_ukoly(conn, cursor)

    cursor.execute("SELECT id, stav FROM ukoly")
    ukoly = cursor.fetchall()
    povolena_cisla = [row[0] for row in ukoly]

    if vybrane_id is None:
        vybrane_id = int(input("Zadejte ID úkolu pro aktualizaci:"))

    if vybrane_id in povolena_cisla:
        print("Vyberte nový stav úkolu:")
        print("1. Probíhá")
        print("2. Hotovo")
        if nova_volba is None:
            nova_volba = int(input("Zadejte číslo stavu:"))
        if nova_volba == 1:
            novy_stav = "Probíhá"
        elif nova_volba == 2:
            novy_stav = "Hotovo"
        else:
            raise ValueError("Neplatná volba stavu. Opakujte zadání.")

        cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, vybrane_id))
        conn.commit()
        print("Stav úkolu byl úspěšně změněn.")
    else:
        raise ValueError("Zadané ID neexistuje. Opakujte zadání.")

def odstranit_ukol(conn, cursor, odstran_ukol=None):
    zobrazit_ukoly(conn, cursor)

    cursor.execute("SELECT id FROM ukoly")
    povolena_cisla = [row[0] for row in cursor.fetchall()]

    if odstran_ukol is None:
        odstran_ukol = int(input("Zadejte čislo úkolu, který chcete odstranit:"))

    if odstran_ukol in povolena_cisla:
        cursor.execute("DELETE FROM ukoly WHERE id = %s", (odstran_ukol,))
        conn.commit()
    else:
        raise ValueError("Zadané ID neexistuje. Opakujte zadání.")

if __name__ == "__main__":
    (conn, cursor) = pripojeni_db("prod")
    vytvoreni_tabulky(conn, cursor)

    hlavni_menu(conn, cursor)

    cursor.close()
    conn.close()
