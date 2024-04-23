import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import datetime
from PyQt5.QtCore import Qt, QSize, QTimer, QTime, QDate
import os
import psycopg2
import subprocess
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QColor


db_params = {
    "host": "localhost",
    "database": "invoiceManagementSystem",  #pakeisti
    "user": "postgres",
    "password": "riko789",
    "port": "5432"
}


class InvoiceDirectoryWatcher:
    def __init__(self, directory):
        self.directory = directory
        self.last_modified = self.get_latest_modification_time()

    def get_latest_modification_time(self):
        try:
            files = os.listdir(self.directory)
            if not files:  # directory is empty
                return None
            latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(self.directory, x)))
            return os.path.getmtime(os.path.join(self.directory, latest_file))

        except Exception as e:
            print(f"Error from get_latest_modification_time: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.invoice_dialog = None

        self.setWindowTitle('Sąskaitų Valdymo Sistema')
        self.setGeometry(20, 50, 1900, 950)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.vLayout = QVBoxLayout(self.central_widget)

        self.hLayout = QHBoxLayout()

        # paieškos filtrų pavadinimas
        self.checkbox_title = QLabel("Filtruoti pagal:")
        self.checkbox_title.setAlignment(Qt.AlignLeft)
        self.checkbox_title.setStyleSheet("QLabel{font-size: 9pt;}")
        self.hLayout.addWidget(self.checkbox_title)

        # sukuriam checkbox'us filtrams
        self.objektas_checkbox = QCheckBox("objektą", self)
        self.tiekejas_checkbox = QCheckBox("tiekėjo pavadinimą", self)
        self.apmokejimo_data_checkbox = QCheckBox('apmokėjimo datą', self)
        self.skubumas_checkbox = QCheckBox('skubumą', self)

        self.hLayout.addWidget(self.objektas_checkbox)
        self.hLayout.addWidget(self.tiekejas_checkbox)
        self.hLayout.addWidget(self.apmokejimo_data_checkbox)
        self.hLayout.addWidget(self.skubumas_checkbox)

        self.vLayout.addLayout(self.hLayout)

        self.vLayout.setSpacing(10)

        self.hLayout2 = QHBoxLayout()
        self.sort_alphabet_label = QLabel("Rikiuoti pagal abėcėlę:")
        self.sort_alphabet_label.setStyleSheet("QLabel{font-size: 9pt;}")
        self.hLayout2.addWidget(self.sort_alphabet_label)

        self.sort_alphabet = QComboBox(self)
        self.sort_alphabet.addItems(["A-Z", "Z-A"])  # pridedam pasirinkimo galimybes
        self.hLayout2.addWidget(self.sort_alphabet)

        self.hLayout2.addSpacing(1500)

        self.vLayout.addLayout(self.hLayout2)

        self.hLayout3 = QHBoxLayout()
        self.sort_order_label = QLabel("Rikiuoti pagal datą:")
        self.sort_order_label.setStyleSheet("QLabel{font-size: 9pt;}")
        self.hLayout3.addWidget(self.sort_order_label)

        self.sort_order = QComboBox(self)
        self.sort_order.addItems(["Didėjančiai", "Mažėjančiai"])
        self.hLayout3.addWidget(self.sort_order)

        self.hLayout3.addSpacing(1500)

        self.vLayout.addLayout(self.hLayout3)

        self.hLayout4 = QHBoxLayout()

        self.suvesti_saskaita_button = QPushButton("Užregistruoti gautą saskaitą")
        self.suvesti_saskaita_button.clicked.connect(self.invoice_registration_form)
        self.hLayout4.addWidget(self.suvesti_saskaita_button)

        self.skenuotos_saskaitos = QPushButton('Tikrinti gaunamų sąskaitų katalogą')
        self.skenuotos_saskaitos.clicked.connect(self.check_for_new_file)
        self.hLayout4.addWidget(self.skenuotos_saskaitos)

        self.saskaitu_registras_button = QPushButton('Peržiūrėti sąskaitų registrą')
        self.saskaitu_registras_button.clicked.connect(self.display_registry_of_invoices)
        self.hLayout4.addWidget(self.saskaitu_registras_button)

        self.koreguoti_irasa_button = QPushButton('Koreguoti įrašą')
        self.koreguoti_irasa_button.clicked.connect(self.update_record)
        self.hLayout4.addWidget(self.koreguoti_irasa_button)

        self.sukurti_saskaita_button = QPushButton('Išrašyti sąskaitą')
        self.sukurti_saskaita_button.clicked.connect(self.create_invoice)
        self.hLayout4.addWidget(self.sukurti_saskaita_button)

        self.vLayout.addLayout(self.hLayout4)

        self.saskaitu_sarasas = QTableWidget()
        self.saskaitu_sarasas.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # nustatome visos eilutės pasirinkimą (ne atskirų stulpelių)
        self.saskaitu_sarasas.setSelectionMode(QAbstractItemView.MultiSelection)  # kelių rezultatų eilučių pasirinkimas
        self.vLayout.addWidget(self.saskaitu_sarasas)

        self.setLayout(self.vLayout)

        self.directory_watcher = InvoiceDirectoryWatcher("C:/Users/Raminta/Documents/Programavimas su python 2023-12-18/Invoice Management System/Saskaitos")
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.check_for_new_file)
        # # self.timer.start(1000 * 60 * 60 * 12)  # tikrinti ryte ir vakare (kas 12 val)
        # self.timer.start(10000)

#/////////////////////////////////////   FUNKCIJOS   /////////////////////////////////////

    def invoice_registration_form(self):
        try:
            self.registrationDialog = QDialog()
            self.registrationDialog.setWindowTitle("Gautų sąskaitų registravimas")
            self.registrationDialog.setFixedSize(1200, 700)

            self.layout = QFormLayout(self)

            self.projektoNr_field = QLineEdit()
            self.layout.addRow(QLabel('Projekto numeris:'), self.projektoNr_field)

            self.tiekejas_field = QLineEdit()
            self.layout.addRow(QLabel('Pardavėjo pavadinimas:'), self.tiekejas_field)

            self.saskaitosNr_field = QLineEdit()
            self.layout.addRow(QLabel('Sąskaitos numeris:'), self.saskaitosNr_field)

            self.saskaitosData_field = QLineEdit()
            self.layout.addRow(QLabel('Sąskaitos data:'), self.saskaitosData_field)

            self.apmoketiIki_field = QLineEdit()
            self.layout.addRow(QLabel('Apmokėti iki:'), self.apmoketiIki_field)

            # apmokėjimo skubumo pasirinkimas
            self.skubumas = QComboBox()
            self.skubumas.addItem("--")
            self.skubumas.addItem("Skubu")
            self.skubumas.addItem("Per 30 dienų")
            self.skubumas.addItem("Neskubu")
            self.layout.addRow(QLabel('Apmokėjimo skubumas:'), self.skubumas)

            self.busena = QComboBox()
            self.busena.addItem("Apmokėta")
            self.busena.addItem("Neapmokėta")
            self.layout.addRow(QLabel('Sąskaitos būsena:'), self.busena)

            self.apmokejimoData_field = QLineEdit()
            self.layout.addRow(QLabel('Sąskaita apmokėta:'), self.apmokejimoData_field)

            self.pastabos_field = QTextEdit()
            self.layout.addRow(QLabel('Pastabos:'), self.pastabos_field)

            self.insert_button = QPushButton("Užregistruoti gautą sąskaitą")
            self.insert_button.clicked.connect(self.register_invoice_received)
            self.layout.addRow(self.insert_button)

            self.registrationDialog.setLayout(self.layout)
            self.registrationDialog.show()

        except Exception as e:
            print(f'Error in register_invoice_received: {e}')

    def register_invoice_received(self): # duomenų įkėlimas į duomenų bazę
        try:
            projekto_numeris = self.projektoNr_field.text()
            tiekejo_pavadinimas = self.tiekejas_field.text()
            saskaitos_nr = self.saskaitosNr_field.text()
            saskaitos_data = self.saskaitosData_field.text()
            apmoketi_iki = self.apmoketiIki_field.text()
            apmokejimo_skubumas = self.skubumas.currentText()
            apmokejimo_busena = self.busena.currentText()

            # laukelis įrašyti datą, kada sąskaita buvo apmokėta
            kada_apmoketa = self.apmokejimoData_field.text()
            if not kada_apmoketa:  # patikrinama, ar datos laukelis tuščias
                kada_apmoketa = None  # jei data neįvedama, duomenų bazės lentelėje bus įrašoma NULL reikšmė

            # pastabų laukelis
            pastabos = self.pastabos_field.toPlainText()
            if not pastabos:  # jeigu pastabos neįrašytos, bus rodoma NULL reikšmė
                pastabos = None

            connection = psycopg2.connect(**db_params)
            cursor = connection.cursor()

            insert_query = """
            INSERT INTO saskaitos (
            projekto_numeris,
            tiekejo_pavadinimas,
            saskaitos_nr,
            saskaitos_data,
            apmoketi_iki,
            apmokejimo_skubumas,
            apmokejimo_busena,
            kada_apmoketa,
            pastabos
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(insert_query, (
                projekto_numeris,
                tiekejo_pavadinimas,
                saskaitos_nr,
                saskaitos_data,
                apmoketi_iki,
                apmokejimo_skubumas,
                apmokejimo_busena,
                kada_apmoketa,
                pastabos
            ))

            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, 'Information', 'Sąskaita sėkmingai įrašyta į duomenų bazę')
            self.registrationDialog.close()  # uždaromas sąskaitos suvedimo langas


        except Exception as e:
            print(f"Error from register_invoice_received: {e}")

    def display_registry_of_invoices(self):
        try:
            with psycopg2.connect(**db_params) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM saskaitos")
                    rows = cursor.fetchall()

                    self.saskaitu_sarasas.setRowCount(len(rows))
                    self.saskaitu_sarasas.setColumnCount(10)

                    # lentelės stulpelių pavadinimai
                    headers = ['Įrašo Nr.', 'Projekto Nr.', 'Tiekėjas', 'Sąskaitos Nr.', 'Sąskaitos data', 'Apmokėti iki', 'Skubumas', 'Apmokėta / Neapmokėta', 'Kada apmokėta', 'Pastabos']
                    self.saskaitu_sarasas.setHorizontalHeaderLabels(headers)
                    self.saskaitu_sarasas.horizontalHeader().setStyleSheet('QHeaderView::section { background-color: lightgrey}')

                    for i, row in enumerate(rows):
                        for j, item in enumerate(row):
                            if item is None:
                                item = ''  # replace None with an empty string

                            if j in [4, 5, 8]:  # 'Sąskaitos data', 'Apmokėti iki', 'Kada apmokėta' column indices
                                if item and isinstance(item, datetime.date):  # check if item is not an empty string and is a date
                                    item = item.strftime('%Y-%m-%d')  # convert date to string
                                table_item = QTableWidgetItem(str(item))
                            elif j == 7 and item == 'Apmokėta':  # 'Apmokėta / Neapmokėta' column index
                                table_item = QTableWidgetItem(str(item))
                                table_item.setBackground(QColor(144, 238, 144))  # light green color
                            elif j == 6 and item == 'Skubu':
                                table_item = QTableWidgetItem(str(item))
                                table_item.setBackground(QColor(255, 0, 0))  # red color
                            else:
                                table_item = QTableWidgetItem(str(item))
                            self.saskaitu_sarasas.setItem(i, j, table_item)
                            self.saskaitu_sarasas.resizeColumnToContents(j)


            self.saskaitu_sarasas.show()

        except Exception as e:
            print(f"Error from check_registry_of_invoices: {e}")

    def update_record(self):
        try:
            # pažymėtos eilutės identifikavimas
            current_row = self.saskaitu_sarasas.currentRow()

            # gaunam duomenis iš lentelės
            record_id = self.saskaitu_sarasas.item(current_row, 0)
            if record_id is not None:
                record_id = record_id.text()
            new_values = []
            for i in range(0, 9):
                item = self.saskaitu_sarasas.item(current_row, i)
                if item is not None:
                    new_values.append(item.text())

            # atnaujinama duomenų bazė
            self.confirm_update(record_id, new_values)

            # atnaujinamas lentelės vaizdas
            self.display_registry_of_invoices()

        except Exception as e:
            print(f"Error from update_record: {e}")

    def confirm_update(self, record_id, new_values):
        try:
            with psycopg2.connect(**db_params) as connection:
                with connection.cursor() as cursor:

                    update_query = """
                    UPDATE saskaitos SET
                    projekto_numeris = %s,
                    tiekejo_pavadinimas = %s,
                    saskaitos_nr = %s,
                    saskaitos_data = %s,
                    apmoketi_iki = %s,
                    apmokejimo_skubumas = %s,
                    apmokejimo_busena = %s,
                    kada_apmoketa = %s,
                    pastabos = %s 
                    WHERE saskaitos_id = %s
                    """

                    cursor.execute(update_query, (*new_values, record_id)) # The * operator in this context is used for unpacking the elements of new_values, which is expected to be an iterable (like a list or a tuple
                    connection.commit()

                    # gaunamas pakoreguotų eilučių skaičius ir parodomas pranešimas
                    count = cursor.rowcount
                    QMessageBox.information(self, "Information", f"Sėkmingai atnaujinta {count} įrašai(-ų)", QMessageBox.Ok)

        except (Exception, psycopg2.Error) as error:
            print(f'Error from confirm_update: {error}')
            QMessageBox.warning(self, "Error", 'Klaida atnaujinant duomenis')


    def check_for_new_file(self):
        try:
            # get the list of all files in the directory
            files = os.listdir(self.directory_watcher.directory)

            # if the directory is not empty
            if files:
                # open the directory
                subprocess.Popen(f'explorer "{os.path.realpath(self.directory_watcher.directory)}"')


        except Exception as e:
            print(f"Error from check_for_new_file: {e}")

    def create_invoice(self):
        from pdf_kurimas import CreationOfInvoice
        invoice = CreationOfInvoice()
        invoice.create_invoice()


# //////////////////////////////////////////

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

#@@@@@@@@@@@@@@@@@@@  APMOKĖJIMO BŪSENA CHECKBOX KLASĖ @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

class ComboBoxItem(QTableWidgetItem):
    def __init__(self, text):
        super().__init__(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ComboBoxItem()
    window.show()
    sys.exit(app.exec_())

#@@@@@@@@@@@@@@@@@@@  SĄSKAITŲ SUVEDIMO KLASĖ @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

class InvoiceDialog(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sąskaitų registravimo langas")
        self.layout = QFormLayout(self)

        self.projektoNr_field = QLineEdit()
        self.layout.addRow(QLabel('Projekto numeris:'), self.projektoNr_field)

        self.tiekejas_field = QLineEdit()
        self.layout.addRow(QLabel('Pardavėjo pavadinimas:'), self.tiekejas_field)

        self.saskaitosNr_field = QLineEdit()
        self.layout.addRow(QLabel('Sąskaitos numeris:'), self.saskaitosNr_field)

        self.saskaitosData_field = QLineEdit()
        self.layout.addRow(QLabel('Sąskaitos data:'), self.saskaitosData_field)

        self.apmoketiIki_field = QLineEdit()
        self.layout.addRow(QLabel('Apmokėti iki:'), self.apmoketiIki_field)

        # apmokėjimo skubumo pasirinkimas
        self.skubumas = QComboBox()
        self.skubumas.addItem("Skubu")
        self.skubumas.addItem("Per 30 dienų")
        self.skubumas.addItem("Neskubu")
        self.layout.addRow(QLabel('Apmokėjimo skubumas:'), self.skubumas)

        # apmokėjimo būsenos pasirinkimas
        self.busena = QCheckBox('Neapmokėta')
        self.busena.stateChanged.connect(self.on_busena_changed)
        self.layout.addRow(QLabel('Sąskaitos būsena:'), self.busena)

        self.apmokejimoData_field = QLineEdit()
        self.layout.addRow(QLabel('Sąskaita apmokėta:'), self.apmokejimoData_field)

        self.pastabos_field = QTextEdit()
        self.layout.addRow(QLabel('Pastabos:'), self.pastabos_field)

        self.insert_button = QPushButton("Užregistruoti gautą sąskaitą")
        self.insert_button.clicked.connect(self.register_invoice_received)
        self.layout.addRow(self.insert_button)

    def register_invoice_received(self):
        try:
            projekto_numeris = self.projektoNr_field.text()
            tiekejo_pavadinimas = self.tiekejas_field.text()
            saskaitos_nr = self.saskaitosNr_field.text()
            saskaitos_data = self.saskaitosData_field.text()
            apmoketi_iki = self.apmoketiIki_field.text()
            apmokejimo_skubumas = self.skubumas.currentText()
            apmokejimo_busena = self.busena.currentText()

            # laukelis įrašyti datą, kada sąskaita buvo apmokėta
            kada_apmoketa = self.apmokejimoData_field.text()
            if not kada_apmoketa:  # patikrinama, ar datos laukelis tuščias
                kada_apmoketa = None  # jei data neįvedama, duomenų bazės lentelėje bus įrašoma NULL reikšmė

            # pastabų laukelis
            pastabos = self.pastabos_field.toPlainText()
            if not pastabos:  # jeigu pastabos neįrašytos, bus rodoma NULL reikšmė
                pastabos = None

            connection = psycopg2.connect(**db_params)
            cursor = connection.cursor()

            insert_query = """
            INSERT INTO saskaitos (
            projekto_numeris,
            tiekejo_pavadinimas,
            saskaitos_nr,
            saskaitos_data,
            apmoketi_iki,
            apmokejimo_skubumas,
            apmokejimo_busena,
            kada_apmoketa,
            pastabos
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(insert_query, (
                projekto_numeris,
                tiekejo_pavadinimas,
                saskaitos_nr,
                saskaitos_data,
                apmoketi_iki,
                apmokejimo_skubumas,
                apmokejimo_busena,
                kada_apmoketa,
                pastabos
            ))

            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, 'Information', 'Sąskaita sėkmingai įrašyta į duomenų bazę')
            self.close()  # uždaromas sąskaitos suvedimo langas

        except Exception as e:
            print(f"Error from register_invoice_received: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InvoiceDialog()
    window.show()
    sys.exit(app.exec_())