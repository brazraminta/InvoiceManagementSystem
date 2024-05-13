import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
import datetime
from datetime import datetime, date
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QStringListModel
import os
import os.path
import psycopg2
import subprocess
from PyQt5.QtGui import QColor, QFont, QPixmap





db_params = {
    "host": "localhost",
    "database": "invoiceManagementSystem",  #pakeisti
    "user": "postgres",
    "password": "riko789",
    "port": "5432"
}

# failų katalogo tikrinimui
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
            print(f"Error in get_latest_modification_time: {e}")


class UpdateRecordWindow(QDialog):

    form_submitted = pyqtSignal(str, str, str, str, str, str, str, str, str, str)
    def __init__(self, record_id, current_data, main_window, parent=None):
        super().__init__(parent)
        self.record_id = record_id
        self.main_window = main_window

        self.setWindowTitle("Įrašo koregavimo langas")
        self.setFixedSize(500, 500)

        self.vLayout = QVBoxLayout()  # pagrindinis išdėstymas
        # pildymo laukelių išdėstymas
        self.fLayout = QFormLayout(self)

        # sukuriami QLineEdit laukeliai kiekvienai reikšmei, kuri gali būti atnaujinta
        self.updated_Projekto_nr = QLineEdit(current_data[1])
        self.updated_Projekto_nr.setFixedSize(150, 30)
        self.updated_Projekto_nr.setStyleSheet("font-size: 10px;")
        self.fLayout.addRow(QLabel('Projekto numeris:'), self.updated_Projekto_nr)

        self.updated_tiekejo_pavadinimas = QLineEdit(current_data[2])
        self.updated_tiekejo_pavadinimas.setFixedSize(150, 30)
        self.updated_tiekejo_pavadinimas.setStyleSheet("font-size: 10px;")
        self.fLayout.addRow(QLabel('Pardavėjo pavadinimas:'), self.updated_tiekejo_pavadinimas)

        self.updated_saskaitos_nr = QLineEdit(current_data[3])
        self.updated_saskaitos_nr.setFixedSize(150, 30)
        self.updated_saskaitos_nr.setStyleSheet("font-size: 10px;")
        self.fLayout.addRow(QLabel('Sąskaitos numeris:'), self.updated_saskaitos_nr)

        self.updated_saskaitos_data = QDateEdit()
        self.updated_saskaitos_data.setDate(QDate.fromString(current_data[4], "yyyy-MM-dd"))
        self.updated_saskaitos_data.setFixedSize(150, 30)
        self.fLayout.addRow(QLabel('Sąskaitos data:'), self.updated_saskaitos_data)

        self.updated_apmoketi_iki = QDateEdit()
        self.updated_apmoketi_iki.setDate(QDate.fromString(current_data[5], "yyyy-MM-dd"))
        self.updated_apmoketi_iki.setFixedSize(150, 30)
        self.fLayout.addRow(QLabel('Apmokėti iki:'), self.updated_apmoketi_iki)

        # self.updated_apmokejimo_skubumas = QLineEdit(current_data[6])
        self.updated_skubumas_combo = QComboBox()
        self.updated_skubumas_combo.setFixedSize(150, 30)
        self.updated_skubumas_combo.setStyleSheet("font-size: 10px;")
        self.updated_skubumas_combo.addItems([' ', 'Skubu', 'Neskubu'])
        self.fLayout.addRow(QLabel('Apmokėjimo skubumas:'), self.updated_skubumas_combo)

        # QCombo laukelis sąskaitos būsenos pakeitimui
        self.apmokejimo_busena_combo = QComboBox()
        self.apmokejimo_busena_combo.setFixedSize(150, 30)
        self.apmokejimo_busena_combo.setStyleSheet("font-size: 10px;")
        self.apmokejimo_busena_combo.addItems(['Apmokėta', 'Neapmokėta'])
        self.fLayout.addRow(QLabel('Apmokėjimo būsena:'), self.apmokejimo_busena_combo)

        # dabartinės apmokėjimo datos laukelis
        hLayout = QHBoxLayout()
        hLayout.addWidget(QLabel('Esama apmokėjimo data:'))

        self.current_apmokejimo_data = QLineEdit(current_data[8])
        self.current_apmokejimo_data.setFixedSize(150, 30)
        hLayout.addWidget(self.current_apmokejimo_data)

        # esamos datos ištrynimas (tuščio laukelio įrašymas į duomenų bazę)
        self.null_date_checkbox = QCheckBox('Ištrinti apmokėjimo datą')
        self.null_date_checkbox.setChecked(False)
        hLayout.addWidget(self.null_date_checkbox)
        hLayout.addStretch()

        self.fLayout.addRow(hLayout)

        # atnaujintos datos laukelis
        hLayout2 = QHBoxLayout()
        hLayout2.addWidget(QLabel('Nauja apmokėjimo data:'))

        self.updated_apmokejimo_data = QDateTimeEdit()
        self.updated_apmokejimo_data.setDisplayFormat("yyyy-MM-dd")
        self.updated_apmokejimo_data.setDate(QDate.currentDate())
        self.updated_apmokejimo_data.setCalendarPopup(True)
        self.updated_apmokejimo_data.setFixedSize(150, 30)
        hLayout2.addWidget(self.updated_apmokejimo_data)

        self.update_date_checkbox = QCheckBox('Atnaujinti datą')
        self.update_date_checkbox.setChecked(True)
        self.update_date_checkbox.stateChanged.connect(self.on_update_date_checkbox_changed)
        hLayout2.addWidget(self.update_date_checkbox)
        hLayout2.addStretch()

        self.fLayout.addRow(hLayout2)

        self.updated_pastabos = QLineEdit(current_data[9])
        self.updated_pastabos.setFixedSize(150, 30)
        self.updated_pastabos.setStyleSheet("font-size: 10px;")
        self.fLayout.addRow(QLabel('Pastabos:'), self.updated_pastabos)

        self.new_sutikrinimas_combo = QComboBox()
        self.new_sutikrinimas_combo.setFixedSize(150, 30)
        self.new_sutikrinimas_combo.addItems(['Patikrinti', 'Sutikrinta'])
        self.new_sutikrinimas_combo.currentTextChanged.connect(self.update_updated_pastabos_field)
        self.fLayout.addRow(QLabel('Patikrinti / Sutikrinta:'), self.new_sutikrinimas_combo)

        # pakeitimų patvirtinimo mygtukas
        self.submit_button = QPushButton("Patvirtinti pakeitimus")
        self.submit_button.clicked.connect(self.submit_form)
        self.fLayout.addWidget(self.submit_button)
        self.vLayout.addLayout(self.fLayout)

        self.setLayout(self.vLayout)
        self.show()

    def update_updated_pastabos_field(self, text):
        current_text = self.updated_pastabos.text()
        if current_text:
            new_text = current_text + "; " + text
        else:
            new_text = text
        self.updated_pastabos.setText(new_text)

    def submit_form(self):
        try:
            # gaunami duomenys iš užpildytų laukelių
            updated_projekto_numeris = self.updated_Projekto_nr.text()
            updated_tiekejo_pavadinimas = self.updated_tiekejo_pavadinimas.text()
            updated_saskaitos_nr = self.updated_saskaitos_nr.text()
            updated_saskaitos_data = self.updated_saskaitos_data.date().toString("yyyy-MM-dd")
            updated_apmoketi_iki = self.updated_apmoketi_iki.date().toString("yyyy-MM-dd")

            # QCombo laukelis apmokėjimo skubumo pakeitimui
            updated_apmokejimo_skubumas_text = self.updated_skubumas_combo.currentText()
            skubumas_index = self.updated_skubumas_combo.findText(updated_apmokejimo_skubumas_text)
            if skubumas_index >= 0:
                self.updated_skubumas_combo.setCurrentIndex(skubumas_index)

            # QCombo laukelis apmokėjimo būsenos pakeitimui
            updated_apmokejimo_busena_text = self.apmokejimo_busena_combo.currentText()
            index = self.apmokejimo_busena_combo.findText(updated_apmokejimo_busena_text)
            if index >= 0:
                self.apmokejimo_busena_combo.setCurrentIndex(index)

            # apmokėjimo datos pakeitimų ar esamų reikšmmių įrašymas į duomenų bazę
            if self.update_date_checkbox.isChecked():
                updated_apmokejimo_data = self.updated_apmokejimo_data.date().toString("yyyy-MM-dd") if not self.updated_apmokejimo_data.text() == '' else ''
            elif self.null_date_checkbox.isChecked():
                updated_apmokejimo_data = ''
            else:
                updated_apmokejimo_data = self.current_apmokejimo_data.text()  # įrašoma esama data

            updated_pastabos = self.updated_pastabos.text()
            if not updated_pastabos:  # jeigu pastabos neįrašytos, bus rodoma NULL reikšmė
                updated_pastabos = None

            self.form_submitted.emit(updated_projekto_numeris, updated_tiekejo_pavadinimas, updated_saskaitos_nr, updated_saskaitos_data,
                                     updated_apmoketi_iki, updated_apmokejimo_skubumas_text, updated_apmokejimo_busena_text, updated_apmokejimo_data, updated_pastabos, self.record_id)

            try:
                self.close()
                self.main_window.display_registry_of_invoices()
            except Exception as exc:
                print(f'Error in submit_form closing QDialog: {exc}')

        except Exception as e:
            print(f'Error in UpdateRecordWindow.submit_form: {e}')

    def on_update_date_checkbox_changed(self, state):
        if state == Qt.Checked:
            self.updated_apmokejimo_data.setDate(QDate.currentDate())
        else:
            self.updated_apmokejimo_data.clear()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@   PAGRINDINIS LANGAS   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.invoice_dialog = None
        self.initUI()

    def initUI(self):

        self.setWindowTitle('Sąskaitų Valdymo Sistema')
        self.setGeometry(20, 50, 1900, 950)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.vLayout = QVBoxLayout(self.central_widget)

        # sąskaitų registro ir filtrų išdėstymas
        self.hLayout = QHBoxLayout()

        # mygtukų pavadinimų ir laukelių šrifto dydis
        font = QFont()
        font.setPointSize(8)

        # vertikalus išdėstymas QLabel (filtrų pavadinimas)
        self.label_vLayout = QVBoxLayout()
        self.label_vLayout.addSpacing(10)

        # paieškos filtrų pavadinimas
        self.filter_title = QLabel("Filtruoti įrašus pagal:")
        self.filter_title.setAlignment(Qt.AlignLeft)
        self.filter_title.setStyleSheet("QLabel{font-size: 10pt;}")
        self.label_vLayout.addWidget(self.filter_title)
        self.label_vLayout.addSpacing(10)

        self.hLayout.addLayout(self.label_vLayout)
        self.hLayout.addStretch(10)

        # sukuriam filtrus su reikšmių įrašymo laukeliais
        self.projektas_label = QLabel("* projektą:", self)
        self.projektas_label.setFont(font)
        self.projektoNr_input = QLineEdit(self)
        self.projektoNr_input.setFixedSize(150, 30)
        self.projektoNr_input.setPlaceholderText("Įveskite projekto numerį")
        self.projektoNr_input.textChanged.connect(self.filter_projects)

        # laukelius pridedam prie išdėstymo
        self.hLayout.addWidget(self.projektas_label)
        self.hLayout.addWidget(self.projektoNr_input)

        # self.filterHLayout2.addStretch(50)

        self.tiekejas_label = QLabel("* tiekėją:", self)
        self.tiekejas_label.setFont(font)
        self.tiekejas_input = QLineEdit(self)
        self.tiekejas_input.setFixedSize(150, 30)
        self.tiekejas_input.setPlaceholderText("Įveskite tiekėjo pavadinimą")
        self.tiekejas_input.textChanged.connect(self.filter_suppliers)

        # sukuriamas QStringListModel metodas, grąžinantis tiekėjų pavadinimus ir projektų numerius
        tiekejai = QStringListModel()
        tiekejai.setStringList(self.get_names_of_suppliers())

        projektai = QStringListModel()
        projektai.setStringList(self.get_project_numbers())

        # sukuriamas QCompleter su tiekėjų ir projektų modeliu (kad siūlytų rašomo pavadinimo ar numerio užbaigimą)
        completer = QCompleter()
        completer.setModel(tiekejai)
        completer.setModel(projektai)
        self.tiekejas_input.setCompleter(completer)
        self.projektoNr_input.setCompleter(completer)

        # laukelius pridedam prie išdėstymo
        self.hLayout.addWidget(self.tiekejas_label)
        self.hLayout.addWidget(self.tiekejas_input)

        self.hLayout.addStretch(20)

        # filtravimas pagal metus
        self.year_filter = QLabel("* metus:", self)
        self.year_filter.setFont(font)
        self.hLayout.addWidget(self.year_filter)

        self.years_combo = QComboBox()
        self.years_combo.setFixedSize(100, 30)
        current_year = datetime.now().year
        self.years_combo.addItems([str(year) for year in range(current_year, 2011, -1)])
        self.years_combo.insertItem(0, "")  # pridedama tuščia reikšmė
        self.years_combo.setCurrentIndex(0)  # nustatoma tuščia reikšmė kaip pasirinkta pagal nutylėjimą
        self.years_combo.currentIndexChanged.connect(self.show_chosen_year)
        self.hLayout.addWidget(self.years_combo)

        # filtravimas pagal ketvirtį
        self.quarter_filter = QLabel('* ketvirtį:', self)
        self.quarter_filter.setFont(font)
        self.hLayout.addWidget(self.quarter_filter)

        self.quarters_combo = QComboBox()
        self.quarters_combo.setFixedSize(100, 30)
        self.quarters_combo.addItems(['I ketv.', 'II ketv.', 'III ketv.', 'IV ketv.'])
        self.quarters_combo.insertItem(0, "")  # pridedama tuščia reikšmė
        self.quarters_combo.setCurrentIndex(0)  # nustatoma tuščia reikšmė kaip pasirinkta pagal nutylėjimą
        self.quarters_combo.currentIndexChanged.connect(self.show_chosen_quarter)
        self.hLayout.addWidget(self.quarters_combo)

        # filtravimas pagal mėnesį
        self.month_filter = QLabel('* mėnesį:', self)
        self.month_filter.setFont(font)
        self.hLayout.addWidget(self.month_filter)

        self.months_combo = QComboBox()
        self.months_combo.setFixedSize(100, 30)
        self.months_combo.addItems(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
        self.months_combo.insertItem(0, "")  # pridedama tuščia reikšmė
        self.months_combo.setCurrentIndex(0)  # nustatoma tuščia reikšmė kaip pasirinkta pagal nutylėjimą
        self.months_combo.currentIndexChanged.connect(self.show_chosen_month)
        self.hLayout.addWidget(self.months_combo)

        self.hLayout.addSpacing(100)

        # pridedam pasirinktų paieškos filtrų išvalymą
        self.filter_cleanup = QPushButton("Išvalyti filtrus", self)
        self.filter_cleanup.setFixedSize(150, 40)
        self.filter_cleanup.clicked.connect(self.clean_up_filters)
        self.hLayout.addWidget(self.filter_cleanup)

        self.hLayout.addSpacing(400)

        self.vLayout.addLayout(self.hLayout)

        # sąskaitų lentelės horizontalus išdėstymas
        self.table_Layout = QHBoxLayout()

        self.saskaitu_sarasas = QTableWidget()
        self.saskaitu_sarasas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.saskaitu_sarasas.resizeColumnsToContents()
        self.saskaitu_sarasas.setSortingEnabled(True)
        self.saskaitu_sarasas.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # nustatome visos eilutės pasirinkimą (ne atskirų stulpelių)
        self.saskaitu_sarasas.setSelectionMode(QAbstractItemView.SingleSelection)  # vienos rezultatų eilutės pasirinkimas, kad kita būtų atžymėta
        self.saskaitu_sarasas.cellClicked.connect(self.on_invoiceNo_clicked)
        self.table_Layout.addWidget(self.saskaitu_sarasas)

        # mygtukų vertikalus išdėstymas lentlės dešiniajame krašte
        self.buttonLayout = QVBoxLayout()

        self.saskaitu_registras_button = QPushButton('Sąskaitų registras')
        self.saskaitu_registras_button.setFont(font)
        self.saskaitu_registras_button.setFixedSize(200, 60)
        self.saskaitu_registras_button.clicked.connect(self.display_registry_of_invoices)
        self.buttonLayout.addWidget(self.saskaitu_registras_button)

        self.suvesti_saskaita_button = QPushButton("Užregistruoti gautą saskaitą")
        self.suvesti_saskaita_button.setFont(font)
        self.suvesti_saskaita_button.setFixedSize(200, 40)
        self.suvesti_saskaita_button.clicked.connect(self.invoice_registration_form)
        self.buttonLayout.addWidget(self.suvesti_saskaita_button)

        self.skenuotos_saskaitos = QPushButton('Sąskaitų katalogas')
        self.skenuotos_saskaitos.setFont(font)
        self.skenuotos_saskaitos.setFixedSize(200, 40)
        self.skenuotos_saskaitos.clicked.connect(self.check_for_new_file)
        self.buttonLayout.addWidget(self.skenuotos_saskaitos)

        self.sukurti_saskaita_button = QPushButton('Išrašyti sąskaitą')
        self.sukurti_saskaita_button.setFont(font)
        self.sukurti_saskaita_button.setFixedSize(200, 40)
        self.sukurti_saskaita_button.clicked.connect(self.create_invoice)
        self.buttonLayout.addWidget(self.sukurti_saskaita_button)

        self.buttonLayout.addSpacing(50)

        # mygtukas sąskaitos apmokėjimo būsenai ir datai pakeisti
        self.apmoketa_button = QPushButton('Patvirtinti apmokėjimą')
        self.apmoketa_button.setFont(font)
        self.apmoketa_button.setFixedSize(200, 50)
        self.apmoketa_button.clicked.connect(self.invoice_payment_confirmation)
        self.buttonLayout.addWidget(self.apmoketa_button)

        self.koreguoti_irasa_button = QPushButton('Koreguoti įrašą')
        self.koreguoti_irasa_button.setFont(font)
        self.koreguoti_irasa_button.setFixedSize(200, 50)
        self.koreguoti_irasa_button.clicked.connect(self.update_record_button_clicked)
        self.buttonLayout.addWidget(self.koreguoti_irasa_button)

        self.istrinti_irasa_button = QPushButton('Ištrinti įrašą')
        self.istrinti_irasa_button.setFont(font)
        self.istrinti_irasa_button.setFixedSize(200, 50)
        self.istrinti_irasa_button.clicked.connect(self.delete_record)
        self.buttonLayout.addWidget(self.istrinti_irasa_button)

        self.buttonLayout.addSpacing(50)

        # tikrinimas, ar yra apmokėtinų sąskaitų einamajai dienai
        self.tikrinti_apmokejima = QPushButton('Ar yra apmokėtinų\nsąskaitų šiai dienai?')
        self.tikrinti_apmokejima.setFont(font)
        self.tikrinti_apmokejima.setFixedSize(200, 70)
        self.tikrinti_apmokejima.clicked.connect(self.check_invoices_due_date)
        self.buttonLayout.addWidget(self.tikrinti_apmokejima)

        self.buttonLayout.addSpacing(50)

        self.table_Layout.addLayout(self.buttonLayout)
        self.vLayout.addLayout(self.table_Layout)

        # paveikslėlio pridėjimas po lentele
        pixmap = QPixmap("C:/Users/Raminta/Documents/Programavimas su python 2023-12-18/Invoice Management System/logo.jpg")
        pixmap = pixmap.scaled(1900, 100, Qt.KeepAspectRatio)  # paveikslėlio dydžio pritaikymas pagal langą išlaikant proporcijas
        label = QLabel()
        # label.setAlignment(Qt.AlignCenter)
        label.setPixmap(pixmap)
        self.vLayout.addWidget(label)

        self.setLayout(self.vLayout)

        # nurodom sąskaitų katalogo vietą, kurią tikrins
        self.directory_watcher = InvoiceDirectoryWatcher("C:/Users/Raminta/Documents/Programavimas su python 2023-12-18/Invoice Management System/Saskaitos")
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.check_for_new_file)
        # # self.timer.start(1000 * 60 * 60 * 12)  # tikrinti ryte ir vakare (kas 12 val)
        # self.timer.start(10000)

#/////////////////////////////////////   FUNKCIJOS   /////////////////////////////////////

    def get_names_of_suppliers(self):
        names_of_suppliers = []
        try:
            with psycopg2.connect(**db_params) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT DISTINCT tiekejo_pavadinimas FROM saskaitos")
                    rows = cursor.fetchall()
                    for row in rows:
                        names_of_suppliers.append(row[0])
        except Exception as e:
            print(f'Error in get_names_of_suppliers: {e}')
        return names_of_suppliers

    def get_project_numbers(self):
        project_numbers = []
        try:
            with psycopg2.connect(**db_params) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT DISTINCT projekto_numeris FROM saskaitos")
                    rows = cursor.fetchall()
                    for row in rows:
                        project_numbers.append(row[0])
        except Exception as e:
            print(f'Error in get_project_numbers: {e}')
        return project_numbers

    def filter_projects(self, text):
        try:
            with psycopg2.connect(**db_params) as connection:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM saskaitos WHERE projekto_numeris LIKE %s"
                    cursor.execute(query, (text+'%',))
                    rows = cursor.fetchall()

                    # atnaujinama lentelė su atrinktais rezultatais
                    self.update_invoice_table(rows)

        except Exception as e:
            print(f'Error in filter_projects: {e}')

    def filter_suppliers(self, text):
        try:
            with psycopg2.connect(**db_params) as connection:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM saskaitos WHERE LOWER(tiekejo_pavadinimas) LIKE LOWER(%s)"
                    cursor.execute(query, ('%'+text+'%',))  # pridedame '%' prie teksto, kad gautume visus tiekėjus, kurių pavadinimai prasideda įvestu tekstu
                    rows = cursor.fetchall()

                    # atnaujinama lentelė su atrinktais rezultatais
                    self.update_invoice_table(rows)
        except Exception as e:
            print(f'Error in filter_suppliers: {e}')
            raise

    def show_chosen_year(self, index):
        try:
            with psycopg2.connect(**db_params) as connection:
                with connection.cursor() as cursor:
                    selected_year = int(self.years_combo.itemText(index))

                    query = (f"SELECT * FROM saskaitos WHERE EXTRACT (YEAR FROM saskaitos_data) = {selected_year}")

                    cursor.execute(query)
                    rows = cursor.fetchall()
                    print(rows)

                    self.update_table_after_filtering(rows)
        except Exception as e:
            print(f'Error in show_chosen_year: {e}')


    def show_chosen_quarter(self, index):
        try:
            with psycopg2.connect(**db_params) as connection:
                with connection.cursor() as cursor:
                    if index == 1:
                        start_month, end_month = 1, 3
                    elif index == 2:
                        start_month, end_month = 4, 6
                    elif index == 3:
                        start_month, end_month = 7, 9
                    elif index == 4:
                        start_month, end_month = 10, 12

                    selected_year = self.years_combo.currentText()
                    if selected_year:
                        selected_year = int(selected_year)

                        query = (f"SELECT * FROM saskaitos WHERE EXTRACT (MONTH FROM saskaitos_data) BETWEEN {start_month} AND {end_month}"
                                 f" AND EXTRACT (YEAR FROM saskaitos_data) = {selected_year}")
                    else:
                        query = (f"SELECT * FROM saskaitos WHERE EXTRACT (MONTH FROM saskaitos_data) BETWEEN {start_month} AND {end_month}")

                    cursor.execute(query)
                    rows = cursor.fetchall()
                    print(rows)

                    self.update_table_after_filtering(rows)
        except Exception as e:
            print(f'Error in show_chosen_quarter: {e}')

    def show_chosen_month(self, index):
        try:
            with psycopg2.connect(**db_params) as connection:
                with connection.cursor() as cursor:
                    selected_month = int(self.months_combo.itemText(index))

                    query = (f"SELECT * FROM saskaitos WHERE EXTRACT (MONTH FROM saskaitos_data) = {selected_month}")

                    cursor.execute(query)
                    rows = cursor.fetchall()
                    print(rows)

                    self.update_table_after_filtering(rows)
        except Exception as e:
            print(f'Error in show_chosen_month: {e}')

    def clean_up_filters(self):
        try:
            with psycopg2.connect(**db_params) as connection:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM saskaitos"
                    cursor.execute(query)
                    rows = cursor.fetchall()

                    self.update_table_after_filtering(rows)
        except Exception as e:
            print(f'Error in clean_up_filters: {e}')

    def update_table_after_filtering(self, rows, today=None):
        try:
            # prieš atnaujinant lentelę 'datetime.date' objektai pakeičiami į tekstą
            for i, row in enumerate(rows):
                list_row = list(row)
                for j, item in enumerate(list_row):
                    if isinstance(item, date):
                        list_row[j] = item.strftime('%Y-%m-%d')
                rows[i] = tuple(list_row)

            self.saskaitu_sarasas.setRowCount(len(rows))
            self.saskaitu_sarasas.setColumnCount(10)

            # lentelės stulpelių pavadinimai
            headers = ['Įrašo Nr.', 'Projekto Nr.', 'Tiekėjas', 'Sąskaitos Nr.', 'Sąskaitos data', 'Apmokėti iki',
                       'Skubumas', 'Apmokėta / Neapmokėta', 'Kada apmokėta', 'Pastabos']
            self.saskaitu_sarasas.setHorizontalHeaderLabels(headers)
            self.saskaitu_sarasas.horizontalHeader().setStyleSheet('QHeaderView::section { background-color: lightgrey}')

            # gaunama šios dienos data
            if today is None:
                today = date.today().strftime('%Y-%m-%d')

            for i, row in enumerate(rows):
                for j, item in enumerate(row):
                    if item is None:
                        item = ''  # None pakeičiamas tuščiu laukeliu

                    if j in [4, 5, 8]:  # 'Sąskaitos data', 'Apmokėti iki', 'Kada apmokėta' stuleplių indeksai
                        # if item and isinstance(item, datetime.date):  # patikrinama ar reikšmė nėra tuščias laukelis ir yra data
                        if item:  # patikrinama ar reikšmė nėra tuščias laukelis
                            if isinstance(item, date):  # patikrinama ar reikšmė yra data
                                item = datetime.strftime('%Y-%m-%d')  #
                        table_item = QTableWidgetItem(str(item))
                    else:
                        table_item = QTableWidgetItem(str(item))

                    # nuspalvinamos eilutės, jeigu atitinkamos sąlygos yra tenkinamos
                    if row[5] and datetime.strptime(row[5], '%Y-%m-%d').date().strftime('%Y-%m-%d') == today and row[
                        7] == 'Neapmokėta':
                        table_item.setBackground(QColor(255, 0, 0))  # raudona spalva
                    elif row[6] == 'Skubu':
                        table_item.setBackground(QColor(255, 0, 0))  # raudona spalva
                    elif row[7] == 'Apmokėta':
                        table_item.setBackground(QColor(144, 238, 144))  # šviesiai žalia spalva

                    try:
                        self.saskaitu_sarasas.setItem(i, j, table_item)
                        self.saskaitu_sarasas.resizeColumnToContents(j)
                    except Exception as e:
                        print(f'Error in update_invoice_table.setItem(i, j, table_item): {e}')

            self.saskaitu_sarasas.show()

        except Exception as e:
            print(f"Error from update_table_after_filtering: {e}")


    def update_invoice_table(self, rows, today=None):
        try:
            self.saskaitu_sarasas.setRowCount(len(rows))
            self.saskaitu_sarasas.setColumnCount(10)

            # lentelės stulpelių pavadinimai
            headers = ['Įrašo Nr.', 'Projekto Nr.', 'Tiekėjas', 'Sąskaitos Nr.', 'Sąskaitos data', 'Apmokėti iki',
                       'Skubumas', 'Apmokėta / Neapmokėta', 'Kada apmokėta', 'Pastabos']
            self.saskaitu_sarasas.setHorizontalHeaderLabels(headers)
            self.saskaitu_sarasas.horizontalHeader().setStyleSheet('QHeaderView::section { background-color: lightgrey}')

            # gaunama šios dienos data
            if today is None:
                today = date.today().strftime('%Y-%m-%d')

            for i, row in enumerate(rows):
                for j, item in enumerate(row):
                    if item is None:
                        item = ''  # None pakeičiamas tuščiu laukeliu

                    if j in [4, 5, 8]:  # 'Sąskaitos data', 'Apmokėti iki', 'Kada apmokėta' stuleplių indeksai
                        # if item and isinstance(item, datetime.date):  # patikrinama ar reikšmė nėra tuščias laukelis ir yra data
                        if item:  # patikrinama ar reikšmė nėra tuščias laukelis
                            if isinstance(item, date):  # patikrinama ar reikšmė yra data
                                item = item.strftime('%Y-%m-%d')  # data paverčiama į tekstinę reikšmę
                            elif isinstance(item, str):  # patikrinama ar reikšmė yra tekstas
                                try:
                                    item = datetime.strptime(item, '%Y-%m-%d').date()
                                except ValueError:
                                    pass
                        table_item = QTableWidgetItem(str(item))
                    else:
                        table_item = QTableWidgetItem(str(item))

                    # nuspalvinamos eilutės, jeigu atitinkamos sąlygos yra tenkinamos
                    if row[5] and datetime.strptime(row[5], '%Y-%m-%d').date().strftime('%Y-%m-%d') == today and row[7] == 'Neapmokėta':
                        table_item.setBackground(QColor(255, 0, 0))  # raudona spalva
                    elif row[6] == 'Skubu':
                        table_item.setBackground(QColor(255, 0, 0))  # raudona spalva
                    elif row[7] == 'Apmokėta':
                        table_item.setBackground(QColor(144, 238, 144))  # šviesiai žalia spalva

                    try:
                        self.saskaitu_sarasas.setItem(i, j, table_item)
                        self.saskaitu_sarasas.resizeColumnToContents(j)
                    except Exception as e:
                        print(f'Error in update_invoice_table.setItem(i, j, table_item): {e}')

            self.saskaitu_sarasas.show()

        except Exception as e:
            print(f"Error from update_invoice_table: {e}")

    def invoice_registration_form(self):
        try:
            self.registrationDialog = QDialog()
            self.registrationDialog.setWindowTitle("Gautų sąskaitų registravimas")
            self.registrationDialog.setFixedSize(400, 500)

            self.vLayout = QVBoxLayout()  # pagrindinis vertikalus išdėstymas

            # pildymo laukelių išdėstymas
            self.fLayout = QFormLayout(self)

            self.saskaitos_mygtukas = QPushButton('Sąskaitų katalogas')
            self.saskaitos_mygtukas.setFixedSize(150, 30)
            self.saskaitos_mygtukas.setStyleSheet("font-size: 10px;")
            self.saskaitos_mygtukas.clicked.connect(self.open_invoice_catalog)
            self.fLayout.addRow(QLabel('Pasirinkti sąskaitą ->'), self.saskaitos_mygtukas)

            self.projektoNr_field = QLineEdit()
            self.projektoNr_field.setFixedSize(150, 30)
            self.projektoNr_field.setStyleSheet("font-size: 10px;")
            self.fLayout.addRow(QLabel('Projekto numeris:'), self.projektoNr_field)

            self.tiekejas_field = QLineEdit()
            self.tiekejas_field.setFixedSize(150, 30)
            self.fLayout.addRow(QLabel('Pardavėjo pavadinimas:'), self.tiekejas_field)

            self.saskaitosNr_field = QLineEdit()
            self.saskaitosNr_field.setFixedSize(150, 30)
            self.fLayout.addRow(QLabel('Sąskaitos numeris:'), self.saskaitosNr_field)

            self.saskaitosData_field = QDateEdit()
            self.saskaitosData_field.setDisplayFormat("yyyy-MM-dd")
            self.saskaitosData_field.setCalendarPopup(True)
            self.saskaitosData_field.setDate(QDate.currentDate())
            self.saskaitosData_field.setFixedSize(150, 30)
            self.fLayout.addRow(QLabel('Sąskaitos data:'), self.saskaitosData_field)

            self.apmoketiIki_field = QDateEdit()
            self.apmoketiIki_field.setDisplayFormat("yyyy-MM-dd")
            self.apmoketiIki_field.setCalendarPopup(True)
            self.apmoketiIki_field.setDate(QDate.currentDate())
            self.apmoketiIki_field.setFixedSize(150, 30)
            self.fLayout.addRow(QLabel('Apmokėti iki:'), self.apmoketiIki_field)

            # apmokėjimo skubumo pasirinkimas
            self.skubumas = QComboBox()
            self.skubumas.addItem('Neskubu')
            self.skubumas.addItem('Skubu')
            self.skubumas.setFixedSize(150, 30)
            self.fLayout.addRow(QLabel('Apmokėjimo skubumas:'), self.skubumas)

            self.busena = QComboBox()
            self.busena.addItem("Apmokėta")
            self.busena.addItem("Neapmokėta")
            self.busena.setFixedSize(150, 30)
            self.fLayout.addRow(QLabel('Sąskaitos būsena:'), self.busena)

            # apmokėjimo datos laukelio ir pasirinkimo išdėstymas horizontaliai
            apmoketaLayout = QHBoxLayout()

            self.apmokejimoData_label = QLabel('Apmokėta (data):')
            apmoketaLayout.addWidget(self.apmokejimoData_label)
            apmoketaLayout.addStretch()

            self.apmokejimoData_field = QLineEdit()
            self.apmokejimoData_field.setFixedSize(150, 30)
            apmoketaLayout.addWidget(self.apmokejimoData_field)

            self.calendar_button = QPushButton('Pasirinkti datą')
            self.calendar_button.clicked.connect(self.open_calendar)
            apmoketaLayout.addWidget(self.calendar_button)

            self.fLayout.addRow(apmoketaLayout)

            self.pastabos_field = QLineEdit()
            self.pastabos_field.setFixedSize(150, 30)
            self.fLayout.addRow(QLabel('Pastabos:'), self.pastabos_field)

            self.sutikrinimas_combo = QComboBox()
            self.sutikrinimas_combo.setFixedSize(150, 30)
            self.sutikrinimas_combo.addItems(['Patikrinti', 'Sutikrinta'])
            self.sutikrinimas_combo.currentTextChanged.connect(self.update_pastabos_field)
            self.fLayout.addRow(QLabel('Patikrinti / Sutikrinta:'), self.sutikrinimas_combo)

            self.vLayout.addLayout(self.fLayout)

            # registracijos mygtuko sukūrimas
            self.insert_button = QPushButton("Užregistruoti gautą sąskaitą")
            self.insert_button.setFixedSize(200, 40)
            self.insert_button.clicked.connect(self.register_invoice_received)

            # mygtuko centravimas
            self.hLayout = QHBoxLayout()  # horizontalus išdėstymas, kad eitų centruoti
            self.hLayout.addStretch()
            self.hLayout.addWidget(self.insert_button)
            self.hLayout.addStretch()

            self.vLayout.addSpacing(1)
            self.vLayout.addLayout(self.hLayout)
            self.vLayout.addSpacing(60)

            self.registrationDialog.setLayout(self.vLayout)
            self.registrationDialog.show()

        except Exception as e:
            print(f'Error in register_invoice_received: {e}')

    def open_invoice_catalog(self):
        try:
            filename, _ =QFileDialog.getOpenFileName(None, "Pasirinkite PDF failą",
                                                     "C:/Users/Raminta/Documents/Programavimas su python 2023-12-18/Invoice Management System/Saskaitos",
                                                     "PDF Files (*.pdf)")
            if filename:
                os.system(f'start "" "{filename}"')  # (f'start {filename}') nesuveikė, todėl reikėjo pridėti papildomas kabutes
            else:
                QMessageBox.warning(self, "Perspėjimas", "Nepasirinktas joks failas")

        except Exception as e:
            print(f'Error in open_invoice_catalog: {e}')


    def open_calendar(self):
        dialog = QDialog()
        calendar = QCalendarWidget(dialog)
        button = QPushButton('Patvirtinti pasirinktą datą', dialog)
        button.clicked.connect(dialog.accept)

        layout = QVBoxLayout(dialog)
        layout.addWidget(calendar)
        layout.addWidget(button)

        if dialog.exec():
            date = calendar.selectedDate()
            self.apmokejimoData_field.setText(date.toString("yyyy-MM-dd"))

    def update_pastabos_field(self, text):
        current_text = self.pastabos_field.text()
        if current_text:
            new_text = current_text + "; " + text
        else:
            new_text = text
        self.pastabos_field.setText(new_text)

    def register_invoice_received(self): # duomenų įkėlimas į duomenų bazę
        try:
            projekto_numeris = self.projektoNr_field.text()
            tiekejo_pavadinimas = self.tiekejas_field.text()
            saskaitos_nr = self.saskaitosNr_field.text()
            saskaitos_data = self.saskaitosData_field.date().toString("yyyy-MM-dd")
            apmoketi_iki = self.apmoketiIki_field.date().toString("yyyy-MM-dd")
            apmokejimo_skubumas = self.skubumas.currentText()
            apmokejimo_busena = self.busena.currentText()

            # laukelis įrašyti datą, kada sąskaita buvo apmokėta
            kada_apmoketa = self.apmokejimoData_field.text()
            if kada_apmoketa == '':  # patikrinama, ar datos laukelis tuščias
                kada_apmoketa = None  # jei data neįvedama, duomenų bazės lentelėje bus įrašoma NULL reikšmė

            # pastabų laukelis
            pastabos = self.pastabos_field.text()
            if not pastabos:  # jeigu pastabos neįrašytos, bus rodoma NULL reikšmė
                pastabos = None

            with psycopg2.connect(**db_params) as connection:
                with connection.cursor() as cursor:
                    # patikrinama, ar sąskaitos numeris jau yra sąskaitų registre
                    cursor.execute('SELECT * FROM saskaitos WHERE saskaitos_nr = %s AND tiekejo_pavadinimas = %s', (saskaitos_nr, tiekejo_pavadinimas,))
                    existing_invoice = cursor.fetchone()

                    if existing_invoice is not None:
                        QMessageBox.warning(self, 'Įspėjimas', 'Toks sąskaitos numeris jau yra sąskaitų registre')
                        return

                     # jei sąskaitos numerio nėra, tęsiamas įrašymas
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
                    headers = ['Įrašo Nr.', 'Projekto Nr.', 'Tiekėjas', 'Sąskaitos Nr.', 'Sąskaitos data', 'Apmokėti iki', 'Skubumas',
                               'Apmokėta / Neapmokėta', 'Kada apmokėta', 'Pastabos']
                    self.saskaitu_sarasas.setHorizontalHeaderLabels(headers)
                    self.saskaitu_sarasas.horizontalHeader().setStyleSheet('QHeaderView::section { background-color: lightgrey}')

                    # gaunama šios dienos data
                    today = date.today().strftime('%Y-%m-%d')

                    for i, row in enumerate(rows):
                        for j, item in enumerate(row):
                            if item is None:
                                item = ''  # None pakeičiamas tuščiu laukeliu

                            if j in [4, 5, 8]:  # 'Sąskaitos data', 'Apmokėti iki', 'Kada apmokėta' stuleplių indeksai
                                # if item and isinstance(item, date):  # patikrinama ar reikšmė nėra tuščias laukelis ir yra data
                                if isinstance(item, date):  # patikrinama ar reikšmė nėra tuščias laukelis ir yra data
                                    item = item.strftime('%Y-%m-%d')  # data paverčiama į tekstinę reikšmę
                                table_item = QTableWidgetItem(str(item))
                            else:
                                table_item = QTableWidgetItem(str(item))

                            # nuspalvinamos eilutės, jeigu atitinkamos sąlygos yra tenkinamos
                            if row[5] and row[5].strftime('%Y-%m-%d') == today and row[7] == 'Neapmokėta':
                                table_item.setBackground(QColor(255, 0, 0))  # raudona spalva
                            elif row[6] == 'Skubu':
                                table_item.setBackground(QColor(255, 0, 0))  # raudona spalva
                            elif row[7] == 'Apmokėta':
                                table_item.setBackground(QColor(144, 238, 144))  # šviesiai žalia spalva

                            try:
                                self.saskaitu_sarasas.setItem(i, j, table_item)
                                self.saskaitu_sarasas.resizeColumnToContents(j)
                            except Exception as e:
                                print(f'Error in display_registry_of_invoices.setItem(i, j, table_item): {e}')

            self.saskaitu_sarasas.show()

        except Exception as e:
            print(f"Error from display_registry_of_invoices: {e}")


    def invoice_payment_confirmation(self):
        try:
            current_row = self.saskaitu_sarasas.currentRow()
            if current_row >= 0:
                self.apmokejimo_busena_changed(current_row, "Apmokėta", datetime.date.today().strftime('%Y-%m-%d'))
        except Exception as e:
            print(f"Error from invoice_payment_confirmation: {e}")

    def apmokejimo_busena_changed(self, row, new_payment_status, payment_date):
        # gaunamas sąskaitos numeris iš pasirinktos eilutės
        invoice_number_item = self.saskaitu_sarasas.item(row, 3)
        invoice_number = invoice_number_item.text()
        try:
            with psycopg2.connect(**db_params) as connection:
                with connection.cursor() as cursor:
                    update_query = """
                      UPDATE saskaitos SET
                      apmokejimo_busena = %s,
                      kada_apmoketa = %s
                      WHERE saskaitos_nr = %s
                      """

                    cursor.execute(update_query, (new_payment_status, payment_date, invoice_number))
                    connection.commit()

                    QMessageBox.information(self, "Informacija", "Sėkmingai atnaujinta apmokėjimo būsena ir apmokėjimo data",
                                            QMessageBox.Ok)
                    try:  # atnaujinti rodomus duomenis lentelėje
                        self.saskaitu_sarasas.setItem(row, 6, QTableWidgetItem(''))
                        self.saskaitu_sarasas.setItem(row, 7, QTableWidgetItem(new_payment_status))
                        self.saskaitu_sarasas.setItem(row, 8, QTableWidgetItem(payment_date if payment_date is not None else '' ))
                        self.display_registry_of_invoices()
                    except Exception as e:
                        print(f'Error in apmokejimo_busena_changed when updating table: {e}')

        except Exception as e:
            print(f'Error in apmokejimo_busena_changed: {e}')
            QMessageBox.warning(self, "Klaida", "Klaida atnaujinant duomenis")

    def update_record_button_clicked(self):
        try:
            # gaunami pažymėtos eilutės duomenys
            current_data = self.get_current_record()
            record_id = current_data[0]

            # sukuriamas ir atidaromas UpdateRecordWindow langas
            self.update_record_window = UpdateRecordWindow(record_id, current_data, self)

            # iškviečiamas duomenų bazės atnaujinimo metodas patvirtinus pakeitimus
            self.update_record_window.form_submitted.connect(self.update_database)

            self.update_record_window.show()
        except Exception as e:
            print(f"Error from update_record_button_clicked: {e}")

    def get_current_record(self):
        try:
            # pažymėtos eilutės identifikavimas
            current_row = self.saskaitu_sarasas.currentRow()

            # gaunam duomenis iš lentelės
            current_data = []
            for i in range(10):
                item = self.saskaitu_sarasas.item(current_row, i)
                if item is not None:
                    value = item.text()
                    if value == '--' or value == 'None':
                        value = ''
                    current_data.append(value)

            print(f'Current_data: {current_data}')
            return current_data

        except Exception as e:
            print(f"Error from update_record: {e}")

    def update_database(self, updated_projekto_numeris, updated_tiekejo_pavadinimas, updated_saskaitos_nr, updated_saskaitos_data,
                        updated_apmoketi_iki, updated_apmokejimo_skubumas, updated_apmokejimo_busena, updated_apmokejimo_data, updated_pastabos, record_id):
        try:
            # sukuriamos naujos reikšmės
            new_values = (updated_projekto_numeris, updated_tiekejo_pavadinimas, updated_saskaitos_nr, updated_saskaitos_data, updated_apmoketi_iki,
                          updated_apmokejimo_skubumas, updated_apmokejimo_busena, updated_apmokejimo_data, updated_pastabos, record_id)
            print(f'New values: {new_values}')
            self.confirm_update(record_id, new_values)

        except Exception as e:
            print(f"Error from update_database: {e}")


    def confirm_update(self, record_id, new_values):
        try:
            if record_id and record_id.isdigit():
                with psycopg2.connect(**db_params) as connection:
                    with connection.cursor() as cursor:

                        new_values = list(new_values)
                        updated_apmokejimo_data = new_values[8]
                        if updated_apmokejimo_data == '':
                            new_values[8] = None

                        update_query = """
                        UPDATE saskaitos SET
                        projekto_numeris = %s,
                        tiekejo_pavadinimas = %s,
                        saskaitos_nr = %s,
                        saskaitos_data = %s,
                        apmoketi_iki = %s,
                        apmokejimo_skubumas = %s,
                        apmokejimo_busena = %s,
                        kada_apmoketa = NULLIF(%s, '')::date,
                        pastabos = %s
                        WHERE saskaitos_id = %s
                        """

                        cursor.execute(update_query, new_values)
                        connection.commit()

                        # gaunamas pakoreguotų eilučių skaičius ir parodomas pranešimas
                        count = cursor.rowcount
                        QMessageBox.information(self, "Information", f"Sėkmingai atnaujinta {count} įrašai(-ų)", QMessageBox.Ok)

                        try:
                            self.display_registry_of_invoices()
                        except Exception as e:
                            print(f'Error in confirm_update method when updating the table: {e}')
            else:
                print(f"Error in confirm_update: Invalid saskaitos_id")

        except Exception as e:
            print(f'Error from confirm_update: {e}')
            QMessageBox.warning(self, "Error", 'Klaida atnaujinant duomenis')

    def delete_record(self):
        try:
            # pažymėtos eilutės identifikavimas
            current_row = self.saskaitu_sarasas.currentRow()

            # gaunamas įrašo id iš lentelės
            record_id = self.saskaitu_sarasas.item(current_row, 0)
            if record_id is not None:
                record_id = record_id.text()

            # prisijungiam prie duomenų bazės
            with psycopg2.connect(**db_params) as connection:
                with connection.cursor() as cursor:
                    delete_query = "DELETE FROM saskaitos WHERE saskaitos_id = %s"

                    cursor.execute(delete_query, (record_id,))
                    connection.commit()
            self.saskaitu_sarasas.removeRow(current_row)  # ištrinamas pažymėtas lentelės įrašas

            QMessageBox.information(self, 'Informacija', 'Įrašas sėkmingai ištrintas iš duomenų bazės')
            # atnaujinamas lentelės vaizdas
            self.display_registry_of_invoices()

        except Exception as e:
            print(f'Trinant įrašą kilo problema: {e}')


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

    def create_invoice(self):  # sąskaitos išrašymo funkcijos iškvietimas
        try:
            from pdf_kurimas import CreationOfInvoice
            invoice = CreationOfInvoice()
            invoice.create_invoice_clicked()
        except Exception as e:
            print(f"Error from create_invoice: {e}")


    def check_invoices_due_date(self):
        try:
            with psycopg2.connect(**db_params) as connection:
                with connection.cursor() as cursor:
                    # gaunama šios dienos data
                    today = datetime.date.today().strftime('%Y-%m-%d')

                    # gaunamos sąskaitos, kurių apmokėjimo data yra šiandien
                    cursor.execute("SELECT * FROM saskaitos WHERE apmoketi_iki = %s AND apmokejimo_busena = 'Neapmoketa'", (today,))
                    rows = cursor.fetchall()

                    if not rows:  # jeigu nėra apmokėtinų sąskaitų
                        QMessageBox.information(self, 'Informacija', 'Apmokėtinų sąskaitų šiai dienai nėra')
                        return

                    # jei yra apmokėtinų sąskaitų, jos parodomos lentelės pavidalu
                    self.saskaitu_sarasas.setRowCount(len(rows))
                    self.saskaitu_sarasas.setColumnCount(10)

                    headers = ['Įrašo Nr.', 'Projekto Nr.', 'Tiekėjas', 'Sąskaitos Nr.', 'Sąskaitos data', 'Apmokėti iki',
                               'Skubumas', 'Apmokėta / Neapmokėta', 'Kada apmokėta', 'Pastabos']
                    self.saskaitu_sarasas.setHorizontalHeaderLabels(headers)
                    self.saskaitu_sarasas.horizontalHeader().setStyleSheet('QHeaderView::section {background-color: lightgrey}')

                    for i, row in enumerate(rows):
                        for j, item in enumerate(row):
                            if item is None:
                                item = ''
                            table_item = QTableWidgetItem(str(item))
                            self.saskaitu_sarasas.setItem(i, j, table_item)
                            self.saskaitu_sarasas.resizeColumnToContents(j)
                    self.saskaitu_sarasas.show()

        except Exception as e:
            print(f'Error in check_invoices_due_date: {e}')

    def on_invoiceNo_clicked(self, row, column):
        if column == 3:  # jeis paspaustas stulpelis yra 'Sąskaitos Nr.'
            item = self.saskaitu_sarasas.item(row, column)
            self.open_invoice(item)

    def open_invoice(self, item):
        saskaitos_nr = item.text()
        filename = f"C:/Users/Raminta/Documents/Programavimas su python 2023-12-18/Invoice Management System/Saskaitos/{saskaitos_nr}.pdf"
        os.system(f'start "" "{filename}"')


# //////////////////////////////////////////

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

#@@@@@@@@@@@@@@@@@@@  APMOKĖJIMO BŪSENA CHECKBOX KLASĖ @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#
# class ComboBoxItem(QTableWidgetItem):
#     def __init__(self, text):
#         super().__init__(text)
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = ComboBoxItem()
#     window.show()
#     sys.exit(app.exec_())