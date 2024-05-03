from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from PyQt5.QtWidgets import *
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
from PyQt5.QtCore import QDate, Qt
from num2words import num2words


class CreationOfInvoice(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sąskaitų išrašymo langas")
        self.setGeometry(500, 200, 1250, 770)

        self.vLayout = QVBoxLayout(self)

        self.formLayout = QFormLayout(self)

        self.saskaitos_numeris = QLineEdit()
        self.formLayout.addRow(QLabel('Sąskaitos numeris:'), self.saskaitos_numeris)

        self.projekto_nr = QLineEdit()
        self.formLayout.addRow(QLabel('Projekto numeris:'), self.projekto_nr)

        self.pirkejas = QLineEdit()
        self.formLayout.addRow(QLabel('Pirkėjo pavadinimas'), self.pirkejas)

        self.imones_kodas = QLineEdit()
        self.formLayout.addRow(QLabel('Įmonės kodas:'), self.imones_kodas)

        self.PVM_kodas = QLineEdit()
        self.formLayout.addRow(QLabel('PVM mokėtojo kodas'), self.PVM_kodas)

        self.pirkejo_adresas = QLineEdit()
        self.formLayout.addRow(QLabel('Pirkėjo adresas'), self.pirkejo_adresas)

        # išrašomo dokumento datos nustatymas
        self.dok_data = QDateEdit()
        self.dok_data.setDisplayFormat("yyyy-MM-dd")
        self.dok_data.setCalendarPopup(True)  # įjungia iššokantį kalendoriaus langelį
        self.dok_data.setDate(QDate.currentDate())  # nustatoma esamoji data
        self.dok_data.setFixedWidth(100)  # nustato fiksuotą eilutės plotį
        self.formLayout.addRow(QLabel('Dokumento data:'), self.dok_data)

        # išrašomo dokumento apmokėjimo datos nustatymas
        self.apmoketi_iki = QDateEdit()
        self.apmoketi_iki.setDisplayFormat("yyyy-MM-dd")
        self.apmoketi_iki.setCalendarPopup(True)
        self.apmoketi_iki.setDate(QDate.currentDate())
        self.apmoketi_iki.setFixedWidth(100)
        self.formLayout.addRow(QLabel('Apmokėti iki:'), self.apmoketi_iki)

        self.vLayout.addLayout(self.formLayout)

        # atliktų darbų lentelės laukelių pildymo formų išdėstymas
        self.lent_pildymo_lauk_layout = QGridLayout()  # pildymo laukelių išdėstymas gardelėmis

        # laukeliai duomenų įrašymui
        self.line_edit1 = QLineEdit()
        self.line_edit2 = QLineEdit()
        self.line_edit3 = QLineEdit()
        self.line_edit4 = QLineEdit()
        self.line_edit5 = QLineEdit()

        # laukelių pavadinimų ir laukelių pozicijos gardelėse
        self.lent_pildymo_lauk_layout.addWidget(QLabel('Eil. Nr.:'), 0, 0)
        self.lent_pildymo_lauk_layout.addWidget(self.line_edit1, 1, 0)
        self.lent_pildymo_lauk_layout.addWidget(QLabel('Atliktų darbų pavadinimas'), 0, 1)
        self.lent_pildymo_lauk_layout.addWidget(self.line_edit2, 1, 1)
        self.lent_pildymo_lauk_layout.addWidget(QLabel('Mato vnt.'), 0, 2)
        self.lent_pildymo_lauk_layout.addWidget(self.line_edit3, 1, 2)
        self.lent_pildymo_lauk_layout.addWidget(QLabel('Kiekis'), 0, 3)
        self.lent_pildymo_lauk_layout.addWidget(self.line_edit4, 1, 3)
        self.lent_pildymo_lauk_layout.addWidget(QLabel('Vnt. kaina'), 0, 4)
        self.lent_pildymo_lauk_layout.addWidget(self.line_edit5, 1, 4)
        self.vLayout.addLayout(self.lent_pildymo_lauk_layout)  # gardelių išdėstymo pridėjimas prie pagrindinio išdėstymo

        # lentelės kontūrų sukūrimas
        self.sukurti_lentele()

        # atskiras išdėstymas PVM 96 str. eilutei po lentele
        self.PVM_hLayout = QHBoxLayout()

        # pridedam žymimąjį langelį PVM įstatymo 96 straipsnio eilutei rodyti arba ne
        self.PVM96_str_label = QLabel('Taikomas PVM įstatymo 96 str.')
        self.PVM96_str_label.setStyleSheet("QLabel{font-size: 10pt;}")
        self.PVM_hLayout.addWidget(self.PVM96_str_label)

        self.PVM96_str_checkbox = QCheckBox()
        self.PVM96_str_checkbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.PVM96_str_checkbox.stateChanged.connect(self.update_moketina_suma)  # susiejame checkbox su mokėtinos sumos pasikeitimu po lentele
        self.PVM_hLayout.addWidget(self.PVM96_str_checkbox)

        self.PVM_hLayout.addStretch(100)  # pastumia checkbox langelį arčiau QLabel pavadinimo

        self.PVM_hLayout.addStretch(10)

        # atskiras išdėstymas sumų eilutėms po lentele
        self.sumu_fLayout = QFormLayout()

        # kiekvienos sumos QLabel ir QLineEdit
        self.suma_viso_label = QLabel('Suma viso: ')
        self.suma_viso_line_edit = QLineEdit()
        self.suma_viso_line_edit.setReadOnly(True)  # nustatome, kad šis laukelis būtų tik skaitymui
        self.sumu_fLayout.addRow(self.suma_viso_label, self.suma_viso_line_edit)

        self.pvm_label = QLabel('PVM 21 %:')
        self.pvm_line_edit = QLineEdit()
        self.pvm_line_edit.setReadOnly(True)
        self.sumu_fLayout.addRow(self.pvm_label, self.pvm_line_edit)

        self.suma_suPVM = QLabel('Viso suma (su PVM):')
        self.suma_suPVM_line_edit = QLineEdit()
        self.suma_suPVM_line_edit.setReadOnly (True)
        self.sumu_fLayout.addRow(self.suma_suPVM, self.suma_suPVM_line_edit)

        self.moketina_suma = QLabel('Mokėtina suma, Eur')
        self.moketina_suma_line_edit = QLineEdit()
        self.moketina_suma_line_edit.setReadOnly(True)
        self.sumu_fLayout.addRow(self.moketina_suma, self.moketina_suma_line_edit)
        # sumų eilučių pridėjimas prie PVM eilutės išdėstymo ir pastarosios pridėjimas prie pagrindinio išdėstymo
        self.PVM_hLayout.addLayout(self.sumu_fLayout)
        self.vLayout.addLayout(self.PVM_hLayout)

        # sąskaitos sukūrimo mygtukas
        self.create_invoice_button = QPushButton('Sukurti sąskaitą')
        self.create_invoice_button.clicked.connect(self.create_invoice_clicked)
        self.vLayout.addWidget(self.create_invoice_button)

        self.setLayout(self.vLayout)

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\   METODAI   //////////////////////////////////////////////////

    def sukurti_lentele(self):
        try:
            self.darbu_lentele = QTableWidget(self)
            self.darbu_lentele.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.darbu_lentele.setRowCount(0)  # nustatome norimą eilučių skaičių
            self.darbu_lentele.setColumnCount(6)  # nustatome norimą stulpelių skaičių
            self.darbu_lentele.setHorizontalHeaderLabels(["Eil. Nr.", "Atliktų darbų pavadinimas", "Mato vnt.", "Kiekis", "Vnt. kaina",
                 "Suma, €"])  # stulpelių antraštės
            self.darbu_lentele.resizeColumnsToContents()

            self.darbu_lentele.cellChanged.connect(self.suskaiciuoti_suma)  # suskaičiuoja paskutinio stulpelio reikšmę pagal 3 ir 4 stulpelių reikšmių sandaugą
            self.darbu_lentele.itemChanged.connect(self.atnaujinti_sumas)  # jeigu pasikeičia duomenys lentelėje, sumų eilutėse pasikeičia sumos

            # mygtukas  lentelės atnaujinimui
            fill_table_button = QPushButton('Atnaujinti lentelę', self)
            fill_table_button.clicked.connect(self.atnaujinti_lentele)

            self.vLayout.addWidget(self.darbu_lentele)
            self.vLayout.addWidget(fill_table_button)

        except Exception as e:
            print(f'Error in sukurti_lentele: {e}')

    def atnaujinti_lentele(self):
        try:
            # paimamas tekstas iš QLineEdit laukelių
            eil_nr = self.line_edit1.text()
            darbu_pavadinimas = self.line_edit2.text()
            mato_vnt = self.line_edit3.text()
            kiekis = self.line_edit4.text()
            vnt_kaina = self.line_edit5.text()

            # sukuriama nauja lentelės eilutė su gautu tekstu
            row = [eil_nr, darbu_pavadinimas, mato_vnt, kiekis, vnt_kaina]

            # eilutė pridedama prie lentelės
            self.darbu_lentele.insertRow(self.darbu_lentele.rowCount())
            for i, text in enumerate(row):
                self.darbu_lentele.setItem(self.darbu_lentele.rowCount() - 1, i, QTableWidgetItem(text))

            # Išvalomi QLineEdit laukeliai, kad eitų vesti kitus duomenis
            self.line_edit1.clear()
            self.line_edit2.clear()
            self.line_edit3.clear()
            self.line_edit4.clear()
            self.line_edit5.clear()

        except Exception as e:
            print(f"Error in 'atnaujinti_lentele': {e}")

    def suskaiciuoti_suma(self, row, column):
        try:
            # patikriname, ar pasikeitė trečio ar ketvirto stulpelio elementas
            if column == 3 or column == 4:
                # gauname 4 ir 5 stulpelio reikšmes
                item1 = self.darbu_lentele.item(row, 3)
                item2 = self.darbu_lentele.item(row, 4)
                value1 = 0
                value2 = 0
                if item1 is not None and item1.text() != '':
                    value1 = int(item1.text())
                if item2 is not None and item2.text() != '':
                    value2 = float(item2.text())

                # apskaičiuojam sandaugą
                suma = value1 * value2

                # sukuriam naują QTableWidgetItem su sandauga
                suma_item = QTableWidgetItem("{:.2f}".format(suma))

                # atjungiam cellChanged signalą
                self.darbu_lentele.cellChanged.disconnect()

                # įrašom sandaugą į šeštą stulpelį
                self.darbu_lentele.setItem(row, 5, suma_item)

                # vėl prijungiame cellChanged signalą
                self.darbu_lentele.cellChanged.connect(self.suskaiciuoti_suma)
        except Exception as e:
            print(f"Error in suskaiciuoti_suma: {e}")

    def atnaujinti_sumas(self, item):
        try:
            # pasirenkamas norimas stuleplis (sumos)
            if item.column() == 5:
                suma = 0  # pradinė reikšmė

                # patikrinami visos lentelės paskutiniai stulpeliai su sumomis, kurios sudedamos ir išvedama bendra suma
                for i in range(self.darbu_lentele.rowCount()):
                    item = self.darbu_lentele.item(i, 5)
                    if item is not None and item.text() != '':
                        suma += float(item.text())
                self.suma_viso_line_edit.setText("{:,.2f}".format(suma))  # įrašoma nauja suma su dviem skaičiais po kablelio

                # apskaičiuojamas pvm ir pridedamas į atitinkamą eilutę
                pvm = (suma * (21/100))
                self.pvm_line_edit.setText("{:,.2f}".format(pvm))

                # paskaičiuojama visa suma su PVM
                suma_suPVM = (suma + pvm)
                self.suma_suPVM_line_edit.setText("{:,.2f}".format(suma_suPVM))

                #paskaičiuojama mokėtina suma atsižvelgiant, ar yra taikomas PVM 96 str. (ar pažymėtas checkbox)
                if self.PVM96_str_checkbox.isChecked():
                    suma_viso_text = self.suma_viso_line_edit.text()
                    suma_viso_text = suma_viso_text.replace(',', '')  # pašalinami kableliai, kad atpažintų tekstą
                    self.moketina_suma_line_edit.setText("{:,.2f}".format(float(suma_viso_text)))
                else:
                    suma_suPVM_text = self.suma_suPVM_line_edit.text()
                    suma_suPVM_text = suma_suPVM_text.replace(',', '')
                    self.moketina_suma_line_edit.setText("{:,.2f}".format(float(suma_suPVM_text)))

        except Exception as e:
            print(f"Error in atnaujinti_sumas: {e}")

    def update_moketina_suma(self, state):
        try:
            if state == Qt.Checked:  # jeigu checkbox pažymėtas
                suma_viso_text = self.suma_viso_line_edit.text().replace(',', '')  # pašalinam kablelius, kad atpažintų tekstą
                if suma_viso_text != '':
                    if '.' in suma_viso_text and len(suma_viso_text.split('.')[1]) == 1:  # patikrinama, kiek po kablelio yra skaičių
                        suma_viso_text += '0'  # jeigu tik vienas sksaičius po kablelio, pridedamas nulis, kad būtų du skaičiai po kablelio
                    self.moketina_suma_line_edit.setText("{:,.2f}".format(float(suma_viso_text)))  # įrašoma atitinkama suma
            else:
                suma_suPVM_text = self.suma_suPVM_line_edit.text().replace(',', '')
                if suma_suPVM_text != '':
                    if '.' in suma_suPVM_text and len(suma_suPVM_text.split('.')[1]) == 1:
                        suma_suPVM_text += '0'
                    self.moketina_suma_line_edit.setText("{:,.2f}".format(float(suma_suPVM_text)))

        except Exception as e:
            print(f"Error in update_moketina_suma: {e}")

    def paversti_skaicius_zodziais(selfself, skaicius):
        # skaičius padalinamas į dvi dalis per kablelį
        sveika_dalis, dalis_po_kablelio = str(skaicius).split('.')

        # patikrinama, ar po kablelio yra du skaitmenys, jei ne, pridedamas antras skaičius - 0
        if len(dalis_po_kablelio) == 1:
            dalis_po_kablelio += '0'

        # konvertuojame sveikąją dalį (iki kablelio) į žodžius
        sveika_dalis_zodziais = num2words(int(sveika_dalis), lang='lt')

        return sveika_dalis_zodziais + ' eurai (-ų) ' + dalis_po_kablelio + ' ct'

    def create_invoice_clicked(self):
        try:
            # surinkti duomenis iš formos
            self.saskaitos_numeris = self.saskaitos_numeris.text()
            self.pirkejas = self.pirkejas.text()
            self.imones_kodas = self.imones_kodas.text()
            self.PVM_kodas = self.PVM_kodas.text()
            self.pirkejo_adresas = self.pirkejo_adresas.text()
            self.dok_data = self.dok_data.date().toString('yyyy-MM-dd')
            self.apmoketi_iki = self.apmoketi_iki.date().toString('yyyy-MM-dd')

            # surinkti duomenis iš lentelės
            table_data = []
            for i in range(self.darbu_lentele.rowCount()):
                row_data = []
                for j in range(self.darbu_lentele.columnCount()):
                    item = self.darbu_lentele.item(i, j)
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append("")

                table_data.append(row_data) # pridedamas kiekvienas elementas kaip atskiras
            print(table_data)

            # patikrinti, ar table_data nėra tuščias
            if not table_data:
                QMessageBox.Warning(self, 'Klaida', 'Lentelei užpildyti nėra duomenų')
                return

            # patikrinti, ar rowCount ir columnCount yra teisingi
            if len(table_data) != self.darbu_lentele.rowCount() or (table_data and len(table_data[0]) != self.darbu_lentele.columnCount()):
                print("Error: rowCount or columnCount is incorrect")
                return

            # nurodom failo įrašymo vietą ir pavadinimą
            text, ok = QInputDialog.getText(self, 'Įveskite failo pavadinimą', 'Failo pavadinimas: ')
            if ok:
                filename = f"C:/Users/Raminta/Documents/Programavimas su python 2023-12-18/Invoice Management System/Israsytos saskaitos/{text}.pdf"
                self.create_invoice(filename, table_data[1:])
        except Exception as e:
            print(f'Error in create_invoice_clicked: {e}')

    def create_invoice(self, filename, table_data):
        try:
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4

            # užregistruojam lietuviškas raides palaikantį šriftą
            pdfmetrics.registerFont(TTFont('DejaVuSans', "C:/Users/Raminta/Downloads/dejavu-sans/DejaVuSans.ttf"))
            pdfmetrics.registerFont(TTFont('DejaVuBold', "C:/Users/Raminta/Downloads/dejavu-sans/DejaVuSans-Bold.ttf"))

            # Add some custom text for header
            c.setFont("DejaVuBold", 24)
            c.drawString(150, 780, "PVM SĄSKAITA FAKTŪRA")  # x - pirmojo simbolio koordinatė

            # sąskaitos numerio eilutė
            c.setFont("DejaVuSans", 14)
            c.drawString(230, 755, f"Serija IND Nr. {self.saskaitos_numeris}")

            # sąskaitos išrašymo data
            c.setFont("DejaVuBold", 12)
            c.drawString(260, 740, f"{self.dok_data}")

            # pardavėjo duomenų blokas
            c.setFont("DejaVuBold", 12)
            c.drawString(30, 700, "Pardavėjas:")
            c.setFont("DejaVuSans", 10)
            c.drawString(30, 685, 'UAB "Indasta"')
            c.drawString(30, 670, "Įmonės kodas: 302716777")
            c.drawString(30, 655, "PVM mokėtojo kodas: LT100006623911")
            c.drawString(30, 640, "Adresas: S.Daukanto g. 19, Kazlų Rūda")
            c.drawString(30, 625, 'Bankas: AB "Swedbank"')
            c.drawString(30, 610, "Atsiskaitomoji sąskaita: ")
            c.drawString(30, 595, 'LT47 7300 0101 3385 164')

            # kliento duomenų blokas
            c.setFont("DejaVuBold", 12)
            c.drawString(340, 700, "Pirkėjas:")
            c.setFont("DejaVuSans", 10)
            c.drawString(340, 685, f'{self.pirkejas}')
            c.drawString(340, 670, f"Įmonės kodas: {self.imones_kodas}")
            c.drawString(340, 655, f"PVM mokėtojo kodas: {self.PVM_kodas}")
            c.drawString(340, 640, f"Adresas: {self.pirkejo_adresas}")

            # apmokėti iki
            c.setFont("DejaVuBold", 12)
            c.drawString(340, 560, f"Apmokėti iki: {self.apmoketi_iki}")

            # paslaugų / prekių lentelė
            col_widths = [50, 200, 60, 50, 80, 80]
            row_heights = [30] * len(table_data)

            start_x = 30
            start_y = 545

            c.setFont("DejaVuSans", 10)
            # uždedame stulpelių antraštes
            headers = ['Eil. Nr.', 'Atliktų darbų pavadinimas', 'Mato vnt.', 'Kiekis', 'Vnt. kaina', 'Suma, €']

            # nubraižom antraščių eilutę
            for col, header in enumerate(headers):
                x = start_x + sum(col_widths[:col])
                y = start_y

            # antraščių centravimas
            text_width = pdfmetrics.stringWidth(header, 'DejaVuSans', 10)
            text_x = x + (col_widths[col] - text_width) / 2
            text_y = y + row_heights[0] - 15

            # antraščių nubraižymas
            c.drawString(text_x, text_y, header)
            c.rect(x, y, col_widths[col], row_heights[0], stroke=1, fill=0)

            # Apskaičiuojame kiekvienos eilutės aukštį
            row_heights = []
            for row_data in table_data:
                row_height = 30  # pradinis eilutės aukštis
                for col, cell in enumerate(row_data):
                    if col == 1:  # darbų aprašymo stulpelis
                        lines = simpleSplit(cell, 'DejaVuSans', 10, col_widths[col] - 10)
                        row_height = max(row_height, 15 * len(lines))
                row_heights.append(row_height)

            # nubraižome lentelę
            for row, row_data in enumerate(table_data, start=1): # pradedame nuo 1, nes antraštės jau yra nubraižytos
                for col, cell in enumerate(row_data):
                    # paskaičiuoja celės pradžios tašką
                    x = start_x + sum(col_widths[:col])
                    y = start_y - sum(row_heights[:row]) if row < len(row_heights) else start_y

                    # paskaičiuoja teksto plotį
                    text_width = pdfmetrics.stringWidth(cell, 'DejaVuSans', 10)

                    # paskaičiuoja pradinį teksto tašką
                    if col == 0 or col >= 2:  # centruos pirmą stulpelį ir nuo trečio stulpelio imtinai
                        text_x = x + (col_widths[col] - text_width) / 2
                    else:
                        text_x = x + 5  # Add a small padding for non-centered columns
                    text_y = y + row_heights[row] - 15

                    # darbų aprašymo stulpelio talpinimas celėje
                    if col == 1:
                        lines = simpleSplit(cell, 'DejaVuSans', 10, col_widths[col] - 10)

                        # eilutės aukštis apskaičiuojamas pagal teksto eilučių skaičių
                        row_heights[row] = max(row_heights[row], 15 * len(lines))
                        for line in lines:
                            c.drawString(text_x, text_y, line)
                            text_y -= 15  # move to the next line
                    else:
                        c.drawString(text_x, text_y, cell)

                    # braižo celių kraštus-linijas
                    c.rect(x, y, col_widths[col], row_heights[row], stroke=1, fill=0)

            # paskaičiuojamas bendras lentelės aukštis
            total_table_height = sum(row_heights)

            # tekstas po lentele
            c.setFont("DejaVuBold", 10)
            c.drawString(340, 330, 'Viso suma:')
            c.drawString(340, 315, 'PVM 21 %:')
            c.drawString(340, 300, 'Viso suma (su PVM):')
            c.drawString(340, 285, 'Mokėtina suma, Eur:')

            # teksto po lentele reikšmės
            c.setFont("DejaVuSans", 10)
            texts = [self.suma_viso_line_edit.text(), self.pvm_line_edit.text(), self.suma_suPVM_line_edit.text(), self.moketina_suma_line_edit.text()]
            y_coords = [330 - total_table_height, 315 - total_table_height, 300 - total_table_height, 285 - total_table_height]

            for i, text in enumerate(texts):
                # paskaičiuoja teksto plotį
                text_width = pdfmetrics.stringWidth(text, 'DejaVuSans', 10)

                # apskaičiuoja pradinį teksto tašką
                x = 540 - text_width  # atima teksto plotį iš norimo pabaigos taško

                c.drawString(x, y_coords[i], text)


            # PVM 96 str. eilutė
            if self.PVM96_str_checkbox.isChecked():
                c.setFont("DejaVuSans", 10)
                c.drawString(30, 200, '* Pagal LR PVM įst. 96 str. taikomas atvirkštinis PVM apmokestinimas')

            # mokėtina suma žodžiais
            c.setFont("DejaVuBold", 10)
            suma = float(self.moketina_suma_line_edit.text().replace(',', ''))
            text = self.paversti_skaicius_zodziais(suma)
            c.drawString(30, 170, text)
            text_width = c.stringWidth(text, 'DejaVuBold', 10)
            c.line(30, 170 - 10, 550, 170 - 10)

            c.setFont("DejaVuSans", 8)
            c.drawString(200, 150, 'suma žodžiais')

            # parašai
            c.setFont("DejaVuBold", 10)
            c.drawString(30, 100, 'Išrašė:')
            c.setFont("DejaVuSans", 10)
            c.drawString(30, 80, 'Statybos direktorius Vaidotas Pocius')

            c.setFont("DejaVuSans", 8)
            pareigos_text = 'pareigos, vardas, pavardė'
            pareigos_text_width = c.stringWidth(pareigos_text, 'DejaVuSans', 8)
            c.drawString(30, 60, pareigos_text)
            c.line(30, 60 + 15, 30 + pareigos_text_width, 60 + 15)

            parasas_text = 'parašas'
            # parasas_text_width = c.stringWidth(parasas_text, 'DejaVuSans', 10)
            c.drawString(30, 10, parasas_text)
            line_length = 50
            c.line(30, 10 + 10, 30 + line_length, 10 + 10)

            c.setFont("DejaVuBold", 10)
            c.drawString(340, 100, 'Priėmė:')

            c.setFont("DejaVuSans", 8)
            c.drawString(340, 60, pareigos_text)
            c.line(340, 60 + 15, 340 + pareigos_text_width, 60 + 15)

            c.drawString(340, 10, parasas_text)
            c.line(340, 10 + 10, 340 + line_length, 10 + 10)

            # Finalize the PDF
            c.save()
            QMessageBox.information(self, 'Informacija', 'Sąskaita sėkmingai sukurta ir patalpinta išrašytų sąskaitų kataloge')

        except Exception as e:
            print(f'Error in create_invoice method: {e}')



#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\///////////////////////////////////////////
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CreationOfInvoice()
    window.show()
    sys.exit(app.exec_())
