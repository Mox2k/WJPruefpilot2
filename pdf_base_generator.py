import os
import sys
import configparser
import base64
import io

from string import Template
from datetime import datetime, timedelta
from PIL import Image


class PDFGeneratorBase:
    """Basisklasse fuer PDF-Generatoren mit gemeinsamen Methoden."""

    def __init__(self):
        self.stored_data = {}
        self.data_to_append = {}

    def add_title(self, title):
        self.stored_data['title_data'] = title

    def add_company_and_inspector_data(self):
        """Fügt Firmen- und Prüferdaten aus der Konfigurationsdatei hinzu."""
        config = configparser.ConfigParser()
        config.read('settings.ini')

        firma = config['FIRMA']['firma']
        strasse = config['FIRMA']['strasse']
        plz = config['FIRMA']['plz']
        ort = config['FIRMA']['ort']
        land = config.get('FIRMA', 'land', fallback='Germany')
        telefon = config.get('FIRMA', 'telefon', fallback='')
        webseite = config.get('FIRMA', 'webseite', fallback='')

        logo_bild = self._resolve_bild_pfad(config['FIRMA']['logo'])
        pruefer_name = config['PRUEFER']['name']
        unterschrift_bild = self._resolve_bild_pfad(config['PRUEFER']['unterschrift'])
        stempel_bild = self._resolve_bild_pfad(config['FIRMA']['stempel'])

        # Initialisiere logo_str, img_str und stempel_str mit leeren Strings
        logo_str = ""
        img_str = ""
        stempel_str = ""

        try:
            # Überprüfen Sie, ob die Dateien existieren
            if not os.path.exists(logo_bild):
                raise FileNotFoundError(f"Logobild nicht gefunden: {logo_bild}")
            if not os.path.exists(unterschrift_bild):
                raise FileNotFoundError(f"Unterschriftsbild nicht gefunden: {unterschrift_bild}")
            if not os.path.exists(stempel_bild):
                raise FileNotFoundError(f"Stempelbild nicht gefunden: {stempel_bild}")

            logo_str = self._verarbeite_bild(logo_bild, breite=1600)
            img_str = self._verarbeite_bild(unterschrift_bild, hoehe=600)
            stempel_str = self._verarbeite_bild(stempel_bild, breite=800)

        except (FileNotFoundError, OSError) as e:
            print(f"Error loading or processing image: {e}")

        self.data_to_append['company_and_inspector_data'] = {
            'firma': firma,
            'strasse': strasse,
            'plz': plz,
            'ort': ort,
            'land': land,
            'telefon': telefon,
            'webseite': webseite,
            'logo_str': logo_str,
            'pruefer_name': pruefer_name,
            'unterschrift_str': img_str,
            'stempel_str': stempel_str
        }

    def add_waagen_data(self, waage_data):
        kdw_bezeichnung, kdw_snr, kdw_ident_nr, hersteller_name, kdw_modell, kdw_standort, kdw_raum, kdw_luftbewegung, kdw_unruhe, kdw_verschmutzung, \
            kdw_waegebereich1, kdw_waegebereich2, kdw_waegebereich3, kdw_waegebereich4, kdw_teilungswert1, kdw_teilungswert2, \
            kdw_teilungswert3, kdw_teilungswert4, kdw_feuchte_min, kdw_feuchte_max, kdw_dakks_intervall, auf_nummer_bez, \
            kunde_name1, kunde_name2, kunde_name3, kunde_strasse, kunde_plz, kunde_ort, aufheizzyklus, temp_herstellertoleranz = waage_data

        # Erstelle ein Dictionary mit allen Daten
        waage_data_dict = {
            'WJ-Nummer': kdw_bezeichnung,
            'S/N': kdw_snr,
            'Inventarnummer': kdw_ident_nr,
            'Hersteller': hersteller_name,
            'Modell': kdw_modell,
            'Standort': kdw_standort,
            'Raum': kdw_raum,
            'Luftbewegung': kdw_luftbewegung,
            'Unruhe': kdw_unruhe,
            'Verschmutzung': kdw_verschmutzung,
            'Bereich1': kdw_waegebereich1,
            'Bereich2': kdw_waegebereich2,
            'Bereich3': kdw_waegebereich3,
            'Bereich4': kdw_waegebereich4,
            'Teilung1': kdw_teilungswert1,
            'Teilung2': kdw_teilungswert2,
            'Teilung3': kdw_teilungswert3,
            'Teilung4': kdw_teilungswert4,
            'Feuchte Min': kdw_feuchte_min,
            'Feuchte Max': kdw_feuchte_max,
            'DAkkS-Intervall': kdw_dakks_intervall,
            'Auftragsnummer': auf_nummer_bez,
            'Kunde_name1': kunde_name1,
            'Kunde_name2': kunde_name2,
            'Kunde_name3': kunde_name3,
            'Kunde_Strasse': kunde_strasse,
            'Kunde_plz': kunde_plz,
            'Kunde_ort': kunde_ort,
            'Aufheizzyklus': aufheizzyklus,
            'TempHerstellertoleranz': temp_herstellertoleranz
        }

        # Filtere die Daten
        filtered_waage_data = {}
        for key, value in waage_data_dict.items():
            if key.startswith(('Bereich', 'Teilung')):
                if value != '0' and value != 0:
                    filtered_waage_data[key] = value
            else:
                filtered_waage_data[key] = value

        # Speichere die gefilterten Daten
        self.data_to_append['waage_data'] = filtered_waage_data

    def add_pruefdatum_bemerkungen(self, pruefdatum, bemerkungen):
        """Fügt Prüfdatum, Bemerkungen und das Datum ein Jahr später hinzu."""

        # Formatiere das Prüfdatum
        pruefdatum_obj = datetime.strptime(pruefdatum, "%d.%m.%Y")
        pruefdatum_str = pruefdatum_obj.strftime("%d.%m.%Y")

        # Berechne das Datum in einem Jahr
        datum_in_einem_jahr = pruefdatum_obj + timedelta(days=365)
        datum_in_einem_jahr_str = datum_in_einem_jahr.strftime("%m.%Y")

        # Speichere pruefdaten und bemerkungen
        self.data_to_append['pruefdatum'] = pruefdatum_str
        self.data_to_append['datum_in_einem_jahr'] = datum_in_einem_jahr_str
        self.data_to_append['bemerkungen'] = bemerkungen

    def get_calibration_number(self):
        return self.generate_calibration_number()

    @staticmethod
    def _resolve_bild_pfad(dateiname):
        """Loest einen Bilddateinamen zum vollstaendigen Pfad auf.
        Sucht zuerst in data/, dann im Arbeitsverzeichnis."""
        if not dateiname:
            return dateiname
        # Wenn bereits absoluter Pfad, direkt verwenden
        if os.path.isabs(dateiname) and os.path.exists(dateiname):
            return dateiname
        # Zuerst in data/ suchen
        data_pfad = os.path.join(os.getcwd(), 'data', dateiname)
        if os.path.exists(data_pfad):
            return data_pfad
        # Fallback: Arbeitsverzeichnis
        return dateiname

    @staticmethod
    def _verarbeite_bild(bild_pfad, breite=None, hoehe=None):
        """Oeffnet ein Bild, konvertiert zu RGBA, skaliert proportional und gibt Base64 zurueck.
        Entweder breite oder hoehe angeben — das andere wird proportional berechnet."""
        with Image.open(bild_pfad) as bild:
            if bild.mode == 'P':
                bild = bild.convert('RGBA')
            if breite:
                faktor = breite / float(bild.size[0])
                neue_hoehe = int(float(bild.size[1]) * faktor)
                bild = bild.resize((breite, neue_hoehe), Image.LANCZOS)
            elif hoehe:
                faktor = hoehe / float(bild.size[1])
                neue_breite = int(float(bild.size[0]) * faktor)
                bild = bild.resize((neue_breite, hoehe), Image.LANCZOS)
            puffer = io.BytesIO()
            bild.save(puffer, format="PNG", optimize=True, quality=95)
            return base64.b64encode(puffer.getvalue()).decode('utf-8')

    def _build_kunde_string(self):
        """Baut den Kunden-String mit optionalen Zusatzzeilen."""
        Kunde = self.data_to_append.get('waage_data', {}).get('Kunde_name1', '')

        if self.data_to_append.get('waage_data', {}).get('Kunde_name2', '') != "":
            Kunde = self.data_to_append.get('waage_data', {}).get('Kunde_name1', '') + "<br>" + self.data_to_append.get(
                'waage_data', {}).get('Kunde_name2', '')
        elif self.data_to_append.get('waage_data', {}).get('Kunde_name3', '') != "":
            Kunde = self.data_to_append.get('waage_data', {}).get('Kunde_name1', '') + "<br>" + self.data_to_append.get(
                'waage_data', {}).get('Kunde_name2', '') + "<br>" + self.data_to_append.get('waage_data', {}).get(
                'Kunde_name3', )

        return Kunde

    def _get_template_path(self, template_name):
        """Gibt den Pfad zur Template-Datei zurueck (kompatibel mit PyInstaller --onefile)."""
        # PyInstaller entpackt Dateien in ein temporaeres Verzeichnis (_MEIPASS)
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, 'templates', template_name)

    def _load_template(self, template_name):
        """Laedt ein HTML-Template aus dem templates-Ordner."""
        template_path = self._get_template_path(template_name)
        with open(template_path, 'r', encoding='utf-8') as f:
            return Template(f.read())

    def _render_pdf(self, html_content, filename):
        """Rendert HTML zu PDF mit xhtml2pdf."""
        from xhtml2pdf import pisa
        result_file = open(filename, "w+b")
        pisa_status = pisa.CreatePDF(html_content, dest=result_file)
        result_file.close()

        if pisa_status.err:
            return False
        return True
