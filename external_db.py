import sqlite3
import os

from settings import Settings


class ExternalDatabase:
    """Klasse für den Zugriff auf die externe SQLite-Datenbank."""

    def __init__(self, db_path):
        self.db_path = db_path
        if not os.path.isabs(self.db_path):  # Wenn der Pfad nicht absolut ist
            settings = Settings("settings.ini")
            base_dir = settings.get_setting("PATH", "directory")
            self.db_path = os.path.join(base_dir, self.db_path)  # Pfad relativ zum Basisverzeichnis machen

        # ... (Verbindung zur Datenbank herstellen)

    def get_waagen_by_kunde(self, kundennummer):
        """Liest alle relevanten Informationen (Waagen, Aufträge, Adressen, Aufheizzyklus, Temp. Herstellertoleranz) für einen bestimmten Kunden."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT 
                        IFNULL(kdw.kdw_bezeichnung, ''), 
                        IFNULL(kdw.kdw_snr, ''), 
                        IFNULL(kdw.kdw_ident_nr, ''), 
                        IFNULL(hersteller_adr.adr_name1, ''), 
                        IFNULL(kdw.kdw_modell, ''),
                        IFNULL(kdw.kdw_standort, ''), 
                        IFNULL(kdw.kdw_raum, ''), 
                        IFNULL(kdw.kdw_luftbewegung, ''), 
                        IFNULL(kdw.kdw_unruhe, ''),
                        IFNULL(kdw.kdw_verschmutzung, ''), 
                        IFNULL(kdw.kdw_waegebereich1, ''), 
                        IFNULL(kdw.kdw_waegebereich2, ''),
                        IFNULL(kdw.kdw_waegebereich3, ''), 
                        IFNULL(kdw.kdw_waegebereich4, ''), 
                        IFNULL(kdw.kdw_teilungswert1, ''),
                        IFNULL(kdw.kdw_teilungswert2, ''), 
                        IFNULL(kdw.kdw_teilungswert3, ''), 
                        IFNULL(kdw.kdw_teilungswert4, ''),
                        IFNULL(kdw.kdw_feuchte_min, ''), 
                        IFNULL(kdw.kdw_feuchte_max, ''), 
                        IFNULL(kdw.kdw_dakks_intervall, ''),
                        IFNULL(auf.auf_nummer_bez, ''),  
                        IFNULL(kunde_adr.adr_name1, ''), 
                        IFNULL(kunde_adr.adr_name2, ''), 
                        IFNULL(kunde_adr.adr_name3, ''), 
                        IFNULL(kunde_adr.adr_strasse, ''), 
                        IFNULL(kunde_adr.adr_plz, ''), 
                        IFNULL(kunde_adr.adr_ort, ''), 
                        (
                            SELECT IFNULL(bdw.bdw_int, '') 
                            FROM benutzerdefwerte bdw
                            JOIN benutzerdef bdf ON bdw.bdw_bdf_guid = bdf.bdf_guid
                            WHERE bdw.bdw_obj_guid = kdw.kdw_guid 
                              AND bdf.bdf_name = 'Feuchtebestimmer Aufheizzyklus in min'
                        ) AS Aufheizzyklus,
                        (
                            SELECT IFNULL(bdw.bdw_dec, '')  
                            FROM benutzerdefwerte bdw
                            JOIN benutzerdef bdf ON bdw.bdw_bdf_guid = bdf.bdf_guid
                            WHERE bdw.bdw_obj_guid = kdw.kdw_guid 
                              AND bdf.bdf_name = 'Feuchtebestimmer Herstellertoleranz'
                        ) AS TempHerstellertoleranz 
                    FROM kundenwaage kdw
                    LEFT JOIN adress kunde_adr ON kdw.kdw_kunde = kunde_adr.adr_nummer 
                    LEFT JOIN adress hersteller_adr ON kdw.kdw_hersteller = hersteller_adr.adr_nummer 
                    LEFT JOIN auftrag auf ON kdw.kdw_kunde = auf.auf_kunde 
                    WHERE kdw.kdw_kunde = ?
                    """,
                    (kundennummer,),
                )
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Fehler beim Lesen der Datenbank: {e}")
            return []

    def get_auftragsinformationen(self):
        """Liest Auftragsinformationen (Auftragsnummer und Firma) aus der Datenbank."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Abfrage angepasst, um Auftragsnummer, Kundennummer und Firmennamen zu erhalten
                cursor.execute("""
                    SELECT auf_nummer_bez, auf_kunde, adr_name1 
                    FROM auftrag
                    JOIN adress ON auf_kunde = adr_nummer
                    ORDER BY auf_nr DESC
                """)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Fehler beim Lesen der Datenbank: {e}")
            return []

    def get_auftragsdaten(self, auftragsnummer):
        """Gibt die Kundennummer und den Kundennamen für eine bestimmte Auftragsnummer zurück."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT auf_kunde FROM auftrag WHERE auf_nummer_bez = ?", (auftragsnummer,))
                kundennummer = cursor.fetchone()
                if kundennummer:
                    cursor.execute("SELECT adr_name1 FROM adress WHERE adr_nummer = ?", (kundennummer[0],))
                    kunde = cursor.fetchone()
                    return kundennummer[0], kunde[0] if kunde else None
                else:
                    return None, None
        except sqlite3.Error as e:
            print(f"Fehler beim Lesen der Datenbank: {e}")
            return None, None
