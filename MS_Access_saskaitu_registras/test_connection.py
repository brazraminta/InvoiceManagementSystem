# import pyodbc
#
#
# db_path = r"C:\Users\Raminta\Documents\Programavimas su python 2023-12-18\Invoice Management System\Access\Gaunamų sąskaitų registras.accdb"
#
#
# def get_names_of_suppliers():
#     names_of_suppliers = []
#     try:
#         with pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ=' + db_path) as connection:
#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT DISTINCT tiekejas FROM saskaitos_su_Access_duomenu_baze")
#                 rows = cursor.fetchall()
#                 for row in rows:
#                     print(names_of_suppliers.append(row[0]))
#     except Exception as e:
#         print(f'Error in get_names_of_suppliers: {e}')
#     return names_of_suppliers
#
# suppliers = get_names_of_suppliers()
# suppliers



############################################################
import sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PyQt5.QtWidgets import *
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib import colors
from reportlab.lib.units import mm
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
            self.table_data = []
            for i in range(self.darbu_lentele.rowCount()):
                row_data = []
                for j in range(self.darbu_lentele.columnCount()):
                    item = self.darbu_lentele.item(i, j)
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append("")

                self.table_data.append(row_data) # pridedamas kiekvienas elementas kaip atskiras
            print(self.table_data)

            # patikrinti, ar self.table_data nėra tuščias
            if not self.table_data:
                QMessageBox.Warning(self, 'Klaida', 'Lentelei užpildyti nėra duomenų')
                return

            # patikrinti, ar rowCount ir columnCount yra teisingi
            if len(self.table_data) != self.darbu_lentele.rowCount() or (self.table_data and len(self.table_data[0]) != self.darbu_lentele.columnCount()):
                print("Klaida: eilučių ir stulpelių skaičius nėra teisingas")
                return

            # nurodom failo įrašymo vietą ir pavadinimą
            text, ok = QInputDialog.getText(self, 'Įveskite failo pavadinimą', f'Failo pavadinimas: {self.saskaitos_numeris}')
            if ok:
                filename = f"C:/Users/Raminta/Documents/Programavimas su python 2023-12-18/Invoice Management System/Israsytos saskaitos/{text}.pdf"
                self.create_invoice(filename, self.table_data[0:])
        except Exception as e:
            print(f'Error in create_invoice_clicked: {e}')


def create_invoice(self):
    try:
        # Draw seller information block
        self.draw_seller_block()

        # Draw buyer information block
        self.draw_buyer_block()

        # Draw payment due date
        self.draw_payment_due()

        # Draw table headers
        self.draw_table_headers()

        # Draw table data
        self.draw_table_data()

        # Calculate total table height for subsequent elements positioning
        total_table_height = sum(self.calculate_row_heights())

        # Draw final elements below the table
        self.draw_final_elements(total_table_height)

        # Save the PDF
        self.c.save()
        print("Finished generating the table.")
        QMessageBox.information(self, 'Informacija',
                                'Sąskaita sėkmingai sukurta ir patalpinta išrašytų sąskaitų kataloge')

    except Exception as e:
        print(f'Error in create_invoice method: {e}')


def draw_seller_block(self):
    self.set_font("DejaVuBold", 12)
    self.draw_text(30, 700, "Pardavėjas:")
    self.set_font("DejaVuSans", 10)
    seller_info = [
        'UAB "Pardavėjas"',
        "Įmonės kodas: 112233445",
        "PVM mokėtojo kodas: LT112233445",
        "Adresas: Adreso g. 19, Miestas",
        'Bankas: AB "Bankas"',
        "Atsiskaitomoji sąskaita:",
        'LT11 0000 2222 3333 444'
    ]
    y = 685
    for info in seller_info:
        self.draw_text(30, y, info)
        y -= 15


def draw_buyer_block(self):
    self.set_font("DejaVuBold", 12)
    self.draw_text(340, 700, "Pirkėjas:")
    self.set_font("DejaVuSans", 10)
    buyer_info = [
        self.pirkejas,
        f"Įmonės kodas: {self.imones_kodas}",
        f"PVM mokėtojo kodas: {self.PVM_kodas}",
        f"Adresas: {self.pirkejo_adresas}"
    ]
    y = 685
    for info in buyer_info:
        self.draw_text(340, y, info)
        y -= 15


def draw_payment_due(self):
    self.set_font("DejaVuBold", 12)
    self.draw_text(340, 560, f"Apmokėti iki: {self.apmoketi_iki}")


def draw_table_headers(self):
    start_x = 30
    start_y = 510
    col_widths = [50, 200, 60, 50, 80, 80]
    headers = ['Eil. Nr.', 'Atliktų darbų pavadinimas', 'Mato vnt.', 'Kiekis', 'Vnt. kaina', 'Suma, €']
    self.set_font("DejaVuSans", 10)

    for col, header in enumerate(headers):
        headers_x = start_x + sum(col_widths[:col])
        header_text_width = pdfmetrics.stringWidth(header, 'DejaVuSans', 10)
        header_text_x = headers_x + (col_widths[col] - header_text_width) / 2
        header_text_y = start_y + 15
        self.draw_text(header_text_x, header_text_y, header)


def draw_table_data(self):
    start_x = 30
    start_y = 510
    col_widths = [50, 200, 60, 50, 80, 80]
    row_heights = self.calculate_row_heights()

    for row, row_data in enumerate(self.table_data):
        for col, cell in enumerate(row_data):
            cell_x = start_x + sum(col_widths[:col])
            cell_y = start_y - sum(row_heights[:row])
            text_x = cell_x + 5 if col == 1 else cell_x + (
                        col_widths[col] - pdfmetrics.stringWidth(cell, 'DejaVuSans', 10)) / 2
            text_y = cell_y + row_heights[row] - 15

            if col == 1:
                lines = self.split_text(cell, col_widths[col] - 10)
                for line in lines:
                    self.draw_text(text_x, text_y, line)
                    text_y -= 15
            else:
                self.draw_text(text_x, text_y, cell)
            self.c.rect(cell_x, cell_y, col_widths[col], row_heights[row])


def calculate_row_heights(self):
    row_heights = []
    for row_data in self.table_data:
        row_height = 30
        for col, cell in enumerate(row_data):
            if col == 1:
                lines = self.split_text(cell, 200 - 10)
                row_height = max(row_height, 15 * len(lines))
        row_heights.append(row_height)
    return row_heights


def split_text(self, text, width):
    return simpleSplit(text, 'DejaVuSans', 10, width)


def draw_final_elements(self, total_table_height):
    self.set_font("DejaVuBold", 10)
    self.draw_text(340, 330 - total_table_height, 'Viso suma:')
    self.draw_text(340, 315 - total_table_height, 'PVM 21 %:')
    self.draw_text(340, 300 - total_table_height, 'Viso suma (su PVM):')
    self.draw_text(340, 285 - total_table_height, 'Mokėtina suma, Eur:')

    self.set_font("DejaVuSans", 10)
    texts = [self.suma_viso, self.pvm, self.suma_suPVM, self.moketina_suma]
    y_coords = [330, 315, 300, 285]

    for i, text in enumerate(texts):
        text_width = pdfmetrics.stringWidth(text, 'DejaVuSans', 10)
        x = 540 - text_width
        self.draw_text(x, y_coords[i] - total_table_height, text)

    if self.PVM96_str_checkbox:
        self.set_font("DejaVuSans", 10)
        self.draw_text(30, 200, '* Pagal LR PVM įst. 96 str. taikomas atvirkštinis PVM apmokestinimas')

    self.set_font("DejaVuBold", 10)
    suma = float(self.moketina_suma.replace(',', ''))
    text = self.paversti_skaicius_zodziais(suma)
    self.draw_text(30, 170, text)
    self.c.line(30, 160, 550, 160)

    self.set_font("DejaVuSans", 8)
    self.draw_text(200, 150, 'suma žodžiais')

    self.draw_signatures()


def draw_signatures(self):
    self.set_font("DejaVuBold", 10)
    self.draw_text(30, 100, 'Išrašė:')
    self.set_font("DejaVuSans", 10)
    self.draw_text(30, 80, 'Pardavėjo atstovas Vardenis Pavardenis')
    self.set_font("DejaVuSans", 8)
    pareigos_text = 'pareigos, vardas, pavardė'
    self.draw_text(30, 60, pareigos_text)
    self.c.line(30, 75, 30 + pdfmetrics.stringWidth(pareigos_text, 'DejaVuSans', 8), 75)
    self.draw_text(30, 10, 'parašas')
    self.c.line(30, 20, 80, 20)

    self.set_font("DejaVuBold", 10)
    self.draw_text(340, 100, 'Priėmė:')
    self.set_font("DejaVuSans", 8)
    self.draw_text(340, 60, pareigos_text)
    self.c.line(340, 75, 340 + pdfmetrics.stringWidth(pareigos_text, 'DejaVuSans', 8), 75)
    self.draw_text(340, 10, 'parašas')
    self.c.line(340, 20, 390, 20)


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\///////////////////////////////////////////
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CreationOfInvoice()
    window.show()
    sys.exit(app.exec_())

###################################################################
##################################################################

# Example usage:
c = canvas.Canvas("invoice.pdf", pagesize=A4)
c.setTitle("Invoice")
c.setAuthor("Author")

invoice_generator = InvoiceGenerator(
    c,
    pirkejas="Client Name",
    imones_kodas="123456789",
    PVM_kodas="LT123456789",
    pirkejo_adresas="Client Address",
    apmoketi_iki="2024-07-31",
    table_data=[["1", "Service Description", "unit", "1", "100", "100"]],
    suma_viso="100",
    pvm="21",
    suma_suPVM="121",
    moketina_suma="121",
    PVM96_str_checkbox=True
)
invoice_generator.create_invoice()