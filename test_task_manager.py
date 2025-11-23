import mysql.connector
import pytest
from task_manager import vytvoreni_tabulky, pridat_ukol, aktualizovat_ukol, odstranit_ukol

@pytest.fixture(scope="function")
def db_setup():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password"
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE test")
    conn.database = "test"

    cursor.execute("""
        CREATE TABLE ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(100),
            popis TEXT,
            stav VARCHAR(20) DEFAULT 'Nezahájeno',
            datum_vytvoreni DATE
        )
    """)
    conn.commit()

    yield conn, cursor

    cursor.execute("DROP TABLE IF EXISTS ukoly")
    cursor.execute("DROP DATABASE IF EXISTS test")
    conn.commit()

    cursor.close()
    conn.close()

def test_pridat_ukol_pozitivni(db_setup):
    conn, cursor = db_setup
    pridat_ukol(conn, cursor, "test_nazev", "test_popis")
    cursor.execute("SELECT nazev, popis FROM ukoly WHERE nazev = %s", ("test_nazev",))
    result = cursor.fetchone()
    assert result == ("test_nazev", "test_popis")

def test_aktualizovat_ukol_pozitivni(db_setup):
    conn, cursor = db_setup
    cursor.execute('''
        INSERT INTO ukoly (nazev, popis, datum_vytvoreni)
        VALUES (%s, %s, CURDATE())
    ''', ("nazev", "popis"))
    conn.commit()

    aktualizovat_ukol(conn, cursor, 1, 1)
    cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (1,))
    result = cursor.fetchall()
    assert result[0] == ("Probíhá",)

def test_odstranit_ukol_pozitivni(db_setup):
    conn, cursor = db_setup
    cursor.execute('''
        INSERT INTO ukoly (nazev, popis, datum_vytvoreni)
        VALUES (%s, %s, CURDATE())
    ''', ("nazev", "popis"))
    conn.commit()

    odstranit_ukol(conn, cursor, 1)
    cursor.execute("SELECT * FROM ukoly WHERE id = %s", (1,))
    result = cursor.fetchall()
    assert result == []

def test_pridat_ukol_negativni(db_setup):
    conn, cursor = db_setup
    nazev = ""
    with pytest.raises(ValueError, match="Zadán prázdný název úkolu. Opakujte zadání."):
        pridat_ukol(conn, cursor, nazev, "test_popis")

def test_aktualizovat_ukol_negativni(db_setup):
    conn, cursor = db_setup
    # Úkol neexistuje
    with pytest.raises(ValueError, match="Zadané ID neexistuje. Opakujte zadání."):
        aktualizovat_ukol(conn, cursor, 1, 1)

def test_odstranit_ukol_negativni(db_setup):
    conn, cursor = db_setup
    # Úkol neexistuje
    with pytest.raises(ValueError, match="Zadané ID neexistuje. Opakujte zadání."):
        odstranit_ukol(conn, cursor, 1)