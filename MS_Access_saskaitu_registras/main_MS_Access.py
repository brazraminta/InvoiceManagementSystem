import pyodbc
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QStringListModel
from PyQt5.QtGui import QColor, QFont, QPixmap
import datetime
from datetime import datetime, date, timedelta
import sys
import os
import logging
import xlsxwriter
import subprocess
import shutil
import glob
import fnmatch
import re



#////////////////////////////////////////   LOGGING   \\\\\\\\\\\\\\\\\\\\\\\\\\\\
# programos veikimo logavimas
logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s - %(levelname)s - %(message)s',
                    filename='MS_Access.log',
                    filemode='w')  # 'w' reiškia, kad failas bus perrašytas kiekvieną kartą pradedant programą


#////////////////////////////////    DUOMENŲ BAZĖS KELIAS    \\\\\\\\\\\\\\\\\\\\
# duomenų bazės kelias
db_path = r"C:\Users\Raminta\Documents\Programavimas su python 2023-12-18\Invoice Management System\Access\Gaunamų sąskaitų registras.accdb"
# db_path = r"C:\Users\TetianaJonaitis\UAB Indasta\Indasta - Dokumentai\00_Buhalteriniai dokumentai\01_Gaunamos sąskaitos 2024\Gaunamų sąskaitų registras.accdb"
# db_path = r"C:\Users\Andrius\Documents\Gaunamų sąskaitų registras.accdb"

#//////////////////////////////////  KLASĖ FAILŲ KATALOGO TIKRINIMUI   \\\\\\\\\\\\\\

# # (REIKIA PADARYTI, KAD TIKRINTŲ SHAREPOINT AR ONEDRIVE KATALOGĄ)
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

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@   ĮRAŠŲ KOREGAVIMO KLASĖ   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

class UpdateRecordWindow(QDialog):

    form_submitted = pyqtSignal(str, str, str, str, str, str, str, str, str, str)

    def __init__(self, record_id, current_data, main_window, parent=None):
        super().__init__(parent)
        self.record_id = record_id
        self.main_window = main_window

        self.setWindowTitle("Įrašo koregavimo langas")
        self.setFixedSize(500, 600)

        self.vLayout = QVBoxLayout()  # pagrindinis išdėstymas
        self.fLayout = QFormLayout()  # pildymo laukelių išdėstymas

        # sukuriami QLineEdit laukeliai kiekvienai reikšmei, kuri gali būti atnaujinta
        self.updated_Projekto_nr = QLineEdit(current_data[1])
        self.updated_Projekto_nr.setFixedSize(150, 30)
        self.updated_Projekto_nr.setStyleSheet("font-size: 12px;")
        self.fLayout.addRow(QLabel('Projekto numeris:'), self.updated_Projekto_nr)

        self.updated_tiekejo_pavadinimas = QLineEdit(current_data[2])
        self.updated_tiekejo_pavadinimas.setFixedSize(150, 30)
        self.updated_tiekejo_pavadinimas.setStyleSheet("font-size: 12px;")
        self.fLayout.addRow(QLabel('Tiekėjo pavadinimas:'), self.updated_tiekejo_pavadinimas)

        self.updated_saskaitos_nr = QLineEdit(current_data[3])
        self.updated_saskaitos_nr.setFixedSize(150, 30)
        self.updated_saskaitos_nr.setStyleSheet("font-size: 12px;")
        self.fLayout.addRow(QLabel('Sąskaitos numeris:'), self.updated_saskaitos_nr)

        self.updated_saskaitos_data = QDateEdit()
        self.updated_saskaitos_data.setCalendarPopup(True)
        self.updated_saskaitos_data.setDate(QDate.fromString(current_data[4], "yyyy-MM-dd"))
        self.updated_saskaitos_data.setFixedSize(150, 30)
        self.updated_saskaitos_data.setFont(QFont("Arial", 9))
        self.fLayout.addRow(QLabel('Sąskaitos data:'), self.updated_saskaitos_data)

        self.updated_apmoketi_iki = QDateEdit()
        self.updated_apmoketi_iki.setCalendarPopup(True)
        self.updated_apmoketi_iki.setDate(QDate.fromString(current_data[5], "yyyy-MM-dd"))
        self.updated_apmoketi_iki.setFixedSize(150, 30)
        self.updated_apmoketi_iki.setFont(QFont("Arial", 9))
        self.fLayout.addRow(QLabel('Apmokėti iki:'), self.updated_apmoketi_iki)

        self.updated_skubumas_combo = QComboBox()
        self.updated_skubumas_combo.setFixedSize(150, 30)
        self.updated_skubumas_combo.setStyleSheet("font-size: 12px;")
        self.updated_skubumas_combo.addItems(['', 'Skubu'])
        self.fLayout.addRow(QLabel('Skubu / Neskubu:'), self.updated_skubumas_combo)

        # QCombo laukelis sąskaitos būsenos pakeitimui
        self.apmokejimo_busena_combo = QComboBox()
        self.apmokejimo_busena_combo.setFixedSize(150, 30)
        self.apmokejimo_busena_combo.setStyleSheet("font-size: 12px;")
        self.apmokejimo_busena_combo.addItems(['Neapmokėta', 'Apmokėta'])
        self.fLayout.addRow(QLabel('Apmokėjimo būsena:'), self.apmokejimo_busena_combo)

        # dabartinės apmokėjimo datos laukelis
        hLayout = QHBoxLayout()
        hLayout.addWidget(QLabel('Esama apmokėjimo data:'))

        self.current_apmokejimo_data = QLineEdit(current_data[6])
        self.current_apmokejimo_data.setFixedSize(150, 30)
        self.current_apmokejimo_data.setFont(QFont("Arial", 9))
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

        self.updated_apmokejimo_data = QDateEdit()
        self.updated_apmokejimo_data.setDisplayFormat("yyyy-MM-dd")
        self.updated_apmokejimo_data.setCalendarPopup(True)
        self.updated_apmokejimo_data.setDate(QDate.currentDate())
        self.updated_apmokejimo_data.setFixedSize(150, 30)
        self.updated_apmokejimo_data.setFont(QFont("Arial", 9))
        hLayout2.addWidget(self.updated_apmokejimo_data)

        self.update_date_checkbox = QCheckBox('Atnaujinti datą')
        self.update_date_checkbox.setStyleSheet("font-size: 12px;")
        self.update_date_checkbox.setChecked(True)
        self.update_date_checkbox.stateChanged.connect(self.on_update_date_checkbox_changed)
        hLayout2.addWidget(self.update_date_checkbox)
        hLayout2.addStretch()

        self.fLayout.addRow(hLayout2)

        self.updated_pastabos = QLineEdit(current_data[8])
        self.updated_pastabos.setFixedSize(150, 30)
        self.updated_pastabos.setStyleSheet("font-size: 12px;")
        self.fLayout.addRow(QLabel('Pastabos:'), self.updated_pastabos)

        self.new_sutikrinimas_combo = QComboBox()
        self.new_sutikrinimas_combo.setFixedSize(150, 30)
        self.new_sutikrinimas_combo.setStyleSheet("font-size: 12px;")
        self.new_sutikrinimas_combo.addItems(['Patikrinti', 'Sutikrinta'])
        self.new_sutikrinimas_combo.currentTextChanged.connect(self.update_updated_pastabos_field)
        self.fLayout.addRow(QLabel('Patikrinti / Sutikrinta:'), self.new_sutikrinimas_combo)

        # self.updated_sudengta = QLineEdit(current_data[10])
        # self.updated_sudengta.setFixedSize(150, 30)
        # self.updated_sudengta.setStyleSheet("font-size: 12px;")
        # self.fLayout.addRow(QLabel('Sudengta: '), self.updated_sudengta)

        # pakeitimų patvirtinimo mygtukas
        self.submit_button = QPushButton("Patvirtinti pakeitimus")
        self.submit_button.clicked.connect(self.submit_form)
        self.fLayout.addWidget(self.submit_button)

        self.vLayout.addLayout(self.fLayout)

        self.setLayout(self.vLayout)
        # self.show()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@   PAKEITIMŲ KLASĖS METODAI   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
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

            # apmokėjimo datos pakeitimų ar esamų reikšmių įrašymas į duomenų bazę
            if self.update_date_checkbox.isChecked():
                updated_apmokejimo_data = self.updated_apmokejimo_data.date().toString("yyyy-MM-dd") if not self.updated_apmokejimo_data.text() == '' else ''
            elif self.null_date_checkbox.isChecked():
                updated_apmokejimo_data = ''
            else:
                updated_apmokejimo_data = self.current_apmokejimo_data.text()  # įrašoma esama data

            # QCombo laukelis apmokėjimo būsenos pakeitimui
            updated_apmokejimo_busena_text = self.apmokejimo_busena_combo.currentText()
            index = self.apmokejimo_busena_combo.findText(updated_apmokejimo_busena_text)
            if index >= 0:
                self.apmokejimo_busena_combo.setCurrentIndex(index)

            # QCombo laukelis apmokėjimo skubumo pakeitimui
            updated_apmokejimo_skubumas_text = self.updated_skubumas_combo.currentText()
            skubumas_index = self.updated_skubumas_combo.findText(updated_apmokejimo_skubumas_text)
            if skubumas_index >= 0:
                self.updated_skubumas_combo.setCurrentIndex(skubumas_index)

            updated_pastabos = self.updated_pastabos.text()
            if not updated_pastabos:  # jeigu pastabos neįrašytos, bus rodoma NULL reikšmė
                updated_pastabos = None

            # updated_sudengta = self.updated_sudengta.text()
            # if not updated_sudengta:
            #     updated_sudengta = None

            self.form_submitted.emit(updated_projekto_numeris, updated_tiekejo_pavadinimas, updated_saskaitos_nr, updated_saskaitos_data,
                                     updated_apmoketi_iki, updated_apmokejimo_data, updated_apmokejimo_busena_text,
                                     updated_apmokejimo_skubumas_text, updated_pastabos, self.record_id)
            try:
                self.close()

                # įrašų atvaizdavimo metodo iškvietimas iš MainWindow klasės
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
        self.initUI()

    def initUI(self):

        self.setWindowTitle('Sąskaitų Valdymo Sistema')
        self.setGeometry(20, 50, 1900, 950)  # lango dydis pagal pikselius

        self.central_widget = QWidget(self)
        self.vLayout = QVBoxLayout(self.central_widget)

        # sąskaitų registro ir filtrų išdėstymas
        self.hLayout = QHBoxLayout()
        
        # mygtukų pavadinimų ir laukelių šrifto dydis
        font = QFont()
        font.setPointSize(9)

        # vertikalus išdėstymas QLabel (filtrų pavadinimas)
        self.label_vLayout = QVBoxLayout()
        
        self.label_vLayout.addSpacing(10)

        # paieškos filtrų pavadinimas
        self.filter_title = QLabel("Filtruoti įrašus pagal:")
        self.filter_title.setAlignment(Qt.AlignLeft)
        self.filter_title.setStyleSheet("QLabel{font-size: 12pt;}")
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

        # laukelių pridėjimas į išdėstymą
        self.hLayout.addWidget(self.tiekejas_label)
        self.hLayout.addWidget(self.tiekejas_input)

        self.hLayout.addStretch(20)  # tarpelis tarp laukelių

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
        self.months_combo.addItem("")   # pridedama tuščia reikšmė
        self.months_combo.addItems(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
        # self.months_combo.insertItem(0, "")  # pridedama tuščia reikšmė
        self.months_combo.setCurrentIndex(0)  # nustatoma tuščia reikšmė kaip pasirinkta pagal nutylėjimą
        self.months_combo.currentIndexChanged.connect(self.show_chosen_month)
        self.hLayout.addWidget(self.months_combo)

        self.hLayout.addSpacing(100)

        # pridedam pasirinktų paieškos filtrų išvalymą
        self.filter_cleanup = QPushButton("Išvalyti filtrus", self)
        self.filter_cleanup.setFont(font)
        self.filter_cleanup.setFixedSize(150, 40)
        self.filter_cleanup.clicked.connect(self.clean_up_filters)
        # self.filter_cleanup.clicked.connect(self.display_registry_of_invoices)  # iš naujo įkeliami įrašai iš duomenų bazės
        self.hLayout.addWidget(self.filter_cleanup)

        self.hLayout.addStretch(20)

        # tikrinimas, ar yra apmokėtinų sąskaitų einamajai dienai
        self.tikrinti_apmokejima = QPushButton('Neapmokėtos sąskaitos')
        self.tikrinti_apmokejima.setFont(font)
        self.tikrinti_apmokejima.setFixedSize(200, 40)
        self.tikrinti_apmokejima.clicked.connect(self.check_invoices_due_date)
        self.tikrinti_apmokejima.setStyleSheet("background-color: red;")
        self.hLayout.addWidget(self.tikrinti_apmokejima)

        self.hLayout.addSpacing(200)

        self.vLayout.addLayout(self.hLayout)

        # sąskaitų lentelės horizontalus išdėstymas
        self.table_Layout = QHBoxLayout()

        self.saskaitu_sarasas = QTableWidget()
        self.saskaitu_sarasas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.saskaitu_sarasas.resizeColumnsToContents()
        self.saskaitu_sarasas.setSortingEnabled(True)
        self.saskaitu_sarasas.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # nustatome visos eilutės pasirinkimą (ne atskirų stulpelių)
        self.saskaitu_sarasas.setSelectionMode(QAbstractItemView.SingleSelection)  # vienos rezultatų eilutės pasirinkimas, kad kita būtų atžymėta
        self.saskaitu_sarasas.cellClicked.connect(self.on_invoiceNo_clicked)  # paspaudus ant sąskatos numerio, atidaromas sąskaitos failas
        self.saskaitu_sarasas.cellClicked.connect(self.on_projectNo_clicked)  # paspaudus ant projekto numerio, atidaromas projekto katalogas, kuriame yra sąskaitos

        self.table_Layout.addWidget(self.saskaitu_sarasas)

        # mygtukų vertikalus išdėstymas lentlės dešiniajame krašte
        self.buttonLayout = QVBoxLayout()

        self.saskaitu_registras_button = QPushButton('Sąskaitų registras')
        self.saskaitu_registras_button.setFont(font)
        self.saskaitu_registras_button.setFixedSize(200, 40)
        self.saskaitu_registras_button.clicked.connect(self.display_registry_of_invoices)
        self.saskaitu_registras_button.setStyleSheet("background-color: lightgreen;")
        self.buttonLayout.addWidget(self.saskaitu_registras_button)

        self.eksportuoti_i_Excel = QPushButton('Eksportuoti į Excel')
        self.eksportuoti_i_Excel.setFont(font)
        self.eksportuoti_i_Excel.setFixedSize(200, 40)
        self.eksportuoti_i_Excel.clicked.connect(self.on_export_button_clicked)
        self.buttonLayout.addWidget(self.eksportuoti_i_Excel)

        self.suvesti_saskaita_button = QPushButton("Užregistruoti gautą saskaitą")
        self.suvesti_saskaita_button.setFont(font)
        self.suvesti_saskaita_button.setFixedSize(200, 40)
        self.suvesti_saskaita_button.clicked.connect(self.invoice_registration_form)
        self.buttonLayout.addWidget(self.suvesti_saskaita_button)

        # naujų failų paieškos mygtukas skenuotų sąskaitų kataloge
        self.skenuotos_saskaitos = QPushButton('Sąskaitų katalogas')
        self.skenuotos_saskaitos.setFont(font)
        self.skenuotos_saskaitos.setFixedSize(200, 40)
        self.skenuotos_saskaitos.clicked.connect(self.check_for_new_file)
        self.buttonLayout.addWidget(self.skenuotos_saskaitos)
        #
        # # mygtukas sąskaitai išrašyti
        # self.sukurti_saskaita_button = QPushButton('Išrašyti sąskaitą')
        # self.sukurti_saskaita_button.setFont(font)
        # self.sukurti_saskaita_button.setFixedSize(200, 40)
        # self.sukurti_saskaita_button.clicked.connect(self.create_invoice)
        # self.buttonLayout.addWidget(self.sukurti_saskaita_button)

        self.buttonLayout.addSpacing(50)

        # mygtukas sąskaitos apmokėjimo būsenai ir datai pakeisti
        self.apmoketa_button = QPushButton('Patvirtinti apmokėjimą')
        self.apmoketa_button.setFont(font)
        self.apmoketa_button.setFixedSize(200, 40)
        self.apmoketa_button.clicked.connect(self.invoice_payment_confirmation)
        self.buttonLayout.addWidget(self.apmoketa_button)

        # mygtukas įrašo koregavimui
        self.koreguoti_irasa_button = QPushButton('Koreguoti įrašą')
        self.koreguoti_irasa_button.setFont(font)
        self.koreguoti_irasa_button.setFixedSize(200, 40)
        self.koreguoti_irasa_button.clicked.connect(self.update_record_button_clicked)
        self.buttonLayout.addWidget(self.koreguoti_irasa_button)

        # mygtukas įrašo ištrynimui
        self.istrinti_irasa_button = QPushButton('Ištrinti įrašą')
        self.istrinti_irasa_button.setFont(font)
        self.istrinti_irasa_button.setFixedSize(200, 40)
        self.istrinti_irasa_button.clicked.connect(self.delete_record)
        self.buttonLayout.addWidget(self.istrinti_irasa_button)

        self.buttonLayout.addSpacing(50)

        # mygtukų išdėstymas pridedamas į lentelės išdėstymą
        self.table_Layout.addLayout(self.buttonLayout)
        # lentelės išdėstymas pridedamas į pagrindinį išdėstymą
        self.vLayout.addLayout(self.table_Layout)
        #
        # # paveikslėlio pridėjimas po lentele
        # pixmap = QPixmap("C:/Users/Raminta/Documents/Programavimas su python 2023-12-18/Invoice Management System/logo.jpg")
        # pixmap = pixmap.scaled(1900, 100, Qt.KeepAspectRatio)  # paveikslėlio dydžio pritaikymas pagal langą išlaikant proporcijas
        # label = QLabel()
        # label.setPixmap(pixmap)  # pridedamas paveikslėlis
        # self.vLayout.addWidget(label)

        # nustatomas pagrindinio lango išdėstymas
        self.central_widget.setLayout(self.vLayout)
        self.setCentralWidget(self.central_widget)

        # nurodom sąskaitų katalogo, kurį tikrins, vietą
        self.directory_watcher = InvoiceDirectoryWatcher("C:/Users/Raminta/OneDrive/Neregistruotos saskaitos")
        # self.directory_watcher = InvoiceDirectoryWatcher("C:/Users/TetianaJonaitis/UAB Indasta/Indasta - Dokumentai/00_Buhalteriniai dokumentai/00_Neregistruotos sąskaitos")
        # # self.timer = QTimer()
        # # self.timer.timeout.connect(self.check_for_new_file)
        # # # self.timer.start(1000 * 60 * 60 * 12)  # tikrinti ryte ir vakare (kas 12 val)
        # # self.timer.start(10000)

        self.show()

#/////////////////////////////////////   MAIN WINDOW FUNKCIJOS   /////////////////////////////////////

    def get_project_numbers(self):
        project_numbers = []
        try:
            with pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path}') as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT DISTINCT projekto_nr FROM saskaitos")
                    rows = cursor.fetchall()
                    for row in rows:
                        project_numbers.append(str(row[0]))
        except Exception as e:
            print(f'Error in get_project_numbers: {e}')
        return project_numbers

    def filter_projects(self, text):
        try:
            with pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path}') as connection:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM saskaitos WHERE projekto_nr LIKE ? ORDER BY saskaitos_id DESC"
                    cursor.execute(query, (f"{text}%",))
                    rows = cursor.fetchall()
                    # print("Rows from filter_projects:", rows)

                    # atnaujinama lentelė su atrinktais rezultatais
                    self.update_invoice_table(rows)

        except Exception as e:
            print(f'Error in filter_projects: {e}')

    def get_names_of_suppliers(self):
        names_of_suppliers = []
        try:
            with pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path}') as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT DISTINCT tiekejas FROM saskaitos")
                    rows = cursor.fetchall()
                    for row in rows:
                        names_of_suppliers.append(row[0])
        except Exception as e:
            print(f'Error in get_names_of_suppliers: {e}')
        return names_of_suppliers

    def filter_suppliers(self, text):
        try:
            with pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path}') as connection:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM saskaitos WHERE LCase(tiekejas) LIKE LCase(?) ORDER BY saskaitos_id DESC"
                    cursor.execute(query, ('%'+text+'%',))  # pridedame '%' prie teksto, kad gautume visus tiekėjus, kurių pavadinimai prasideda įvestu tekstu
                    rows = cursor.fetchall()

                    # atnaujinama lentelė su atrinktais rezultatais
                    self.update_invoice_table(rows)
        except Exception as e:
            print(f'Error in filter_suppliers: {e}')
            raise

    def show_chosen_year(self, index):
        try:
            with pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path}') as connection:
                with connection.cursor() as cursor:
                    selected_year_text = self.years_combo.itemText(index)
                    if selected_year_text:
                        try:
                            selected_year = int(selected_year_text)

                            query = (f"SELECT * FROM saskaitos WHERE DatePart('yyyy', israsymo_data) = {selected_year} ORDER BY israsymo_data DESC")

                            cursor.execute(query)
                            rows = cursor.fetchall()
                            # print(rows)
                            self.update_table_after_filtering(rows)

                        except Exception as e:
                            print(f'Error in show_chosen_year: {str(e)}')

        except Exception as e:
            print(f'Error in show_chosen_year: {str(e)}')


    def show_chosen_quarter(self, index):
        try:
            with pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path}') as connection:
                with connection.cursor() as cursor:
                    if index == 0:
                        start_month, end_month = 1, 12
                    elif index == 1:
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

                        query = (f"SELECT * FROM saskaitos WHERE DatePart('m', israsymo_data) BETWEEN {start_month} AND {end_month}"
                                 f" AND DatePart ('yyyy', israsymo_data) = {selected_year} ORDER BY israsymo_data DESC")
                    else:
                        query = (f"SELECT * FROM saskaitos WHERE DatePart('m', israsymo_data) BETWEEN {start_month} AND {end_month} ORDER BY israsymo_data DESC")

                    cursor.execute(query)
                    rows = cursor.fetchall()
                    print(rows)

                    self.update_table_after_filtering(rows)
        except Exception as e:
            print(f'Error in show_chosen_quarter: {e}')


    def show_chosen_month(self, index):
        selected_month_text = self.months_combo.itemText(index)
        if selected_month_text:  # patikrinama, ar pasirinkta reikšmė nėra tuščia
            try:
                selected_month = int(selected_month_text)

                with pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path}') as connection:
                    with connection.cursor() as cursor:

                            query = (f"SELECT * FROM saskaitos WHERE DatePart('m', israsymo_data) = {selected_month} ORDER BY israsymo_data DESC")

                            cursor.execute(query)
                            rows = cursor.fetchall()

                            self.update_table_after_filtering(rows)

            except Exception as e:
                print(f'Error in show_chosen_month: {e}')

    def clean_up_filters(self):
        try:
            # išvalomas filtrų įvesties laukeliai
            self.projektoNr_input.clear()
            self.tiekejas_input.clear()

            # nustatomos tuščios reikšmės datų laukeliuose
            self.years_combo.setCurrentIndex(0)
            self.quarters_combo.setCurrentIndex(0)
            self.months_combo.setCurrentIndex(0)

            self.display_registry_of_invoices()

        except Exception as e:
            print(f'Error in clean_up_filters: {e}')

    def update_table_after_filtering(self, rows, today=None):  # filtravimas pagal datas
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
                       'Kada apmokėta', 'Apmokėta / Neapmokėta', 'Skubu', 'Pastabos']
            self.saskaitu_sarasas.setHorizontalHeaderLabels(headers)
            self.saskaitu_sarasas.horizontalHeader().setStyleSheet('QHeaderView::section { background-color: lightgrey}')

            # gaunama šios dienos data
            if today is None:
                today = date.today().strftime('%Y-%m-%d')

            for i, row in enumerate(rows):
                for j, item in enumerate(row):
                    if item is None:
                        item = ''  # None pakeičiamas tuščiu laukeliu

                    if j in [4, 5, 6]:  # 'Sąskaitos data', 'Apmokėti iki', 'Kada apmokėta' stuleplių indeksai
                        if item:  # patikrinama ar reikšmė nėra tuščias laukelis
                            if isinstance(item, date):  # patikrinama ar reikšmė yra data
                                item = datetime.strftime('%Y-%m-%d')  #
                        table_item = QTableWidgetItem(str(item))
                    else:
                        table_item = QTableWidgetItem(str(item))

                    # nuspalvinamos eilutės, jeigu atitinkamos sąlygos yra tenkinamos
                    if row[5] and isinstance(row[5], date) and (row[5].strftime('%Y-%m-%d') <= today or row[5] == '') and (row[7] == 'Neapmokėta' or row[8] == 'Skubu'):
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

    def update_invoice_table(self, rows, today=None):  # filtraviams pagal projekto numerius ir tiekėjus
        try:
            self.saskaitu_sarasas.setRowCount(len(rows))
            self.saskaitu_sarasas.setColumnCount(10)

            # lentelės stulpelių pavadinimai
            headers = ['Sąskaitos ID', 'Projekto numeris', 'Tiekėjas', 'Sąskaitos Nr.', 'Sąskaitos data', 'Apmokėti iki',
                        'Kada apmokėta', 'Apmokėta / Neapmokėta', 'Skubu', 'Pastabos']
            self.saskaitu_sarasas.setHorizontalHeaderLabels(headers)
            self.saskaitu_sarasas.horizontalHeader().setStyleSheet('QHeaderView::section { background-color: lightgrey}')

            # gaunama šios dienos data
            if today is None:
                today = datetime.today().strftime('%Y-%m-%d')

            for i, row in enumerate(rows):
                for j, item in enumerate(row):
                    if item is None:
                        item = ''  # None pakeičiamas tuščiu laukeliu
                    # print(rows)

                    if j in [4, 5, 6]:  # 'Sąskaitos data', 'Apmokėti iki', 'Kada apmokėta' stuleplių indeksai
                        if item:  # patikrinama ar reikšmė nėra tuščias laukelis
                            if isinstance(item, datetime):  # patikrinama ar reikšmė yra data
                                item = item.strftime('%Y-%m-%d')  # data paverčiama į tekstinę reikšmę
                            elif isinstance(item, date):  # patikrinama ar reikšmė yra tekstas
                                try:
                                    item = item.date().strftime('%Y-%m-%d')
                                except ValueError:
                                    pass
                        table_item = QTableWidgetItem(str(item))
                    else:
                        table_item = QTableWidgetItem(str(item))

                    # nuspalvinamos eilutės, jeigu atitinkamos sąlygos yra tenkinamos ('apmoketi_iki' == today ir 'neapmoketa' arba '')
                    if row[5] and isinstance(row[5], date) and (row[5].strftime('%Y-%m-%d') <= today or row[5] == '') and (row[7] == 'Neapmokėta' or row[8] == 'Skubu'):
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
            self.registrationDialog.setFixedSize(500, 600)

            self.registration_vLayout = QVBoxLayout(self.registrationDialog)  # pagrindinis vertikalus išdėstymas

            self.fLayout = QFormLayout()  # pildymo laukelių išdėstymas

            self.saskaitos_mygtukas = QPushButton('Neregistruotos sąskaitos')
            self.saskaitos_mygtukas.setFixedSize(200, 35)
            self.saskaitos_mygtukas.setStyleSheet("font-size: 12px;")
            self.saskaitos_mygtukas.clicked.connect(self.open_invoice_catalog)
            self.fLayout.addRow(QLabel('Pasirinkti sąskaitą ->'), self.saskaitos_mygtukas)

            self.projektoNr_field = QLineEdit()
            self.projektoNr_field.setStyleSheet("font-size: 12px;")
            self.projektoNr_field.setFixedSize(150, 30)
            self.projektoNr_field.textChanged.connect(self.convert_to_uppercase)

            # gaunami projektų numeriai iš esančių sąraše
            project_numbers = self.get_project_numbers()

            # sukuriamas QCompleter su projektų numerių sąrašu
            project_completer = QCompleter(project_numbers, self)
            project_completer.setCaseSensitivity(Qt.CaseInsensitive)

            # QCompleter susiejamas su QLineEdit (kad tikrintų, koks numeris rašomas ir pagal tai siūlytų galimus variantus)
            self.projektoNr_field.setCompleter(project_completer)
            self.fLayout.addRow(QLabel('Projekto numeris:'), self.projektoNr_field)

            # tiekėjo pavadinimo įvedimo laukelis
            self.tiekejas_field = QLineEdit()
            self.tiekejas_field.setStyleSheet("font-size: 12px;")
            self.tiekejas_field.setFixedSize(150, 30)

            # gaunami tiekėjų pavadinimai iš esančių sąraše
            supplier_names = self.get_names_of_suppliers()

            # sukuriamas QCompleter su žodžių sąrašu
            supplier_completer = QCompleter(supplier_names, self)
            supplier_completer.setCaseSensitivity(Qt.CaseInsensitive)

            # QCompleter susiejamas su QLineEdit (kad tikrintų, koks pavadinimas rašomas ir pagal tai siūlytų galimus variantus)
            self.tiekejas_field.setCompleter(supplier_completer)
            self.fLayout.addRow(QLabel('Pardavėjo pavadinimas:'), self.tiekejas_field)

            # sąskaitos numerio įvedimo laukelis
            self.saskaitosNr_field = QLineEdit()
            self.saskaitosNr_field.setStyleSheet("font-size: 12px;")
            self.saskaitosNr_field.setFixedSize(150, 30)
            self.saskaitosNr_field.textChanged.connect(self.convert_to_uppercase)
            self.fLayout.addRow(QLabel('Sąskaitos numeris:'), self.saskaitosNr_field)

            # sąskaitos datos pasirinkimas
            self.saskaitosData_field = QDateEdit()
            self.saskaitosData_field.setDisplayFormat("yyyy-MM-dd")
            self.saskaitosData_field.setCalendarPopup(True)  # iššokantis kalendoriukas
            self.saskaitosData_field.setDate(QDate.currentDate())  # nustatoma šiandienos data
            self.saskaitosData_field.setFixedSize(150, 30)
            self.saskaitosData_field.setFont(QFont("Arial", 9))
            self.fLayout.addRow(QLabel('Sąskaitos data:'), self.saskaitosData_field)

            # 'Apmokėti iki' laukelis su datos pasirinkimu
            self.apmoketiIki_field = QDateEdit()
            self.apmoketiIki_field.setDisplayFormat("yyyy-MM-dd")
            self.apmoketiIki_field.setCalendarPopup(True)
            self.apmoketiIki_field.setDate(QDate.currentDate())
            self.apmoketiIki_field.setFixedSize(150, 30)
            self.apmoketiIki_field.setFont(QFont("Arial", 9))
            self.fLayout.addRow(QLabel('Apmokėti iki:'), self.apmoketiIki_field)

            # apmokėjimo būsenos pasirinkimas
            self.busena = QComboBox()
            self.busena.addItems(["Neapmokėta", "Apmokėta"])
            self.busena.setFont(QFont("Arial", 9))
            self.busena.setFixedSize(150, 30)
            self.fLayout.addRow(QLabel('Sąskaitos būsena:'), self.busena)

            # apmokėjimo skubumo pasirinkimas
            self.skubumas = QComboBox()
            self.skubumas.addItem("")
            self.skubumas.addItem('Skubu')
            self.skubumas.setFont(QFont("Arial", 9))
            self.skubumas.setFixedSize(150, 30)
            self.fLayout.addRow(QLabel('Apmokėjimo skubumas:'), self.skubumas)

            # apmokėjimo datos laukelio ir pasirinkimo išdėstymas horizontaliai
            apmoketaLayout = QHBoxLayout()

            # 'Apmokėta (data):' etiketė
            self.apmokejimoData_label = QLabel('Apmokėta (data):')
            apmoketaLayout.addWidget(self.apmokejimoData_label)

            # įterpiamas tarpas tarp elementų
            spacer = QSpacerItem(5, 5, QSizePolicy.Expanding, QSizePolicy.Minimum)
            apmoketaLayout.addItem(spacer)

            # apmokejimo datos eilutė
            self.apmokejimoData_field = QLineEdit()
            self.apmokejimoData_field.setStyleSheet("font-size: 12px;")
            self.apmokejimoData_field.setFixedSize(155, 30)
            apmoketaLayout.addWidget(self.apmokejimoData_field)
            apmoketaLayout.addStretch()

            # kalendoriaus iškvietimas
            self.calendar_button = QPushButton('Pasirinkti datą')
            self.calendar_button.setFixedSize(150, 35)
            self.calendar_button.setStyleSheet("font-size: 12px;")
            self.calendar_button.clicked.connect(self.open_calendar)
            apmoketaLayout.addWidget(self.calendar_button)

            spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
            apmoketaLayout.addItem(spacer)

            self.fLayout.addRow(apmoketaLayout)

            # pastabų laukelis
            self.pastabos_field = QLineEdit()
            self.pastabos_field.setStyleSheet("font-size: 12px;")
            self.pastabos_field.setFixedSize(150, 30)
            self.fLayout.addRow(QLabel('Pastabos:'), self.pastabos_field)

            # pasirinkimas 'Patikrinti / Sutikrinta' prie pastabų
            self.sutikrinimas_combo = QComboBox()
            self.sutikrinimas_combo.setFixedSize(150, 30)
            self.sutikrinimas_combo.addItems(['Patikrinti', 'Sutikrinta'])
            self.sutikrinimas_combo.setFont(QFont("Arial", 9))
            self.sutikrinimas_combo.currentTextChanged.connect(self.update_pastabos_field)
            self.fLayout.addRow(QLabel('Patikrinti / Sutikrinta:'), self.sutikrinimas_combo)

            self.registration_vLayout.addLayout(self.fLayout)

            # sąskaitos registracijos patvirtinimo mygtuko sukūrimas
            self.insert_button = QPushButton("Užregistruoti gautą sąskaitą")
            self.insert_button.setFixedSize(200, 40)
            self.insert_button.setStyleSheet("font-size: 12px;")
            self.insert_button.clicked.connect(self.register_invoice_received)
            self.insert_button.clicked.connect(self.display_registry_of_invoices)

            # mygtuko centravimas
            self.h_layout = QHBoxLayout()  # horizontalus išdėstymas, kad eitų centruoti
            self.h_layout.addStretch()  # pridedamas tarpas prieš mygtuką
            self.h_layout.addWidget(self.insert_button)  # mygtuko pridėjimas prie išdėstymo
            self.h_layout.addStretch()  # pridedamas tarpas po mygtuko

            self.registration_vLayout.addSpacing(1)  # pridedamas tarpas
            self.registration_vLayout.addLayout(self.h_layout)  # h_layout išdėstymas pridedamas prie registration_vLayout išdėstymo
            self.registration_vLayout.addSpacing(60)  # pridedamas tarpas

            # nustatomas pagrindinis registrationDialog išdėstymas
            self.registrationDialog.setLayout(self.registration_vLayout)
            self.registrationDialog.show()  # iškviečiamas dialogo lango rodymas

        except Exception as e:
            print(f'Error in invoice_registration_form: {e}')

    def convert_to_uppercase(self):
        text = self.projektoNr_field.text()
        self.projektoNr_field.setText(text.upper())  # projekto numeris konvertuojamas į didžiąsias raides

    def open_invoice_catalog(self):  # neužregistruotų sąskaitų katalogas
        try:
            filename, _ =QFileDialog.getOpenFileName(None, "Pasirinkite sąskaitą",
                                                     "C:/Users/Raminta/OneDrive/Neregistruotos saskaitos", "PDF Files (*.pdf)")
            # filename, _ = QFileDialog.getOpenFileName(None, "Pasirinkite sąskaitą",
            #                                           "C:/Users/TetianaJonaitis/UAB Indasta/Indasta - Dokumentai/00_Buhalteriniai dokumentai/00_Neregistruotos sąskaitos",
            #                                           "PDF Files (*.pdf)")
            if filename:
                # priskiriamas kelias į self.current_pdf_path
                self.current_pdf_path = filename
                os.system(f'start "" "{filename}"')  # (f'start {filename}') nesuveikė, todėl reikėjo pridėti papildomas kabutes
            else:
                QMessageBox.warning(self, "Perspėjimas", "Nepasirinktas joks failas")

        except Exception as e:
            logging.error(f'Error in open_invoice_catalog: {str(e)}')
            print(f'Error in open_invoice_catalog: {str(e)}')


    def open_calendar(self):  # kalendoriaus atidarymas datos pasirinkimui
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

    def register_invoice_received(self):  # duomenų įkėlimas į duomenų bazę
        try:
            projekto_nr = self.projektoNr_field.text()
            tiekejas = self.tiekejas_field.text()
            saskaitos_nr = self.saskaitosNr_field.text()
            israsymo_data = self.saskaitosData_field.date().toString("yyyy-MM-dd")
            apmoketi_iki = self.apmoketiIki_field.date().toString("yyyy-MM-dd")

            # laukelis įrašyti datą, kada sąskaita buvo apmokėta
            apmokejimo_data = self.apmokejimoData_field.text()
            if apmokejimo_data == '':  # patikrinama, ar datos laukelis tuščias
                apmokejimo_data = None  # jei data neįvedama, duomenų bazės lentelėje bus įrašoma NULL reikšmė

            # apmokėjimo būsenos nustatymas
            apmoketa_ne = self.busena.currentText()

            skubu = self.skubumas.currentText()
            # sudengta = self.sudengta_combo.currentText()

            # pastabų laukelis
            pastabos = self.pastabos_field.text()
            if not pastabos:  # jeigu pastabos neįrašytos, bus rodoma NULL reikšmė
                pastabos = None

            with pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path}') as connection:
                with connection.cursor() as cursor:
                    # patikrinama, ar sąskaitos numeris jau yra sąskaitų registre
                    cursor.execute('SELECT * FROM saskaitos WHERE saskaitos_nr = ? AND tiekejas = ? ORDER BY saskaitos_id DESC', (saskaitos_nr, tiekejas,))
                    existing_invoice = cursor.fetchone()

                    if existing_invoice is not None:
                        QMessageBox.warning(self, 'Įspėjimas', 'Toks sąskaitos numeris jau yra sąskaitų registre')
                        return

                    else:
                         # jei sąskaitos numerio nėra, tęsiamas įrašymas
                        insert_query = """
                        INSERT INTO saskaitos (
                        projekto_nr,
                        tiekejas,
                        saskaitos_nr,
                        israsymo_data,
                        apmoketi_iki,
                        apmokejimo_data,
                        apmoketa_ne, 
                        skubu,                   
                        pastabos
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """

                        # duomenys įrašomi į duomenų bazę
                        cursor.execute(insert_query, (
                            projekto_nr,
                            tiekejas,
                            saskaitos_nr,
                            israsymo_data,
                            apmoketi_iki,
                            apmokejimo_data,
                            apmoketa_ne,
                            skubu,
                            pastabos
                        ))
                        # pakeitimai duomenų bazėje patvirtinami
                        connection.commit()

            QMessageBox.information(self, 'Information', 'Sąskaita sėkmingai įrašyta į duomenų bazę')

            self.registrationDialog.close()  # uždaromas sąskaitos suvedimo langas

            # iškviečiamas metodas pdf failui pervadinti ir perkelti į kitą direktoriją
            self.rename_and_move_invoice(israsymo_data, tiekejas, saskaitos_nr)

        except Exception as e:
            logging.error(f"Unexpected error in register_invoice_received: {str(e)}")
            print(f"Error from register_invoice_received: {e}")

    def rename_and_move_invoice(self, israsymo_data, tiekejas, saskaitos_nr):
        # patikrinama, ar yra atidarytas pdf failas
        if not hasattr(self, 'current_pdf_path') or not self.current_pdf_path:
            # vartotojas informuojamas, kad nėra atidaryto sąskaitos pdf failo
            QMessageBox.information(self, "Informacija", "Neatidarytas sąskaitos pdf failas")

        # priminimas, kad reikia uždaryti pdf failą
        QMessageBox.information(self, "Informacija", "Uždarykite sąskaitos PDF failą, kad būtų galima jį pervadinti ir perkelti!")

        # naujo pavadinimo pdf failui generavimas
        new_filename = f"{israsymo_data}_{tiekejas}_{saskaitos_nr}.pdf"

        # dinamiškai gaunamas OneDrive kelias iš aplinkos kintamojo
        onedrive_path = os.path.join(os.getenv('USERPROFILE'), 'OneDrive', 'Documents')  # nurodomas konkretus katalogas failams saugoti
        save_path = os.path.join(onedrive_path, new_filename)

        # dialogo lango atidarymas vartotojui pasirinkti vietą, kur išsaugoti pervadintą failą
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Pasirinkite vietą sąskaitai išsaugoti", save_path,
                                                   "PDF Files (*.pdf)", options=options)

        if file_path:
            # failas pervadinamas ir perkeliamas
            try:
                if hasattr(self, 'pdf_process') and self.pdf_process.poll() is None:
                    self.pdf_process.terminate()  ## uždaromas pdf failo procesas
                    self.pdf_process.wait()  # palaukiama, kol procesas bus visiškai uždarytas

                shutil.move(self.current_pdf_path, file_path)
                QMessageBox.information(self, "Informacija", f'Sąskaita pervadinta ir išsaugota: {file_path}')
            except Exception as e:
                # QMessageBox.critical(self, 'Klaida', f'Klaida pervadinant ir išsaugant failą: {str(e)}')
                print(f"Error in rename_and_move_invoice: {str(e)}")


    def display_registry_of_invoices(self):
        try:
            logging.info('Pradedamas duomenų įkėlimas')
            # QMessageBox.information(self, 'Informacija', 'Duomenų įkėlimas gali užtrukti keletą sekundžių')
            with (pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path}') as connection):
                with connection.cursor() as cursor:
                    cursor.execute("SELECT saskaitos_id, projekto_nr, tiekejas, saskaitos_nr, israsymo_data, "
                                   "apmoketi_iki, apmokejimo_data, apmoketa_ne, skubu, pastabos "
                                   "FROM saskaitos WHERE israsymo_data >= DATEADD('m', -2, DATE())"
                                   "ORDER BY saskaitos_id DESC")

                    rows = cursor.fetchall()
                    logging.info(f'Gauta {len(rows)} eilučių iš duomenų bazės')

                    self.saskaitu_sarasas.setRowCount(len(rows))
                    self.saskaitu_sarasas.setColumnCount(10)

                    # lentelės stulpelių pavadinimai
                    headers = ['Sąskaitos ID', 'Projekto numeris', 'Tiekėjas', 'Sąskaitos Nr.', 'Sąskaitos data',
                               'Apmokėti iki', 'Kada apmokėta', 'Apmokėta / Neapmokėta', 'Skubu', 'Pastabos']
                    self.saskaitu_sarasas.setHorizontalHeaderLabels(headers)
                    self.saskaitu_sarasas.horizontalHeader().setStyleSheet('QHeaderView::section { background-color: lightgrey}')

                    # gaunama šios dienos data
                    today = datetime.today().strftime('%Y-%m-%d')

                    for i, row in enumerate(rows):
                        for j, item in enumerate(row):
                            if item is None:
                                item = ''  # None pakeičiamas tuščiu laukeliu

                            if j in [4, 5, 6]:  # 'Išrašymo data', 'Apmokėti iki', 'Kada apmokėta' stuleplių indeksai
                                if isinstance(item, date):  # patikrinama ar reikšmė nėra tuščias laukelis ir yra data
                                    item = item.strftime('%Y-%m-%d')  # data paverčiama į tekstinę reikšmę
                                table_item = QTableWidgetItem(str(item))
                            else:
                                table_item = QTableWidgetItem(str(item))

                            # nuspalvinamos eilutės, jeigu atitinkamos sąlygos yra tenkinamos ('Apmokėti iki' <= today ir 'Neapmokėta' arba 'Skubu')
                            if row[7] == 'Apmokėta':
                                table_item.setBackground(QColor(144, 238, 144))  # šviesiai žalia spalva

                            elif row[5] and isinstance(row[5], date) and (row[5].strftime('%Y-%m-%d') <= today or row[5] == '') and (row[7] == 'Neapmokėta' or row[8] == 'Skubu'):
                                table_item.setBackground(QColor(255, 0, 0))  # raudona spalva

                            try:
                                self.saskaitu_sarasas.setItem(i, j, table_item)
                                self.saskaitu_sarasas.resizeColumnToContents(j)
                            except Exception as e:
                                print(f'Error in display_registry_of_invoices.setItem(i, j, table_item): {e}')

                    connection.commit()

            # pridedamas pranešimo rodymas užvedus pele ant sąskaitos numerio celės
            for row in range(self.saskaitu_sarasas.rowCount()):
                item = self.saskaitu_sarasas.item(row, 3)  # sąskaitos numerio stulpelio indeksas
                if item:
                    item.setToolTip("Spustelėkite, kad peržiūrėtumėte sąskaitą")

            self.saskaitu_sarasas.show()

        except Exception as e:
            logging.error(f'Klaida display_registry_of_invoices metode: {e}')
            print(f"Error from display_registry_of_invoices: {e}")

    def invoice_payment_confirmation(self):
        try:
            current_row = self.saskaitu_sarasas.currentRow()
            if current_row >= 0:
                self.apmokejimo_busena_changed(current_row, "Apmokėta", datetime.today().strftime('%Y-%m-%d'))
        except Exception as e:
            print(f"Error from invoice_payment_confirmation: {e}")

    def apmokejimo_busena_changed(self, row, new_payment_status, payment_date):
        # gaunamas sąskaitos numeris iš pasirinktos eilutės
        invoice_number_item = self.saskaitu_sarasas.item(row, 3)
        invoice_number = invoice_number_item.text()
        try:
            with pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path}') as connection:
                with connection.cursor() as cursor:
                    # pasirenkama, kurių stulpelių reikšmės bus atnaujintos
                    update_query = """
                      UPDATE saskaitos SET
                      apmoketa_ne = ?,
                      apmokejimo_data = ?,
                      skubu = ''
                      WHERE saskaitos_nr = ?
                      """

                    cursor.execute(update_query, (new_payment_status, payment_date, invoice_number))
                    connection.commit()

                    QMessageBox.information(self, "Informacija", "Sėkmingai atnaujinta apmokėjimo būsena ir apmokėjimo data", QMessageBox.Ok)

                    self.display_registry_of_invoices()

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

            self.update_record_window.show()  # įrašo koregavimo lango iškvietimas

        except Exception as e:
            print(f"Error from update_record_button_clicked: {e}")

    def get_current_record(self):
        try:
            # pažymėtos eilutės identifikavimas
            current_row = self.saskaitu_sarasas.currentRow()

            # gaunami duomenys iš lentelės
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
            print(f"Error from get_current_record: {e}")
            return []

    def update_database(self, updated_projekto_numeris, updated_tiekejo_pavadinimas, updated_saskaitos_nr, updated_saskaitos_data,
                        updated_apmoketi_iki, updated_apmokejimo_data, updated_apmokejimo_busena, updated_apmokejimo_skubumas, updated_pastabos, record_id):
        try:
            # sukuriamos naujos reikšmės
            new_values = (updated_projekto_numeris, updated_tiekejo_pavadinimas, updated_saskaitos_nr, updated_saskaitos_data,
                        updated_apmoketi_iki, updated_apmokejimo_data, updated_apmokejimo_busena, updated_apmokejimo_skubumas, updated_pastabos, record_id)
            print(f'New values: {new_values}')
            self.confirm_update(record_id, new_values)

        except Exception as e:
            print(f"Error from update_database: {e}")

    def confirm_update(self, record_id, new_values):
        try:
            logging.debug("Starting confirm_update function")
            if record_id and record_id.isdigit():
                logging.debug(f"Connecting to database: {db_path}")

                with pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path}') as connection:
                    with connection.cursor() as cursor:

                        try:
                            # tuščios reikšmės konvertuojamos į 'None' datos laukeliuose
                            new_values = list(new_values)
                            updated_apmokejimo_data = 5
                            if new_values[updated_apmokejimo_data] == '':
                                new_values[updated_apmokejimo_data] = None
                            else:
                                try:
                                    new_values[updated_apmokejimo_data] = datetime.strptime(new_values[updated_apmokejimo_data], '%Y-%m-%d').date()
                                except ValueError:
                                    print(f"Netinkamas datos formatas: {type(new_values[updated_apmokejimo_data])}")
                                    print("new_values[updated_apmokejimo_data]:", new_values[updated_apmokejimo_data])
                                    logging.error(f"Invalid date format: {new_values[updated_apmokejimo_data]}")
                                    return

                            update_query = """
                            UPDATE saskaitos SET
                            projekto_nr = ?,
                            tiekejas = ?,
                            saskaitos_nr = ?,
                            israsymo_data = ?,
                            apmoketi_iki = ?,       
                            apmokejimo_data = ?,
                            apmoketa_ne = ?,
                            skubu = ?,
                            pastabos = ?
                            WHERE saskaitos_id = ?
                            """

                            cursor.execute(update_query, new_values)
                            connection.commit()

                            # pranešimas apie atnaujintą įrašą
                            QMessageBox.information(self, "Information", f"Įrašas sėkmingai atnaujintas", QMessageBox.Ok)

                            # self.display_registry_of_invoices()

                        except pyodbc.Error as e:
                            logging.error(f"Klaida vykdant SQL užklausą: {str(e)}")
                            QMessageBox.critical(self, "Error", f"Klaida atnaujinant įrašą: {str(e)}")

        except Exception as e:
            logging.error(f"Error in confirm_update: Nežinoma klaida - {e}")
            QMessageBox.critical(self, "Klaida", f'Nežinoma klaida: {e}', QMessageBox.Ok)

    def delete_record(self):
        try:
            # prašymas patvirtinti įrašo ištrynimą
            reply = QMessageBox.question(self, "Patvirtinimas", "Ar jūs tikrai norite ištrinti įrašą?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:  # jei patvirtinamas ištrynimas

                # pažymėtos eilutės identifikavimas
                current_row = self.saskaitu_sarasas.currentRow()

                # gaunamas įrašo id iš lentelės
                record_id = self.saskaitu_sarasas.item(current_row, 0)
                if record_id is not None:
                    record_id = record_id.text()

                # prisijungiam prie duomenų bazės
                with pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path}') as connection:
                    with connection.cursor() as cursor:
                        delete_query = "DELETE FROM saskaitos WHERE saskaitos_id = ?"

                        cursor.execute(delete_query, (record_id,))
                        connection.commit()

                self.saskaitu_sarasas.removeRow(current_row)  # ištrinamas pažymėtas lentelės įrašas
                QMessageBox.information(self, 'Informacija', 'Įrašas sėkmingai ištrintas iš duomenų bazės')

            else:
                # jei nepatvirtinamas ištrynimas, nieko nedaroma
                pass

        except Exception as e:
            print(f'Trinant įrašą kilo problema: {str(e)}')


    def check_for_new_file(self):  # metodas naujų failų paieškai skenuotų sąskaitų kataloge
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
            self.invoice_dialog()

        except Exception as e:
            print(f"Error from create_invoice: {str(e)}")

    def check_invoices_due_date(self):
        try:
            logging.info('Fetching and displaying overdue invoices')

            with pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path}') as connection:
                with connection.cursor() as cursor:
                    # today = date.today().strftime('%Y-%m-%d')  # gaunama šios dienos data
                    today = datetime.today().date()

                    # atrenkami įrašai, kur apmokėjimo data mažesnė už arba lygi šiandienai arba yra tuščia ir yra 'Neapmokėta' arba 'Skubu'
                    query = "SELECT * FROM saskaitos"
                    cursor.execute(query)
                    # cursor.execute(query, (today,))
                    rows = cursor.fetchall()

                    filtered_rows = []
                    for row in rows:
                        apmoketi_iki = row[5]
                        apmoketa_ne = row[7]
                        skubu = row[8]

                        if isinstance(apmoketi_iki, datetime):
                            apmoketi_iki = apmoketi_iki.date()

                        condition_1 = apmoketi_iki and apmoketi_iki <= today and apmoketa_ne == 'Neapmokėta' and skubu == 'Skubu'
                        condition_2 = apmoketi_iki and apmoketi_iki <= today and apmoketa_ne == 'Neapmokėta' and skubu == ''
                        condition_3 = apmoketi_iki and apmoketi_iki <= today and apmoketa_ne == '' and skubu == 'Skubu'
                        condition_4 = (apmoketi_iki is None or apmoketi_iki == '') and apmoketa_ne == 'Neapmokėta' and skubu == 'Skubu'
                        condition_5 = (apmoketi_iki is None or apmoketi_iki == '') and apmoketa_ne == 'Neapmokėta' and skubu == ''

                        if condition_1 or condition_2 or condition_3 or condition_4 or condition_5:
                            filtered_rows.append(row)
                            print(filtered_rows)

                    if not filtered_rows:  # jeigu nėra apmokėtinų sąskaitų
                        QMessageBox.information(self, 'Informacija', 'Apmokėtinų sąskaitų šiai dienai nėra')
                        return

                    self.saskaitu_sarasas.setRowCount(len(filtered_rows))
                    self.saskaitu_sarasas.setColumnCount(10)

                    headers = ['Įrašo Nr.', 'Projekto Nr.', 'Tiekėjas', 'Sąskaitos Nr.', 'Sąskaitos data', 'Apmokėti iki',
                               'Kada apmokėta', 'Apmokėta / Neapmokėta', 'Skubu', 'Pastabos']
                    self.saskaitu_sarasas.setHorizontalHeaderLabels(headers)
                    self.saskaitu_sarasas.horizontalHeader().setStyleSheet('QHeaderView::section {background-color: lightgrey}')

                    for i, row in enumerate(filtered_rows):
                        for j, item in enumerate(row):
                            if item is None:
                                item = ''
                            elif isinstance(item, datetime):
                                item = item.date()  # gaunama tik data iš datetime objekto

                            # atrinktų įrašų eilutės nuspalvinamos raudonai
                            table_item = QTableWidgetItem(str(item))
                            self.saskaitu_sarasas.setItem(i, j, table_item)
                            self.saskaitu_sarasas.resizeColumnToContents(j)
                            table_item.setBackground(QColor(255, 0, 0))

                    connection.commit()

            self.saskaitu_sarasas.show()

            logging.info('Displaying overdue invoices completed')

        except Exception as e:
            print(f'Gaunant ir pateikiant sąskaitas įvyko klaida: {str(e)}')
            logging.error(f'Error in check_invoices_due_date: {str(e)}')


    def on_invoiceNo_clicked(self, row, column):
        if column == 3:  # jei pasirenkamas 'Sąskaitos Nr.' stulpelio įrašas

            saskaitos_nr = self.saskaitu_sarasas.item(row, 3).text()  # išgaunamas sąskaitos numeris iš paspausto stulpelio
            israsymo_data = self.saskaitu_sarasas.item(row, 4).text()  # išgaunama sąskaitos išrašymo data

            # iškviečiamas failo atidarymo metodas
            self.open_invoice(israsymo_data, saskaitos_nr)


    def open_invoice(self, israsymo_data, saskaitos_nr):
        try:
            # pagrindinis katalogas, kuriame ieškomi failai
            # base_dir = "C:/Users/TetianaJonaitis/UAB Indasta/Indasta - Dokumentai"
            base_dir = "C:/Users/Raminta/OneDrive/Dokumentai"

            # sukuriamas regex šablonas: sąskaitos data priekyje ir numeris pabaigoje
            search_pattern = re.compile(f"^{re.escape(israsymo_data)}.*{re.escape(saskaitos_nr)}.pdf$")

            # sukuriamas sąrašas failų, atitinkančių paieškos šabloną
            matching_files = []

            # naudojama os.walk funkcija pereiti visus katalogus ir poaplankius
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    # jeigu failas atitinka paieškos šabloną
                     if search_pattern.match(file):
                        matching_files.append(os.path.join(root, file))  # failas prijungiamas prie matching_files sąrašo

            # patikrinama, ar unikalus failas egzistuoja matching_files sąraše
            if matching_files:
                # failai rūšiuojami pagal jų modifikavimo datą (nuo naujausio iki seniausio)
                matching_files.sort(key=os.path.getmtime, reverse=True)

                filename = matching_files[0]  # jei rastas daugiau nei vienas failas, pasirenkamas pirmasis
                os.system(f'start "" "{filename}"')  # atidaromas failas
                print(f'Filename: {filename}')
            else:
                QMessageBox.warning(self, "Perspėjimas", "Failas nerastas")

        except Exception as e:
            print(f"Error in open_invoice: {str(e)}")



    def on_projectNo_clicked(self, row, column):
        if column == 1:  # jei pasirenkamas projekto_nr stulpelio įrašas
            projekto_nr = self.saskaitu_sarasas.item(row, 1).text()  # išgaunamas projekto numeris iš paspausto įrašo

            # iškviečiamas projekto katalogo atidarymo metodas
            self.open_project_directory(projekto_nr)


    def open_project_directory(self, projekto_nr):
        try:
            # pagrindinis katalogas, kuriame ieškomi failai
            # path = "C:/Users/TetianaJonaitis/UAB Indasta/Indasta - Dokumentai"
            path = f"C:/Users/Raminta/OneDrive/Dokumentai/{projekto_nr}/Saskaitos"

            # patikrinama, ar katalogas egzistuoja
            if os.path.exists(path):
                # atidaromas nurodytas projekto katalogas
                os.system(f'start "" "{path}"')
                print(f"Projekto {projekto_nr} katalogas atidarytas")
            else:
                QMessageBox.warning(self, "Klaida", "Katalogas nerastas")

        except Exception as e:
            print(f"Error in open_project_directory: {str(e)}")


    def on_export_button_clicked(self):  # eksportavimas į Excel failą
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, 'Išsaugoti kaip', "", "Excel Files (*.xlsx);;All Files (*)", options=options)

        if filename:
            # pašalinama failų filtrų dalis, jei ji yra failo pavadinime
            if ' (*.xlsx)' in filename:
                filename = filename.replace(' (*.xlsx)', '')
            elif ';;All Files (*)' in filename:
                filename = filename.replace(';;All Files (*)', '')

            # užtikriname, kad failo pavadinimas baigtųsi .xlsx plėtiniu
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'

            self.export_to_excel(filename)

    def export_to_excel(self, filename):
        try:
            # sukuriamas naujas excel failas
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet()

            # sukuriami formatavimo objektai
            red_format = workbook.add_format({'bg_color': '#ff0000'})
            green_format = workbook.add_format({'bg_color': '#90EE90'})

            # nuskaitomi stulpelių pavadinimai ir įrašomi su formatavimu
            for column in range(self.saskaitu_sarasas.columnCount()):
                header = self.saskaitu_sarasas.horizontalHeaderItem(column).text()
                worksheet.write(0, column, header)

            # nustatomas stulpelių plotis pagal QTableWidget stulpelių plotį
            for column in range(self.saskaitu_sarasas.columnCount()):
                worksheet.set_column(column, column, self.saskaitu_sarasas.columnWidth(column) / 10)  # dalijama iš 10, nes Excel ir Qt matavimo vienetai skiriasi

            # nustatomas eilučių aukštis pagal QTableWidget eilučių aukštį
            default_height = 15
            for row in range(self.saskaitu_sarasas.rowCount()):
                worksheet.set_row(row + 1, default_height)

            # nuskaitomi ir įrašomi duomenys iš kiekvienos eilutės ir stulpelio
            for row in range(self.saskaitu_sarasas.rowCount()):
                for column in range(self.saskaitu_sarasas.columnCount()):
                    item = self.saskaitu_sarasas.item(row, column)
                    if item is not None:
                        # tikrinama celės spalva ir taikomas formatavimas
                        if item.background().color().name() == '#ff0000':
                            worksheet.write(row + 1, column, item.text(), red_format)
                        elif item.background().color().name() == QColor(144, 238, 144):
                            worksheet.write(row + 1, column, item.text(), green_format)
                        else:
                            worksheet.write(row + 1, column, item.text())

            workbook.close()
        except Exception as e:
            print(f'Klaida eksportuojant į Excel: {e}')



############################################

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

