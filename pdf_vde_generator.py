from pdf_base_generator import PDFGeneratorBase
from datetime import datetime


class PDFGeneratorVDE(PDFGeneratorBase):

    def add_vde_pruefung(self, schutzklasse, rpe, riso, ipe, ib, vde_messgeraet,
                         nennspannung, nennstrom, nennleistung, frequenz, cosphi, visuelle_pruefung_daten=None,
                         rpe_bemerkungen=None, riso_bemerkungen=None, ipe_bemerkungen=None, ib_bemerkungen=None,
                         elektrische_pruefung_daten=None, vde_pruefung=None):
        """Fügt die VDE-Prüfdaten, elektrischen Daten und visuellen Prüfdaten als Tabelle hinzu."""
        self.data_to_append['vde_data'] = {
            'schutzklasse': schutzklasse,
            'rpe': rpe,
            'riso': riso,
            'ipe': ipe,
            'ib': ib,
            'vde_messgeraet': vde_messgeraet,
            'nennspannung': nennspannung,
            'nennstrom': nennstrom,
            'nennleistung': nennleistung,
            'frequenz': frequenz,
            'cosphi': cosphi,
            'rpe_bemerkungen': rpe_bemerkungen,
            'riso_bemerkungen': riso_bemerkungen,
            'ipe_bemerkungen': ipe_bemerkungen,
            'ib_bemerkungen': ib_bemerkungen,
            'visuelle_pruefung_daten': visuelle_pruefung_daten,
            'elektrische_pruefung_daten': elektrische_pruefung_daten,
            'vde_pruefung': vde_pruefung
        }

    def add_kundennummer(self, kundennummer):
        self.data_to_append['kundennummer'] = kundennummer

    def generate_calibration_number(self):
        from settings import Settings
        s = Settings("settings.ini")
        kuerzel = s.get_pruefer_kuerzel()
        if not kuerzel:
            pruefer_name = self.data_to_append.get('company_and_inspector_data', {}).get('pruefer_name', '')
            kuerzel = ''.join([name[0].upper() for name in pruefer_name.split() if name])
        current_date = datetime.now().strftime("%m%y")
        waage_id = self.data_to_append.get('waage_data', {}).get('WJ-Nummer', '')
        return f"VDE_{kuerzel}_{current_date}_{waage_id}"

    def generate_pdf(self, filename="vde_report.pdf"):
        calibration_number = self.generate_calibration_number()

        Kunde = self._build_kunde_string()

        # VDE-Prüfung und Prüfungsart als Text
        vde_pruefung = self.data_to_append['vde_data']['vde_pruefung']

        vde_text = ""
        if vde_pruefung['vde_701']:
            vde_text = "VDE 701 "
            if vde_pruefung['pruefungsart'] == 0:
                vde_text += "Neugerät"
            elif vde_pruefung['pruefungsart'] == 1:
                vde_text += "Erweiterung"
            elif vde_pruefung['pruefungsart'] == 2:
                vde_text += "Instandsetzung"
        elif vde_pruefung['vde_702']:
            vde_text = "VDE 702 Wiederholungsprüfung"
        else:
            vde_text = "Keine VDE-Prüfung ausgewählt"

        # Umwandlung in römische Zahlen
        def to_roman(num):
            roman_numerals = {1: 'I', 2: 'II', 3: 'III'}
            return roman_numerals.get(num, str(num))

        # Schutzklasse in römische Zahlen umwandeln
        schutzklasse = self.data_to_append['vde_data']['schutzklasse']
        schutzklasse_roman = to_roman(int(schutzklasse))

        # Symbole für Häkchen und Kreuz
        haken = "&#x2714;"  # Unicode für ein dickeres Häkchen
        kreuz = "&#x2718;"  # Unicode für ein dickeres Kreuz

        # Visuelle Prüfungsdaten in Variablen packen
        visuelle_pruefung_daten = self.data_to_append['vde_data']['visuelle_pruefung_daten']

        typenschild = haken if visuelle_pruefung_daten.get("Typenschild/Warnhinweis/Kennzeichnungen",
                                                           0) == 1 else kreuz
        gehaeuse = haken if visuelle_pruefung_daten.get("Gehäuse/Schutzabdeckungen", 0) == 1 else kreuz
        anschlussleitung = haken if visuelle_pruefung_daten.get(
            "Anschlussleitung/stecker,Anschlussklemmen und -adern", 0) == 1 else kreuz
        biegeschutz = haken if visuelle_pruefung_daten.get("Biegeschutz/Zugentlastung", 0) == 1 else kreuz
        leitungshalterungen = haken if visuelle_pruefung_daten.get("Leitungshalterungen, Sicherungshalter, usw.",
                                                                   0) == 1 else kreuz
        kuehlluft = haken if visuelle_pruefung_daten.get("Kühlluftöffnungen/Luftfilter", 0) == 1 else kreuz
        schalter = haken if visuelle_pruefung_daten.get("Schalter, Steuer, Einstell- und Sicherheitsvorrichtungen",
                                                        0) == 1 else kreuz
        bemessung = haken if visuelle_pruefung_daten.get("Bemessung der zugänglichen Gerätesicherung",
                                                         0) == 1 else kreuz
        bauteile = haken if visuelle_pruefung_daten.get("Beuteile und Baugruppen", 0) == 1 else kreuz
        ueberlastung = haken if visuelle_pruefung_daten.get("Anzeichen von Überlastung/unsachgemäßem Gebrauch",
                                                            0) == 1 else kreuz
        verschmutzung_vis = haken if visuelle_pruefung_daten.get(
            "Sicherheitsbeeinträchtigende Verschmutzung/Korrission/Alterung", 0) == 1 else kreuz
        mechanische_gefaehrdung = haken if visuelle_pruefung_daten.get("Mechanische Gefährdung", 0) == 1 else kreuz
        unzulaessige_eingriffe = haken if visuelle_pruefung_daten.get("Unzulässige Eingriffe und Änderungen",
                                                                          0) == 1 else kreuz

        # Hilfsfunktion fuer CSS-Klasse basierend auf Symbol
        def css_class(symbol):
            return 'haken' if symbol == haken else 'kreuz'

        # Erstellung der Grenzwerte basierend auf der Schutzklasse
        grenzwerte = {
            '1': {'rpe': "< 0.3 Ohm", 'riso': "> 1 MOhm", 'ipe': "< 3.5 mA", 'ib': "-"},
            '2': {'rpe': "-", 'riso': "> 2 MOhm", 'ipe': "-", 'ib': "< 0.5 mA"},
            '3': {'rpe': "-", 'riso': "> 0.25 MOhm", 'ipe': "-", 'ib': "-"}
        }.get(schutzklasse, {})

        # Funktion zum Vergleichen der Messwerte mit Grenzwerten
        def check_value(key, value):
            if grenzwerte.get(key) == '-' or value == '-':
                return '-'
            grenz = float(grenzwerte[key].split()[1])
            val = float(value)
            if key in ['rpe', 'ipe', 'ib']:
                return haken if val <= grenz else kreuz
            else:  # für 'riso'
                return haken if val >= grenz else kreuz

        # Erstellung der neuen Variablen für Messgrößen und Prüfergebnis
        messgroessen = {}
        pruefergebnis = {}
        for key, unit in [('rpe', 'Ohm'), ('riso', 'MOhm'), ('ipe', 'mA'), ('ib', 'mA')]:
            value = self.data_to_append['vde_data'].get(key, '-')
            if value != '-':
                prefix = '< ' if key in ['rpe', 'ipe', 'ib'] else '> '
                messgroessen[key] = f"{prefix}{value} {unit}"
                pruefergebnis[key] = check_value(key, value)
            else:
                messgroessen[key] = '-'
                pruefergebnis[key] = '-'

            # Funktion des Gerätes i.O. Checkbox-Status abrufen
            funktion_io = self.data_to_append['vde_data']['elektrische_pruefung_daten'].get('funktion_check_var', 0)
            funktion_io_symbol = haken if funktion_io == 1 else kreuz

        # Überprüfung der visuellen Prüfung
        visuelle_pruefung_bestanden = all(
            val == 1 for val in self.data_to_append['vde_data']['visuelle_pruefung_daten'].values())

        # Überprüfung, ob alle Tests bestanden wurden
        alle_tests_bestanden = (
                all(ergebnis == haken for ergebnis in pruefergebnis.values() if ergebnis != '-') and
                funktion_io_symbol == haken and
                visuelle_pruefung_bestanden
        )
        gesamtergebnis_symbol = haken if alle_tests_bestanden else kreuz

        # CSS-Klassen fuer Pruefergebnisse
        def pruefergebnis_class(ergebnis):
            if ergebnis == '-':
                return ''
            return 'haken' if ergebnis == haken else 'kreuz'

        # Template-Kontext erstellen
        context = {
            'firma': self.data_to_append.get('company_and_inspector_data', {}).get('firma', ''),
            'logo_str': self.data_to_append.get('company_and_inspector_data', {}).get('logo_str', ''),
            'strasse': self.data_to_append.get('company_and_inspector_data', {}).get('strasse', ''),
            'plz': self.data_to_append.get('company_and_inspector_data', {}).get('plz', ''),
            'ort': self.data_to_append.get('company_and_inspector_data', {}).get('ort', ''),
            'land': self.data_to_append.get('company_and_inspector_data', {}).get('land', 'Germany'),
            'telefon': self.data_to_append.get('company_and_inspector_data', {}).get('telefon', ''),
            'webseite': self.data_to_append.get('company_and_inspector_data', {}).get('webseite', ''),
            'pruefer_name': self.data_to_append.get('company_and_inspector_data', {}).get('pruefer_name', ''),
            'unterschrift_str': self.data_to_append.get('company_and_inspector_data', {}).get('unterschrift_str', ''),
            'calibration_number': calibration_number,
            'kundennummer': self.data_to_append.get('kundennummer', 'N/A'),
            'kunde': Kunde,
            'kunde_strasse': self.data_to_append.get('waage_data', {}).get('Kunde_Strasse', ''),
            'kunde_plz': self.data_to_append.get('waage_data', {}).get('Kunde_plz', ''),
            'kunde_ort': self.data_to_append.get('waage_data', {}).get('Kunde_ort', ''),
            'vde_text': vde_text,
            'hersteller': self.data_to_append.get('waage_data', {}).get('Hersteller', ''),
            'modell': self.data_to_append.get('waage_data', {}).get('Modell', ''),
            'sn': self.data_to_append.get('waage_data', {}).get('S/N', ''),
            'inventarnummer': self.data_to_append.get('waage_data', {}).get('Inventarnummer', ''),
            'nennspannung': self.data_to_append.get('vde_data', {}).get('nennspannung', ''),
            'nennstrom': self.data_to_append.get('vde_data', {}).get('nennstrom', ''),
            'nennleistung': self.data_to_append.get('vde_data', {}).get('nennleistung', ''),
            'frequenz': self.data_to_append.get('vde_data', {}).get('frequenz', ''),
            'cosphi': self.data_to_append.get('vde_data', {}).get('cosphi', ''),
            'schutzklasse_roman': schutzklasse_roman,
            # Visuelle Pruefung - Symbole und CSS-Klassen
            'typenschild': typenschild,
            'typenschild_class': css_class(typenschild),
            'gehaeuse': gehaeuse,
            'gehaeuse_class': css_class(gehaeuse),
            'anschlussleitung': anschlussleitung,
            'anschlussleitung_class': css_class(anschlussleitung),
            'biegeschutz': biegeschutz,
            'biegeschutz_class': css_class(biegeschutz),
            'leitungshalterungen': leitungshalterungen,
            'leitungshalterungen_class': css_class(leitungshalterungen),
            'kuehlluft': kuehlluft,
            'kuehlluft_class': css_class(kuehlluft),
            'schalter': schalter,
            'schalter_class': css_class(schalter),
            'bemessung': bemessung,
            'bemessung_class': css_class(bemessung),
            'bauteile': bauteile,
            'bauteile_class': css_class(bauteile),
            'ueberlastung': ueberlastung,
            'ueberlastung_class': css_class(ueberlastung),
            'verschmutzung_vis': verschmutzung_vis,
            'verschmutzung_vis_class': css_class(verschmutzung_vis),
            'mechanische_gefaehrdung': mechanische_gefaehrdung,
            'mechanische_gefaehrdung_class': css_class(mechanische_gefaehrdung),
            'unzulaessige_eingriffe': unzulaessige_eingriffe,
            'unzulaessige_eingriffe_class': css_class(unzulaessige_eingriffe),
            # Messungen - Grenzwerte, Messgroessen, Pruefergebnisse
            'grenzwert_rpe': grenzwerte.get('rpe', '-'),
            'grenzwert_riso': grenzwerte.get('riso', '-'),
            'grenzwert_ipe': grenzwerte.get('ipe', '-'),
            'grenzwert_ib': grenzwerte.get('ib', '-'),
            'messgroesse_rpe': messgroessen.get('rpe', '-'),
            'messgroesse_riso': messgroessen.get('riso', '-'),
            'messgroesse_ipe': messgroessen.get('ipe', '-'),
            'messgroesse_ib': messgroessen.get('ib', '-'),
            'pruefergebnis_rpe': pruefergebnis['rpe'],
            'pruefergebnis_rpe_class': pruefergebnis_class(pruefergebnis['rpe']),
            'pruefergebnis_riso': pruefergebnis['riso'],
            'pruefergebnis_riso_class': pruefergebnis_class(pruefergebnis['riso']),
            'pruefergebnis_ipe': pruefergebnis['ipe'],
            'pruefergebnis_ipe_class': pruefergebnis_class(pruefergebnis['ipe']),
            'pruefergebnis_ib': pruefergebnis['ib'],
            'pruefergebnis_ib_class': pruefergebnis_class(pruefergebnis['ib']),
            'rpe_bemerkungen': self.data_to_append.get('vde_data', {}).get('rpe_bemerkungen', ''),
            'riso_bemerkungen': self.data_to_append.get('vde_data', {}).get('riso_bemerkungen', ''),
            'ipe_bemerkungen': self.data_to_append.get('vde_data', {}).get('ipe_bemerkungen', ''),
            'ib_bemerkungen': self.data_to_append.get('vde_data', {}).get('ib_bemerkungen', ''),
            # Funktionspruefung und Gesamtergebnis
            'funktion_io_symbol': funktion_io_symbol,
            'funktion_io_class': css_class(funktion_io_symbol),
            'vde_messgeraet': self.data_to_append.get('vde_data', {}).get('vde_messgeraet', ''),
            'bemerkungen': self.data_to_append.get('bemerkungen', ''),
            'gesamtergebnis_symbol': gesamtergebnis_symbol,
            'gesamtergebnis_class': css_class(gesamtergebnis_symbol),
            'datum_in_einem_jahr': self.data_to_append.get('datum_in_einem_jahr', ''),
            'pruefdatum': self.data_to_append.get('pruefdatum', ''),
        }

        # Template laden und rendern
        template = self._load_template('vde_template.html')
        html_content = template.safe_substitute(context)

        return self._render_pdf(html_content, filename)
