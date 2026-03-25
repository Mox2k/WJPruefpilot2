import base64
import io
import matplotlib.pyplot as plt

from pdf_base_generator import PDFGeneratorBase
from datetime import datetime


class PDFGeneratorTemp(PDFGeneratorBase):

    def add_tempjustage_data(self, temp_data):
        try:
            # Daten extrahieren
            ist_temp1 = float(temp_data['ist_temp1'])
            soll_temp1 = float(temp_data['soll_temp1'])
            ist_temp2 = float(temp_data['ist_temp2'])
            soll_temp2 = float(temp_data['soll_temp2'])
            temp_messgeraet = temp_data['temp_messgeraet']
            umgebung_temp = temp_data['umgebung_temp']

            # Daten für das Diagramm
            labels = ["Prüfpunkt 1", "Prüfpunkt 2"]
            ist_values = [ist_temp1, ist_temp2]
            soll_values = [soll_temp1, soll_temp2]

            # Diagramm erstellen
            plt.figure(figsize=(7, 3), dpi=300)  # Reduzierte Größe und DPI
            plt.box(on=True)
            plt.rcParams['font.family'] = 'Calibri'
            plt.rcParams['font.size'] = 8  # Kleinere Basisschriftgröße

            plt.plot(labels, ist_values, marker='x', linestyle='--', color='red', label='AS-Found-Temperatur',
                     linewidth=1.5)
            plt.plot(labels, soll_values, marker='x', linestyle='--', color='green', label='AS-Left-Temperatur',
                     linewidth=1.5)

            x_offset = 0.05

            for i, value in enumerate(ist_values):
                plt.axhline(y=value, color='red', linestyle='dotted', linewidth=0.8)
                plt.text(-0.2 - x_offset, value, f'{value:.1f} °C', va='center', ha='right', fontsize=10,
                         color='red')

            for i, value in enumerate(soll_values):
                plt.axhline(y=value, color='green', linestyle='dotted', linewidth=0.8)
                plt.text(-0.2 + x_offset, value, f'{value:.1f} °C', va='center', ha='left', fontsize=10,
                         color='green')

            plt.xlim(-0.5 - x_offset, 1.5 + x_offset)
            plt.ylim(min(ist_values + soll_values) - 10, max(ist_values + soll_values) + 10)

            plt.ylabel("Temperatur (°C)", fontsize=8)
            plt.xticks(labels, fontsize=8)
            plt.legend(fontsize=8)
            plt.grid(axis='y', linestyle='--', alpha=0.5)
            plt.tick_params(axis='y', labelsize=8)

            # Diagramm speichern
            chart_buffer = io.BytesIO()
            plt.savefig(chart_buffer, format="png", dpi=300, bbox_inches='tight', pad_inches=0.1)
            chart_buffer.seek(0)
            chart_str = base64.b64encode(chart_buffer.getvalue()).decode("utf-8")

            # Daten speichern
            self.data_to_append['temp_data'] = {
                'ist_temp1': ist_temp1,
                'soll_temp1': soll_temp1,
                'ist_temp2': ist_temp2,
                'soll_temp2': soll_temp2,
                'temp_messgeraet': temp_messgeraet,
                'umgebung_temp': umgebung_temp,
                'chart_str': chart_str
            }
            plt.clf()
            plt.close()

        except (KeyError, ValueError, TypeError) as e:
            print(f"Error in add_tempjustage_data: {e}")

    def generate_calibration_number(self):
        from settings import Settings
        s = Settings("settings.ini")
        kuerzel = s.get_pruefer_kuerzel()
        if not kuerzel:
            pruefer_name = self.data_to_append.get('company_and_inspector_data', {}).get('pruefer_name', '')
            kuerzel = ''.join([name[0].upper() for name in pruefer_name.split() if name])
        current_date = datetime.now().strftime("%m%y")
        waage_id = self.data_to_append.get('waage_data', {}).get('WJ-Nummer', '')
        return f"TK_{kuerzel}_{current_date}_{waage_id}"

    def generate_pdf(self, filename="report.pdf"):
        calibration_number = self.generate_calibration_number()

        Abweichung1 = round(float(self.data_to_append.get('temp_data', {}).get('ist_temp1', '0')) - float(
            self.data_to_append.get('temp_data', {}).get('soll_temp1', '0')), 2)
        Abweichung2 = round(float(self.data_to_append.get('temp_data', {}).get('ist_temp2', '0')) - float(
            self.data_to_append.get('temp_data', {}).get('soll_temp2', '0')), 2)

        if Abweichung1 == 0:
            Abweichung_Text = "Im Zuge der Kalibrierung wurde keine Abweichung in der Heizkennlinie des Feuchtebestimmers festgestellt."
            Abweichung_Text_eng = "During the calibration, no deviation was detected in the heating characteristic of the moisture analyzer."
        else:
            Abweichung_Text = "Im Zuge der Kalibrierung wurde eine Abweichung in der Heizkennlinie des Feuchtebestimmers festgestellt. Diese Abweichung wurde gemäß den spezifischen Vorgaben des Herstellers korrigiert, um die Genauigkeit der Messungen sicherzustellen."
            Abweichung_Text_eng = "During the calibration, a deviation in the heating characteristic of the moisture analyzer was detected. This deviation was corrected according to the manufacturer's specific instructions to ensure the accuracy of the measurements."

        Aufheizzyklus = self.data_to_append.get('waage_data', {}).get('Aufheizzyklus', '')
        if not Aufheizzyklus or Aufheizzyklus == "None":
            Aufheizzyklus = 15

        TempHerstellertoleranz = self.data_to_append.get('waage_data', {}).get('TempHerstellertoleranz', '')
        toleranz_text = "Herstellertoleranz"
        toleranz_text_eng = "Manufacturer's tolerance"
        if not TempHerstellertoleranz or TempHerstellertoleranz == "None":
            TempHerstellertoleranz = 5.0
            toleranz_text = "Toleranz"
            toleranz_text_eng = "Tolerance"

        # Mindestens eine Nachkommastelle
        try:
            TempHerstellertoleranz = float(TempHerstellertoleranz)
            if TempHerstellertoleranz.is_integer():
                TempHerstellertoleranz = format(TempHerstellertoleranz, '.1f')
        except ValueError:
            # Falls der Wert keine gültige Zahl ist, bleibt er unverändert
            pass

        Kunde = self._build_kunde_string()

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
            'stempel_str': self.data_to_append.get('company_and_inspector_data', {}).get('stempel_str', ''),
            'calibration_number': calibration_number,
            'pruefdatum': self.data_to_append.get('pruefdatum', ''),
            'hersteller': self.data_to_append.get('waage_data', {}).get('Hersteller', ''),
            'modell': self.data_to_append.get('waage_data', {}).get('Modell', ''),
            'sn': self.data_to_append.get('waage_data', {}).get('S/N', ''),
            'kunde': Kunde,
            'kunde_strasse': self.data_to_append.get('waage_data', {}).get('Kunde_Strasse', ''),
            'kunde_plz': self.data_to_append.get('waage_data', {}).get('Kunde_plz', ''),
            'kunde_ort': self.data_to_append.get('waage_data', {}).get('Kunde_ort', ''),
            'auftragsnummer': self.data_to_append.get('waage_data', {}).get('Auftragsnummer', ''),
            'umgebung_temp': self.data_to_append.get('temp_data', {}).get('umgebung_temp', ''),
            'standort': self.data_to_append.get('waage_data', {}).get('Standort', ''),
            'raum': self.data_to_append.get('waage_data', {}).get('Raum', ''),
            'unruhe': self.data_to_append.get('waage_data', {}).get('Unruhe', ''),
            'luftbewegung': self.data_to_append.get('waage_data', {}).get('Luftbewegung', ''),
            'verschmutzung': self.data_to_append.get('waage_data', {}).get('Verschmutzung', ''),
            'temp_messgeraet': self.data_to_append.get('temp_data', {}).get('temp_messgeraet', ''),
            'aufheizzyklus': Aufheizzyklus,
            'bemerkungen': self.data_to_append.get('bemerkungen', ''),
            'soll_temp1': self.data_to_append.get('temp_data', {}).get('soll_temp1', ''),
            'ist_temp1': self.data_to_append.get('temp_data', {}).get('ist_temp1', ''),
            'abweichung1': Abweichung1,
            'soll_temp2': self.data_to_append.get('temp_data', {}).get('soll_temp2', ''),
            'ist_temp2': self.data_to_append.get('temp_data', {}).get('ist_temp2', ''),
            'abweichung2': Abweichung2,
            'temp_herstellertoleranz': TempHerstellertoleranz,
            'abweichung_text': Abweichung_Text,
            'abweichung_text_eng': Abweichung_Text_eng,
            'toleranz_text': toleranz_text,
            'toleranz_text_eng': toleranz_text_eng,
            'chart_str': self.data_to_append.get('temp_data', {}).get('chart_str', ''),
        }

        # Template laden und rendern
        template = self._load_template('temp_template.html')
        html_content = template.safe_substitute(context)

        return self._render_pdf(html_content, filename)
