import configparser
import os
import sys


class Settings:
    """Klasse zum Lesen und Schreiben von Einstellungen aus einer INI-Datei.

    Im gepackten Modus (sys.frozen) werden Settings und Bilder in
    %APPDATA%/WJPruefpilot/ gespeichert. In der Entwicklung bleibt
    alles im Projektordner.
    """

    def __init__(self, config_file='settings.ini'):
        self._config_dir = self._ermittle_config_verzeichnis()
        os.makedirs(self._config_dir, exist_ok=True)
        self.config_file = os.path.join(self._config_dir, config_file)

        self.config = configparser.ConfigParser()
        self.data = {}

        erst_start = not os.path.exists(self.config_file)

        try:
            self.config.read(self.config_file)
        except configparser.Error:
            pass

        if erst_start:
            self._setze_erststart_defaults()

        self.load_settings()

    @staticmethod
    def _ermittle_config_verzeichnis():
        """Gibt das Verzeichnis fuer settings.ini und data/ zurueck."""
        if getattr(sys, 'frozen', False):
            return os.path.join(os.environ['APPDATA'], 'WJPruefpilot')
        return os.path.dirname(os.path.abspath(__file__))

    def _setze_erststart_defaults(self):
        """Schreibt sinnvolle Standardwerte beim allerersten Start."""
        # Protokollpfad: Ordner neben der .exe (frozen) oder neben dem Projekt (dev)
        if getattr(sys, 'frozen', False):
            protokoll_pfad = os.path.join(
                os.path.dirname(sys.executable), 'Protokolle'
            )
        else:
            protokoll_pfad = os.path.join(os.getcwd(), 'Protokolle')
        self.set_setting('PATH', 'protokolle', protokoll_pfad)

        self.set_setting('ALLGEMEIN', 'theme', 'dark')

        # Standard-Temperaturen
        self.set_setting('SYSTEM', 'soll_temp1', '100,0')
        self.set_setting('SYSTEM', 'soll_temp2', '160,0')
        self.set_setting('SYSTEM', 'umgebung_temp', '22,0')

        # VDE-Standardwerte
        self.set_setting('SYSTEM', 'nennspannung', '230')
        self.set_setting('SYSTEM', 'frequenz', '50')
        self.set_setting('SYSTEM', 'cosphi', '1')

    def get_setting(self, section, option, default=None):
        """Liest eine Einstellung oder gibt den Standardwert zurück."""
        if not self.config.has_section(section):
            return default
        return self.config.get(section, option, fallback=default)

    def set_setting(self, section, option, value):
        """Schreibt eine Einstellung in die INI-Datei.
        Liest die Datei vorher neu ein, damit Aenderungen anderer Instanzen nicht verloren gehen."""
        # INI neu einlesen um Konflikte mit anderen Instanzen zu vermeiden
        try:
            self.config.read(self.config_file)
        except configparser.Error:
            pass
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def get_sqlite_databases(self, directory):
        """Gibt eine Liste aller sqlite-Dateien im angegebenen Verzeichnis zurück."""
        databases = []
        for file in os.listdir(directory):
            if file.endswith(".sqlite"):
                databases.append(file)
        return databases

    def set_selected_database(self, database_name):
        """Speichert den Namen der ausgewählten Datenbank in der INI-Datei."""
        self.set_setting('DATABASE', 'name', database_name)

    def get_selected_database(self):
        """Liest den Namen der ausgewählten Datenbank aus der INI-Datei."""
        return self.get_setting('DATABASE', 'name', None)

    def set_company_data(self, firma, strasse, plz, ort):
        """Speichert die Firmendaten in der INI-Datei."""
        self.set_setting('FIRMA', 'firma', firma)
        self.set_setting('FIRMA', 'strasse', strasse)
        self.set_setting('FIRMA', 'plz', plz)
        self.set_setting('FIRMA', 'ort', ort)

    def get_company_data(self):
        """Liest die Firmendaten aus der INI-Datei."""
        return {
            'firma': self.get_setting('FIRMA', 'firma', ''),
            'strasse': self.get_setting('FIRMA', 'strasse', ''),
            'land': self.get_setting('FIRMA', 'land', 'Germany'),
            'telefon': self.get_setting('FIRMA', 'telefon', ''),
            'webseite': self.get_setting('FIRMA', 'webseite', ''),
            'plz': self.get_setting('FIRMA', 'plz', ''),
            'ort': self.get_setting('FIRMA', 'ort', ''),
        }

    def get_pruefer_name(self):
        """Liest den Namen des Prüfers aus der INI-Datei."""
        return self.get_setting('PRUEFER', 'name', '')

    def set_pruefer_name(self, name):
        """Speichert den Namen des Prüfers in der INI-Datei."""
        self.set_setting('PRUEFER', 'name', name)

    def get_messgeraete(self):
        """Liest die Messgeräte-Daten aus der INI-Datei."""
        messgeraete = {}
        for i in range(1, 11):
            messgeraete[f'Temperaturmessgeraet_{i}'] = self.get_setting('MESSGERAETE', f'Temperaturmessgeraet_{i}', '')
            messgeraete[f'VDE-Messgeraet_{i}'] = self.get_setting('MESSGERAETE', f'VDE-Messgeraet_{i}', '')
        return messgeraete

    def set_messgeraete(self, messgeraete):
        """Speichert die Messgeräte-Daten in der INI-Datei."""
        for name, wert in messgeraete.items():
            self.set_setting('MESSGERAETE', name, wert)

    def _bild_pfad_aufloesen(self, section, option):
        """Loest einen Bild-Dateinamen zur vollstaendigen Pfadangabe auf.
        Sucht zuerst in data/, dann im Arbeitsverzeichnis."""
        filename = self.get_setting(section, option, '')
        if not filename:
            return None
        data_pfad = os.path.join(self.get_data_verzeichnis(), filename)
        if os.path.exists(data_pfad):
            return data_pfad
        return os.path.join(os.getcwd(), filename)

    def get_logo_path(self):
        """Liest den Pfad zum Firmenlogo aus der INI-Datei."""
        return self._bild_pfad_aufloesen('FIRMA', 'logo')

    def get_signature_path(self):
        """Liest den Pfad zur Unterschrift aus der INI-Datei."""
        return self._bild_pfad_aufloesen('PRUEFER', 'unterschrift')

    def get_stamp_path(self):
        """Liest den Pfad zum Firmenstempel aus der INI-Datei."""
        return self._bild_pfad_aufloesen('FIRMA', 'stempel')

    def set_stamp_path(self, path):
        """Speichert den Pfad zum Firmenstempel in der INI-Datei."""
        filename = os.path.basename(path)
        self.set_setting('FIRMA', 'stempel', filename)

    def set_protokoll_path(self, path):
        """Speichert den Pfad für die Protokolle in der INI-Datei."""
        self.set_setting('PATH', 'protokolle', path)

    def get_protokoll_path(self):
        """Liest den Pfad fuer die Protokolle aus der INI-Datei."""
        if getattr(sys, 'frozen', False):
            standard = os.path.join(os.path.dirname(sys.executable), 'Protokolle')
        else:
            standard = os.path.join(os.getcwd(), 'Protokolle')
        return self.get_setting('PATH', 'protokolle', standard)

    # --- Data-Verzeichnis ---

    def get_data_verzeichnis(self):
        """Gibt den Pfad zum data/-Ordner zurueck (erstellt ihn bei Bedarf)."""
        data_pfad = os.path.join(os.path.dirname(os.path.abspath(self.config_file)), 'data')
        os.makedirs(data_pfad, exist_ok=True)
        return data_pfad

    # --- Theme ---

    def get_theme(self):
        """Liest das gespeicherte Theme (dark/light)."""
        return self.get_setting('ALLGEMEIN', 'theme', 'dark')

    def set_theme(self, theme):
        """Speichert das Theme (dark/light)."""
        self.set_setting('ALLGEMEIN', 'theme', theme)

    # --- Datenbank-Verzeichnis ---

    def get_db_verzeichnis(self):
        """Liest den Pfad zum Datenbank-Ordner."""
        return self.get_setting('PATH', 'directory', '')

    def set_db_verzeichnis(self, pfad):
        """Speichert den Pfad zum Datenbank-Ordner."""
        self.set_setting('PATH', 'directory', pfad)

    # --- Pruefer-Kuerzel ---

    def get_pruefer_kuerzel(self):
        """Liest das Pruefer-Kuerzel. Wenn leer, wird es aus dem Namen generiert."""
        kuerzel = self.get_setting('PRUEFER', 'kuerzel', '')
        if kuerzel:
            return kuerzel
        # Automatisch aus Name generieren
        name = self.get_pruefer_name()
        if name:
            return ''.join([teil[0].upper() for teil in name.split() if teil])
        return ''

    def set_pruefer_kuerzel(self, kuerzel):
        """Speichert das Pruefer-Kuerzel."""
        self.set_setting('PRUEFER', 'kuerzel', kuerzel)

    # --- Messgeraete (strukturiert) ---

    def get_messgeraete_strukturiert(self, typ="temp"):
        """Liest Messgeraete als Liste von Dicts [{name, seriennummer}].

        Args:
            typ: "temp" oder "vde"
        """
        prefix = "Temperaturmessgeraet" if typ == "temp" else "VDE-Messgeraet"
        geraete = []
        for i in range(1, 11):
            wert = self.get_setting('MESSGERAETE', f'{prefix}_{i}', '')
            if not wert:
                continue
            # Format: "Name (S/N: Seriennummer)" oder alter Stil ohne S/N
            if ' (S/N: ' in wert and wert.endswith(')'):
                teile = wert.rsplit(' (S/N: ', 1)
                name = teile[0]
                sn = teile[1][:-1]  # Klammer am Ende entfernen
            else:
                name = wert
                sn = ''
            geraete.append({'name': name, 'seriennummer': sn})
        return geraete

    def set_messgeraete_strukturiert(self, typ, geraete_liste):
        """Speichert Messgeraete aus einer Liste von Dicts.

        Args:
            typ: "temp" oder "vde"
            geraete_liste: [{"name": ..., "seriennummer": ...}, ...]
        """
        prefix = "Temperaturmessgeraet" if typ == "temp" else "VDE-Messgeraet"
        for i in range(1, 11):
            if i <= len(geraete_liste):
                g = geraete_liste[i - 1]
                name = g.get('name', '').strip()
                sn = g.get('seriennummer', '').strip()
                if name and sn:
                    wert = f"{name} (S/N: {sn})"
                elif name:
                    wert = name
                else:
                    wert = ''
            else:
                wert = ''
            self.set_setting('MESSGERAETE', f'{prefix}_{i}', wert)

    # --- Standard-Werte (System) ---

    def get_standard_soll_temp1(self):
        """Standard-Solltemperatur Pruefpunkt 1."""
        return self.get_setting('SYSTEM', 'soll_temp1', '100,0')

    def set_standard_soll_temp1(self, wert):
        self.set_setting('SYSTEM', 'soll_temp1', wert)

    def get_standard_soll_temp2(self):
        """Standard-Solltemperatur Pruefpunkt 2."""
        return self.get_setting('SYSTEM', 'soll_temp2', '160,0')

    def set_standard_soll_temp2(self, wert):
        self.set_setting('SYSTEM', 'soll_temp2', wert)

    def get_standard_umgebung_temp(self):
        """Standard-Umgebungstemperatur."""
        return self.get_setting('SYSTEM', 'umgebung_temp', '22,0')

    def set_standard_umgebung_temp(self, wert):
        self.set_setting('SYSTEM', 'umgebung_temp', wert)

    # --- VDE Standard-Werte ---

    def get_standard_nennspannung(self):
        return self.get_setting('SYSTEM', 'nennspannung', '230')

    def set_standard_nennspannung(self, wert):
        self.set_setting('SYSTEM', 'nennspannung', wert)

    def get_standard_frequenz(self):
        return self.get_setting('SYSTEM', 'frequenz', '50')

    def set_standard_frequenz(self, wert):
        self.set_setting('SYSTEM', 'frequenz', wert)

    def get_standard_cosphi(self):
        return self.get_setting('SYSTEM', 'cosphi', '1')

    def set_standard_cosphi(self, wert):
        self.set_setting('SYSTEM', 'cosphi', wert)

    # --- VDE Messwerte-Standardwerte ---

    def get_standard_rpe(self):
        return self.get_setting('SYSTEM', 'rpe', '0,3')

    def set_standard_rpe(self, wert):
        self.set_setting('SYSTEM', 'rpe', wert)

    def get_standard_riso(self):
        return self.get_setting('SYSTEM', 'riso', '1,0')

    def set_standard_riso(self, wert):
        self.set_setting('SYSTEM', 'riso', wert)

    def get_standard_ipe(self):
        return self.get_setting('SYSTEM', 'ipe', '0,5')

    def set_standard_ipe(self, wert):
        self.set_setting('SYSTEM', 'ipe', wert)

    def get_standard_ib(self):
        return self.get_setting('SYSTEM', 'ib', '0,5')

    def set_standard_ib(self, wert):
        self.set_setting('SYSTEM', 'ib', wert)

    def get_infobox_anzeigen(self, key):
        """Ob eine spezifische Infobox angezeigt werden soll."""
        return self.get_setting('INFOBOXEN', key, '1') == '1'

    def set_infobox_anzeigen(self, key, anzeigen):
        self.set_setting('INFOBOXEN', key, '1' if anzeigen else '0')

    # --- Fenster-Zustand ---

    def get_fenster_geometrie(self):
        """Gibt (x, y, breite, hoehe) oder None zurueck."""
        x = self.get_setting('FENSTER', 'x', None)
        if x is None:
            return None
        try:
            return (
                int(self.get_setting('FENSTER', 'x', '0')),
                int(self.get_setting('FENSTER', 'y', '0')),
                int(self.get_setting('FENSTER', 'breite', '1000')),
                int(self.get_setting('FENSTER', 'hoehe', '700')),
            )
        except ValueError:
            return None

    def set_fenster_geometrie(self, x, y, breite, hoehe):
        self.set_setting('FENSTER', 'x', str(x))
        self.set_setting('FENSTER', 'y', str(y))
        self.set_setting('FENSTER', 'breite', str(breite))
        self.set_setting('FENSTER', 'hoehe', str(hoehe))

    def get_fenster_maximiert(self):
        return self.get_setting('FENSTER', 'maximiert', 'false') == 'true'

    def set_fenster_maximiert(self, maximiert):
        self.set_setting('FENSTER', 'maximiert', 'true' if maximiert else 'false')

    def get_sidebar_ausgeklappt(self):
        return self.get_setting('FENSTER', 'sidebar_ausgeklappt', 'false') == 'true'

    def set_sidebar_ausgeklappt(self, ausgeklappt):
        self.set_setting('FENSTER', 'sidebar_ausgeklappt', 'true' if ausgeklappt else 'false')

    def get_aktive_seite(self):
        return self.get_setting('FENSTER', 'aktive_seite', 'auftraege')

    def set_aktive_seite(self, seite):
        self.set_setting('FENSTER', 'aktive_seite', seite)

    def get_letzter_auftrag(self):
        """Gibt die zuletzt gewaehlte Auftragsnummer zurueck."""
        return self.get_setting('FENSTER', 'letzter_auftrag', '')

    def set_letzter_auftrag(self, auftragsnummer):
        self.set_setting('FENSTER', 'letzter_auftrag', auftragsnummer)

    def get_settings_tab(self):
        """Gibt den zuletzt aktiven Settings-Tab-Index zurueck."""
        try:
            return int(self.get_setting('FENSTER', 'settings_tab', '0'))
        except ValueError:
            return 0

    def set_settings_tab(self, index):
        self.set_setting('FENSTER', 'settings_tab', str(index))

    def reload(self):
        """Liest die INI-Datei neu ein (nach externen Aenderungen)."""
        self.config = configparser.ConfigParser()
        try:
            self.config.read(self.config_file)
        except configparser.Error:
            pass
        self.load_settings()

    def load_settings(self):
        """Liest die Einstellungen aus der INI-Datei in self.data."""
        self.data = {}
        for section in self.config.sections():
            for key, value in self.config.items(section):
                self.data[key] = value
