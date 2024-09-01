import sys
import os
import locale
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PyQt5.QtWidgets import *
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
from PyQt5.QtCore import QDate, Qt, QSize
from num2words import num2words
from PyQt5.QtGui import QFont, QFontMetrics
import subprocess



class CreationOfInvoice(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sąskaitų išrašymo langas")
        self.setGeometry(500, 50, 1250, 770)

        self.vLayout = QVBoxLayout(self)

        self.laukeliu_hLayout = QHBoxLayout()
        # laukelių išdėstymo horizontaliame išdėstyme forma
        self.formLayout1 = QFormLayout()  # sąskaitos duomenų suvedimo laukelių išdėstymas
        self.formLayout2 = QFormLayout()  # datų ir išrašiusio asmens pasirinkimo išdėstymas

        # sąskaitos numerio suvedimo laukelis, jo pavadinimas ir dydis
        self.saskaitosNr_label = QLabel('Sąskaitos numeris:')
        self.saskaitosNr_label.setFont(QFont("Arial", 10))

        self.saskaitos_numeris = QLineEdit()
        self.saskaitos_numeris.setFixedSize(250, 30)
        self.formLayout1.addRow(self.saskaitosNr_label, self.saskaitos_numeris)

        # projekto numerio suvedimo laukelis, jo pavadinimas ir dydis
        self.projektoNr_label = QLabel('Projekto numeris:')
        self.projektoNr_label.setFont(QFont("Arial", 10))

        self.projekto_nr = QLineEdit()
        self.projekto_nr.setStyleSheet("font-size: 12px; text-transform: uppercase;")
        self.projekto_nr.setFixedSize(250, 30)
        self.projekto_nr.textChanged.connect(self.convert_to_uppercase)
        self.formLayout1.addRow(self.projektoNr_label, self.projekto_nr)

        # pirkėjo pavadinimo suvedimo laukelis, jo pavadinimas ir dydis
        self.pirkejas_label = QLabel('Pirkėjo pavadinimas: ')
        self.pirkejas_label.setFont(QFont("Arial", 10))

        self.pirkejas = QLineEdit()
        self.pirkejas.setFixedSize(250, 30)
        self.formLayout1.addRow(self.pirkejas_label, self.pirkejas)

        # įmonės kodo suvedimo laukelis, jo pavadinimas ir dydis
        self.imones_kodas_label = QLabel('Įmonės kodas:')
        self.imones_kodas_label.setFont(QFont("Arial", 10))

        self.imones_kodas = QLineEdit()
        self.imones_kodas.setFixedSize(250, 30)
        self.formLayout1.addRow(self.imones_kodas_label, self.imones_kodas)

        # PVM kodo suvedimo laukelis, jo pavadinimas ir dydis
        self.PVMkodo_label = QLabel('PVM kodas: ')
        self.PVMkodo_label.setFont(QFont("Arial", 10))

        self.PVM_kodas = QLineEdit()
        self.PVM_kodas.setStyleSheet("font-size: 12px; text-transform: uppercase;")
        self.PVM_kodas.textChanged.connect(self.convert_to_uppercase)
        self.PVM_kodas.setFixedSize(250, 30)
        self.formLayout1.addRow(self.PVMkodo_label, self.PVM_kodas)

        # pirkėjo adreso suvedimo laukelis, jo pavadinimas ir dydis
        self.pirkejo_adresas_label = QLabel('Pirkėjo adresas')
        self.pirkejo_adresas_label.setFont(QFont("Arial", 10))

        self.pirkejo_adresas = QLineEdit()
        self.pirkejo_adresas.setFixedSize(250, 30)
        self.formLayout1.addRow(self.pirkejo_adresas_label, self.pirkejo_adresas)

        self.laukeliu_hLayout.addLayout(self.formLayout1)
        self.laukeliu_hLayout.addStretch(5)

        # išrašomo dokumento datos nustatymas
        self.data_label = QLabel('Dokumento data: ')
        self.data_label.setStyleSheet("font-family: Arial; font-size: 10pt")

        self.dok_data = QDateEdit()
        self.dok_data.setDisplayFormat("yyyy-MM-dd")
        self.dok_data.setCalendarPopup(True)  # įjungia iššokantį kalendoriaus langelį
        self.dok_data.setDate(QDate.currentDate())  # nustatoma esamoji data
        self.dok_data.setFixedSize(350, 30)
        self.dok_data.setFont(QFont("Arial", 9))
        self.dok_data.setFixedWidth(110)  # nustato fiksuotą eilutės plotį
        self.formLayout2.addRow(self.data_label, self.dok_data)

        # išrašomo dokumento apmokėjimo datos nustatymas
        self.apmoketi_iki_label = QLabel('Apmoketi iki: ')
        self.apmoketi_iki_label.setStyleSheet("font-family: Arial; font-size: 10pt")

        self.apmoketi_iki = QDateEdit()
        self.apmoketi_iki.setDisplayFormat("yyyy-MM-dd")
        self.apmoketi_iki.setCalendarPopup(True)
        self.apmoketi_iki.setDate(QDate.currentDate())
        self.apmoketi_iki.setFixedSize(350, 30)
        self.apmoketi_iki.setFont(QFont("Arial", 9))
        self.apmoketi_iki.setFixedWidth(110)  # nustato fiksuotą eilutės plotį
        self.formLayout2.addRow(self.apmoketi_iki_label, self.apmoketi_iki)

        # sąskaitą išrašiusio asmens pasirinkimo laukelis
        self.israse_label = QLabel('Sąskaitą išrašė: ')
        self.israse_label.setStyleSheet("font-family: Arial; font-size: 10pt")

        self.kas_israse = QComboBox()
        self.kas_israse.setFixedSize(250, 30)
        self.kas_israse.addItems(['Statybos direktorius Vaidotas Pocius', 'Direktorius Darius Mažeika'])
        self.formLayout2.addRow(self.israse_label, self.kas_israse)

        self.laukeliu_hLayout.addLayout(self.formLayout2)
        self.laukeliu_hLayout.addStretch(30)  # pridedamas tarpas laukeliu_hLayout išdėstyme

        # išdėstymo naujų sąskaitų išrašymo mygtukui sukūrimas
        self.formLayout3 = QFormLayout()

        # naujos sąskaitos išrašymo mygtukas
        self.new_invoice_button = QPushButton('Išrašyti kitą sąskaitą')
        self.new_invoice_button.setFixedSize(250, 50)
        self.new_invoice_button.clicked.connect(self.new_invoice_clicked)
        self.new_invoice_button.setStyleSheet("background-color: #89cff0; font-size: 10pt;")
        self.formLayout3.addWidget(self.new_invoice_button)  # mygtukas pirdedamas prie horizontalaus išdėstymo

        self.laukeliu_hLayout.addLayout(self.formLayout3)  # mygtukas pridedamas prie atitinkamo išdėstymo
        self.laukeliu_hLayout.addStretch(20)

        self.vLayout.addLayout(self.laukeliu_hLayout)
        self.vLayout.addSpacing(40)

        # laukeliai duomenų įrašymui į atliktų darbų ar suteiktų paslaugų lentelę
        # eilės numeris
        self.line_edit1 = QLineEdit()
        self.line_edit1.setReadOnly(True)  # nustatoma, kad laukelis nebūtų koreguojamas
        self.line_edit1.setFixedSize(50, 30)
        self.line_edit1.setText('1')  # automatinis įrašo numerio pridėjimas

        # atliktų darbų pavadinimas
        self.line_edit2 = QLineEdit()
        self.line_edit2.setFixedSize(900, 30)

        # mato vienetai
        self.combo_box = QComboBox()
        self.combo_box.setFixedSize(75, 30)
        self.combo_box.addItems(["Kompl.", "Vnt."])

        # kiekis
        self.line_edit4 = QLineEdit()
        self.line_edit4.setFixedSize(60, 30)

        # vnt. kaina
        self.line_edit5 = QLineEdit()
        self.line_edit5.setFixedSize(100, 30)

        # atliktų darbų lentelės laukelių pildymo formų išdėstymas
        self.lent_pildymo_lauk_layout = QGridLayout()  # pildymo laukelių išdėstymas gardelėmis

        # laukelių pavadinimų ir laukelių pozicijų nustatymas gardelėse
        self.lent_pildymo_lauk_layout.addWidget(QLabel('Eil. Nr.:'), 0, 0)
        self.lent_pildymo_lauk_layout.addWidget(self.line_edit1, 1, 0)
        self.lent_pildymo_lauk_layout.addWidget(QLabel('Atliktų darbų pavadinimas'), 0, 1)
        self.lent_pildymo_lauk_layout.addWidget(self.line_edit2, 1, 1)
        self.lent_pildymo_lauk_layout.addWidget(QLabel('Mato vnt.'), 0, 2)
        self.lent_pildymo_lauk_layout.addWidget(self.combo_box, 1, 2)
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

        # sukuriami kintamieji sumoms po lentele saugoti
        self.suma_viso = ""
        self.pvm = ""
        self.suma_suPVM = ""
        self.moketina_suma = ""

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
        self.suma_suPVM_line_edit.setReadOnly(True)
        self.sumu_fLayout.addRow(self.suma_suPVM, self.suma_suPVM_line_edit)

        self.moketina_suma = QLabel('Mokėtina suma, Eur')
        self.moketina_suma_line_edit = QLineEdit()
        self.moketina_suma_line_edit.setReadOnly(True)
        self.sumu_fLayout.addRow(self.moketina_suma, self.moketina_suma_line_edit)

        # sumų eilučių pridėjimas prie PVM eilutės išdėstymo ir pastarosios pridėjimas prie pagrindinio išdėstymo
        self.PVM_hLayout.addLayout(self.sumu_fLayout)
        self.vLayout.addLayout(self.PVM_hLayout)

        # sąskaitos mygtuko horizontalus išdėstymas, kad eitų centruoti
        self.invoice_button_layout = QHBoxLayout()

        # sąskaitos sukūrimo mygtukas
        self.create_invoice_button = QPushButton('Sukurti sąskaitą')
        self.create_invoice_button.setFixedSize(250, 50)
        self.create_invoice_button.clicked.connect(self.create_invoice_clicked)
        self.create_invoice_button.setStyleSheet("background-color: #a4c639; font-size: 10pt;")
        self.invoice_button_layout.addWidget(self.create_invoice_button)  # mygtukas pirdedamas prie horizontalaus išdėstymo

        self.invoice_button_layout.addStretch()

        self.vLayout.addLayout(self.invoice_button_layout)  # horizontalus išdėstymas patalpinamas pagrindiniame išdėstyme

        self.setLayout(self.vLayout)

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\   METODAI   //////////////////////////////////////////////////

    def convert_to_uppercase(self):
        projektoNr_text = self.projekto_nr.text()
        PVM_kodas_text = self.PVM_kodas.text()

        if projektoNr_text:
            self.projekto_nr.setText(projektoNr_text.upper())  # projekto numeris konvertuojamas į didžiąsias raides
        elif PVM_kodas_text:
            self.PVM_kodas.setText(PVM_kodas_text.upper())  # PVM kodas konvertuojamas į didžiąsias raides

    def sukurti_lentele(self):
        try:
            self.darbu_lentele = QTableWidget(self)
            self.darbu_lentele.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.darbu_lentele.setRowCount(0)  # nustatome norimą eilučių skaičių
            self.darbu_lentele.setColumnCount(6)  # nustatome norimą stulpelių skaičių
            self.darbu_lentele.setHorizontalHeaderLabels(["Eil. Nr.", "Atliktų darbų pavadinimas", "Mato vnt.", "Kiekis",
                                                          "Vnt. kaina", "Suma, €"])  # stulpelių antraštės

            # lentelės dydis keičiasi pagal turinio dydį
            self.darbu_lentele.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.darbu_lentele.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            # nustatomi minimalūs darbu_lentele lentelės dydžiai
            self.darbu_lentele.setMinimumSize(600, 380)

            #  nustatoma galimybė taisyti įrašus tiesiogiai lentelėje
            self.darbu_lentele.setEditTriggers(QTableWidget.AllEditTriggers)

            self.darbu_lentele.cellChanged.connect(self.suskaiciuoti_suma)  # suskaičiuoja paskutinio stulpelio reikšmę pagal 3 ir 4 stulpelių reikšmių sandaugą
            self.darbu_lentele.itemChanged.connect(self.atnaujinti_sumas)  # jeigu padaugėja duomenų lentelėje, sumų eilutėse pasikeičia sumos
            self.darbu_lentele.itemChanged.connect(self.atnaujinti_sumas_po_istrynimo)  # jeigu ištrinama lentelės eilutė, perskaičiuojamos sumos sumų eilutėse
            self.vLayout.addWidget(self.darbu_lentele)  # lentelė pridedama prie išdėstymo

            # horizontalus išdėstymas mygtukams
            self.hLayout = QHBoxLayout()

            # mygtukas įrašų pridėjimui į lentelę
            fill_table_button = QPushButton('Atnaujinti lentelę', self)
            fill_table_button.setFixedSize(250, 40)
            self.hLayout.addWidget(fill_table_button)  # mygtuko pridėjimas prie išdėstymo

            # metodas atnaujinti_lentele iškviečiamas paspaudus 'Enter'
            fill_table_button.setAutoDefault(True)
            fill_table_button.setDefault(True)
            fill_table_button.clicked.connect(self.atnaujinti_lentele)

            # mygtukas įrašo ištrynimui iš lentelės
            delete_record_button = QPushButton('Ištrinti įrašą', self)
            delete_record_button.setFixedSize(250, 40)
            delete_record_button.clicked.connect(self.delete_table_record)
            self.hLayout.addWidget(delete_record_button)  # mygtuko pridėjimas prie išdėstymo

            self.hLayout.addStretch(10)

            self.vLayout.addLayout(self.hLayout)

        except Exception as e:
            print(f'Error in sukurti_lentele: {e}')


    def atnaujinti_lentele(self):
        try:
            # patikrinama, ar visi laukeliai yra užpildyti
            if not all([self.line_edit1.text(), self.line_edit2.text(), self.line_edit4.text(), self.line_edit5.text()]):
                QMessageBox.warning(self, 'Perspėjimas', "Neužpildyti visi laukeliai")
                return

            # paimamas tekstas iš QLineEdit laukelių
            eil_nr = str(self.darbu_lentele.rowCount() + 1)  # nustatomas naujas Eil. Nr.
            darbu_pavadinimas = self.line_edit2.text()
            mato_vnt = self.combo_box.currentText()
            kiekis = self.line_edit4.text().replace(' ', '').replace(',', '.')
            vnt_kaina = self.line_edit5.text().replace(' ', '').replace(',', '.')

            kiekis_float = float(kiekis)
            vnt_kaina_float = float(vnt_kaina)
            # print('atnaujinti_lentele vnt_kaina_float: ', vnt_kaina_float, '\n kiekis_float: ', kiekis_float)

            # nustatoma lokalė
            locale.setlocale(locale.LC_ALL, '')

            # formatuojama vnt_kaina su tarpais
            formatted_vnt_kaina = locale.format_string("%.2f", vnt_kaina_float, grouping=True)
            formatted_vnt_kaina = formatted_vnt_kaina.replace(',', ' ').replace('.', ',')

            # formatuojamas kiekis su dešimtainėmis dalimis
            formatted_kiekis = locale.format_string("%.2f", kiekis_float, grouping=True)
            formatted_kiekis = formatted_kiekis.replace(',', ' ').replace('.', ',')
            # print('atnaujinti_lentele formatted_vnt_kaina: ', formatted_vnt_kaina)
            # print('atnaujinti_lentele formatted_kiekis: ', formatted_kiekis)

            # sukuriama nauja lentelės eilutė su gautu tekstu
            row = [eil_nr, darbu_pavadinimas, mato_vnt, formatted_kiekis, formatted_vnt_kaina]


            # eilutė pridedama prie lentelės
            self.darbu_lentele.insertRow(self.darbu_lentele.rowCount())
            for i, text in enumerate(row):
                if i == 1:
                    label = QLabel(text)
                    label.setWordWrap(True)
                    label.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # nustatomas teksto lygiavimas
                    self.darbu_lentele.setCellWidget(self.darbu_lentele.rowCount() - 1, i, label)
                else:
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                    self.darbu_lentele.setItem(self.darbu_lentele.rowCount() - 1, i, item)

            # Išvalomi QLineEdit laukeliai, kad eitų vesti kitus duomenis
            self.line_edit1.setText(eil_nr)
            self.line_edit2.clear()
            self.combo_box.setCurrentIndex(0)  # nustatoma pradinė reikšmė combo laukelyje
            self.line_edit4.clear()
            self.line_edit5.clear()

            self.line_edit2.setFocus()

        except Exception as e:
            print(f"Error in 'atnaujinti_lentele': {e}")


    def keyPressEvent(self, event):  # kad užpildytų 'darbu_lentele' lentelę paspaudus Enter klavišą
        if event.key() == Qt.Key_Return:
            self.atnaujinti_lentele()


    def suskaiciuoti_suma(self, row, column):  # esančią darbu_lentele paskutiniame stulpelyje
        try:
            if column in (3, 4):
                # gauname 4 ir 5 stulpelio reikšmes
                kiekis_item = self.darbu_lentele.item(row, 3)
                vnt_kaina_item = self.darbu_lentele.item(row, 4)

                if kiekis_item is not None and vnt_kaina_item is not None:
                    # skaičiaus atvaizdavimas su dešimtainėmis dalimis, panaikinant tarpus ir pakeičiant kablelius taškais
                    kiekis = float(kiekis_item.text().replace(' ', '').replace(',', '.'))
                    vnt_kaina = float(vnt_kaina_item.text().replace(' ', '').replace(',', '.'))

                    suma = kiekis * vnt_kaina
                    # print('suskaiciuoti suma - suma: ', suma)

                    # nustatomas locale modulis
                    locale.setlocale(locale.LC_ALL, '')

                    # formatuojama suma su tarpais tarp tūkstančių, dešimčių tūkstančių ir t.t.
                    formatted_suma = locale.format_string("%.2f", suma, grouping=True)
                    # kad būtų atvaizduojama su tarpasi vietoje kablelių ir kableliais vietoje taškų
                    formatted_suma = formatted_suma.replace(',', ' ').replace('.', ',')
                    # print('suskaiciuoti_suma - formatted_suma: ', formatted_suma)

                    # sukuriamas naujas QTableWidgetItem su formatuota sandauga
                    suma_item = QTableWidgetItem(formatted_suma)

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
            # pasirenkamas sumos stulpelis
            if item.column() == 5:
                suma = 0  # pradinė reikšmė

                # patikrinami visos lentelės paskutiniai stulpeliai su sumomis, kurios sudedamos ir išvedama bendra suma
                for i in range(self.darbu_lentele.rowCount()):
                    item = self.darbu_lentele.item(i, 5)
                    if item is not None and item.text() != '':
                        # pašalinami tarpai, kablelis pakeičiamas tašku, kad būtų galima atlikti matematinius veiksmus
                        suma += float(item.text().replace(' ', '').replace(',', '.'))
                        # print('atnaujinti_sumas - suma (float): ', suma)

                # nustatomas locale
                locale.setlocale(locale.LC_ALL, '')  # nustatoma lokalė

                # formatuojama bendra suma atvaizdavimui su tarpais ir kableliu
                self.suma_viso = locale.format_string("%.2f", suma, grouping=True).replace(',', ' ').replace('.', ',')
                # print('atnaujinti_sumas - self.suma_viso: ', self.suma_viso)

                # į lentelę įrašoma nauja suma su dviem skaičiais po kablelio
                self.suma_viso_line_edit.setText(self.suma_viso)

                # apskaičiuojamas pvm ir pridedamas į atitinkamą eilutę
                pvm = suma * 0.21
                # formatuojama suma atvaizdavimui su tarpais ir kableliu
                self.pvm = locale.format_string("%.2f", pvm, grouping=True).replace(',', ' ').replace('.', ',')
                self.pvm_line_edit.setText(self.pvm)
                # print('atnaujinti_sumas - self.pvm: ', self.pvm)

                # paskaičiuojama visa suma su PVM ir pridedama į atitinkamą eilutę
                suma_suPVM = suma + pvm
                # formatavimas atvaizdavimui su tarpais ir kableliais vietoje taškų
                self.suma_suPVM = locale.format_string("%.2f", suma_suPVM, grouping=True).replace(',', ' ').replace('.', ',')
                self.suma_suPVM_line_edit.setText(self.suma_suPVM)
                # print('atnaujinti_sumas - self.suma_suPVM: ', self.suma_suPVM)

                # mokėtina suma paskaičiuojama atsižvelgiant, ar yra taikomas PVM 96 str. (ar pažymėtas checkbox)
                if self.PVM96_str_checkbox.isChecked():
                    moketina_suma = float(self.suma_viso.replace(' ', '').replace(',', '.'))
                else:
                    moketina_suma = float(self.suma_suPVM.replace(' ', '').replace(',', '.'))

                # formatavimas atvaizdavimui su tarpais ir kableliais vietoje taškų
                self.moketina_suma = locale.format_string("%.2f", moketina_suma, grouping=True).replace(',', ' ').replace('.', ',')
                self.moketina_suma_line_edit.setText(self.moketina_suma)
                # print('atnaujinti_sumas - self.moketina_suma: ', self.moketina_suma)

        except Exception as e:
            print(f"Error in atnaujinti_sumas: {e}")


    def atnaujinti_sumas_po_istrynimo(self):
        try:
            suma = 0

            for i in range(self.darbu_lentele.rowCount()):
                item = self.darbu_lentele.item(i, 5)
                if item is not None and item.text() != '':
                    # pašalinami tarpai, kableliai pakeičiami taškais, kad atpažintų tekstą
                    suma += float(item.text().replace(' ', '').replace(',', '.'))
                    # print('atnaujinti_sumas_po_istrynimo - suma (float): ', suma)

            # nustatomas locale
            locale.setlocale(locale.LC_ALL, '')

            # formatuojama suma atvaizdavimui su tarpais ir kableliais
            self.suma_viso = locale.format_string("%.2f", suma, grouping=True).replace(',', ' ').replace('.', ',')
            self.suma_viso_line_edit.setText(self.suma_viso)
            # print('atnaujinti_sumas_po_istrynimo - self.suma_viso: ', self.suma_viso)

            pvm = suma * 0.21
            self.pvm = locale.format_string("%.2f", pvm, grouping=True).replace(',', ' ').replace('.', ',')
            self.pvm_line_edit.setText(self.pvm)
            # print('atnaujinti_sumas_po_istrynimo - self.pvm: ', self.pvm)

            suma_suPVM = suma + pvm
            self.suma_suPVM = locale.format_string("%.2f", suma_suPVM, grouping=True).replace(',', ' ').replace('.', ',')
            self.suma_suPVM_line_edit.setText(self.suma_suPVM)
            # print('atnaujinti_sumas_po_istrynimo - self.suma_suPVM: ', self.suma_suPVM)

            # mokėtina suma paskaičiuojama atsižvelgiant, ar yra taikomas PVM 96 str. (ar pažymėtas checkbox)
            if self.PVM96_str_checkbox.isChecked():
                moketina_suma = float(self.suma_viso.replace(' ', '').replace(',', '.'))
            else:
                moketina_suma = float(self.suma_suPVM.replace(' ', '').replace(',', '.'))

            self.moketina_suma = locale.format_string("%.2f", moketina_suma, grouping=True).replace(',', ' ').replace('.', ',')
            self.moketina_suma_line_edit.setText(self.moketina_suma)
            # print('atnaujinti_sumas_po_istrynimo - self.moketina_suma: ', self.moketina_suma)

        except Exception as e:
            print(f"Error in atnaujinti_sumas_po_istrynimo: {str(e)}")


    def update_moketina_suma(self, state):
        try:
            # nustatoma lietuviška lokalė
            locale.setlocale(locale.LC_ALL, '')

            if state == Qt.Checked:  # jeigu checkbox pažymėtas
                suma_viso_text = self.suma_viso.replace(' ', '')  # pašalinami tarpai, kad atpažintų tekstą
                if suma_viso_text != '':
                    if '.' in suma_viso_text and len(suma_viso_text.split('.')[1]) == 1:  # patikrinama, kiek po kablelio yra skaičių
                        suma_viso_text += '0'  # jeigu tik vienas skaičius po kablelio, pridedamas papildomas nulis
                    elif ',' in suma_viso_text:  # patikrinama, ar tekstas turi skaičių po kablelio
                        suma_viso_text = suma_viso_text.replace(',', '.')  # kablelis pakeičiamas tašku prieš konvertuojant į float

                    # formatavimas atvaizdavimui su kableliais
                    self.moketina_suma = locale.format_string("%.2f", float(suma_viso_text), grouping=True).replace('.', ',')
                    self.moketina_suma_line_edit.setText(self.moketina_suma)  # atitinkama suma įrašoma į lentelę
            else:
                suma_suPVM_text = self.suma_suPVM.replace(' ', '')  # pašalinami tarpai, kad atpažintų tekstą

                if suma_suPVM_text != '':
                    if '.' in suma_suPVM_text and len(suma_suPVM_text.split('.')[1]) == 1:
                        suma_suPVM_text += '0'
                    elif ',' in suma_suPVM_text:
                        suma_suPVM_text = suma_suPVM_text.replace(',', '.')

                    # formatavimas atvaizdavimui su kableliais
                    self.moketina_suma = locale.format_string("%.2f", float(suma_suPVM_text), grouping=True).replace('.', ',')
                    self.moketina_suma_line_edit.setText(self.moketina_suma)

        except Exception as e:
            print(f"Error in update_moketina_suma: {e}")


    def delete_table_record(self):
        try:
            current_row = self.darbu_lentele.currentRow()  # pažymėta eilutė
            if current_row >= 0:
                self.darbu_lentele.removeRow(current_row)

                # atnaujinamos sumos
                self.atnaujinti_sumas_po_istrynimo()

            else:
                QMessageBox.warning(self, "Perspėjimas", "Nepasirinktas įrašas!", QMessageBox.Ok)
        except Exception as e:
            print(f"Error in delete_Table_record: {str(e)}")


    def paversti_skaicius_zodziais(self, suma):
        try:
            # kablelis pakeičiamas į tašką, kad būtų galima naudoti split funkciją
            suma_str = str(suma).replace(',', '.').replace('\xa0', '').replace(' ', '')
            print('skaičiai į žodžius suma_str: ', suma_str)

            # skaičius padalinamas į dvi dalis per kablelį
            if '.' in suma_str:
                sveika_dalis, dalis_po_kablelio = suma_str.split('.')
            else:
                sveika_dalis = suma_str
                dalis_po_kablelio = '00'  # numatytoji vertė, jei nėra kablelio

            # patikrinama, ar po kablelio yra du skaitmenys, jei ne, pridedamas antras skaičius - 0
            if len(dalis_po_kablelio) == 1:
                dalis_po_kablelio += '0'
            elif len(dalis_po_kablelio) > 2:  # ribojamas skaičius po kablelio iki dviejų
                dalis_po_kablelio = dalis_po_kablelio[:2]

            # konvertuojame sveikąją dalį (iki kablelio) į žodžius
            sveika_dalis_zodziais = num2words(int(sveika_dalis), lang='lt').capitalize()

            return f"{sveika_dalis_zodziais} Eur {dalis_po_kablelio} ct"
        except Exception as e:
            print(f"Error in paversti_skaicius_zodziais: {e}")
            return ""


    def create_invoice_clicked(self):
        try:
            # surinkti duomenis iš formos
            self.invoice_no = self.saskaitos_numeris.text()
            self.buyer = self.pirkejas.text()
            self.company_code = self.imones_kodas.text()
            self.PVM_code = self.PVM_kodas.text().upper()
            self.buyer_address = self.pirkejo_adresas.text()
            self.doc_date = self.dok_data.date().toString('yyyy-MM-dd')
            self.pay_due = self.apmoketi_iki.date().toString('yyyy-MM-dd')

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

                self.table_data.append(row_data)  # pridedamas kiekvienas elementas kaip atskiras
            print(self.table_data)

            # patikrinti, ar self.table_data nėra tuščias
            if not self.table_data:
                QMessageBox.Warning(self, 'Klaida', 'Lentelei užpildyti nėra duomenų')
                return

            # patikrinti, ar rowCount ir columnCount yra teisingi
            if len(self.table_data) != self.darbu_lentele.rowCount() or (self.table_data and len(self.table_data[0]) != self.darbu_lentele.columnCount()):
                print("Klaida: eilučių ir stulpelių skaičius nėra teisingas")
                return

            # # Gauti vartotojo vardą
            # user_name = os.getlogin()

            # # patikrinamas OS tipas ir nustatomas OneDrive katalogo kelias
            # system = platform.system()
            #
            # if system == "Windows":
            #     # OneDrive katalogo kelias Windows OS
            #     one_drive_directory = f"C:/Users/{user_name}/OneDrive"
            # elif system == "Darwin":  # macOS
            #     one_drive_directory = f"/Users/{user_name}/OneDrive"
            # else:
            #     QMessageBox.warning(self, 'Klaida', 'Nepažįstama operacinė sistema. Pasirinkite vietą rankiniu būdu.')
            #     one_drive_directory = None
            #
            # #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # # patikrinama, ar OneDrive egzistuoja arba jei OS nepalaikoma, naudojame dialogą failo pasirinkimui
            # if not one_drive_directory or not os.path.exists(one_drive_directory):
            #     QMessageBox.warning(self, 'Klaida', 'OneDrive katalogas nerastas. Pasirinkite išsaugojimo vietą rankiniu būdu.')

            # Naudojame QFileDialog failo kelio pasirinkimui
            file_dialog = QFileDialog()
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setNameFilter("PDF Files (*.pdf)")

            # nustatomas failo pavadinimo šablonas
            default_filename = f"{self.invoice_no}.pdf"

            # gaunama failo išsaugojimo vieta su pasirinktu failo pavadinimu
            save_path, _ = file_dialog.getSaveFileName(self, "Pasirinkite vietą sąskaitai išsaugoti", default_filename, "PDF Files (*.pdf)")

            # Patikriname, ar vartotojas atšaukė failo išsaugojimo dialogą
            if not save_path:
                print("Failo išsaugojimo dialogas atšauktas")
                return
            if not save_path.lower().endswith(".pdf"):
                save_path += ".pdf"

            # sukuriama sąskaita
            self.create_invoice(save_path, self.table_data)

            # patikrinama, ar failas sukurtas ir egzistuoja
            if os.path.exists(save_path):
                print(f'Opening invoice file: {save_path}')  # Spausdiname failo kelią, kad patikrintume teisingumą
                os.startfile(save_path)  # sukurto pdf dokumento atidarymas peržiūrai
            else:
                print(f"{save_path} dokumentas nerastas.")

        except Exception as e:
            print(f'Error in create_invoice_clicked: {e}')


    def create_invoice(self, filename, table_data):
        try:
            c = canvas.Canvas(filename, pagesize=A4)

            # nustatomas katalogas, kuriame yra vykdomasis failas
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller laikiniesiems failams saugoti naudoja _MEIPASS
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))

            # sukuriami pilni keliai iki šriftų failų
            font_path = os.path.join(base_path, 'times_new_roman/times.ttf')
            bold_font_path = os.path.join(base_path, 'times_new_roman/timesbd.ttf')

            # užregistruojam lietuviškas raides palaikantį šriftą
            pdfmetrics.registerFont(TTFont('times', font_path))
            pdfmetrics.registerFont(TTFont('times_bold', bold_font_path))

            # dokumento antraštės uždėjimas
            c.setFont("times_bold", 22)
            c.drawString(150, 790, "PVM SĄSKAITA FAKTŪRA")  # x - pirmojo simbolio koordinatė

            # sąskaitos numerio eilutė
            c.setFont("times", 14)
            c.drawString(230, 765, f"Serija IND Nr. {self.invoice_no}")

            # sąskaitos išrašymo data
            c.setFont("times_bold", 12)
            c.drawString(260, 745, f"{self.doc_date}")

            # pardavėjo duomenų blokas
            c.setFont("times_bold", 12)
            c.drawString(70, 695, "Pardavėjas:")
            c.setFont("times", 12)
            c.drawString(70, 680, 'UAB "Indasta"')
            c.drawString(70, 665, "Įmonės kodas: 302716777")
            c.drawString(70, 650, "PVM mokėtojo kodas: LT100006623911")
            c.drawString(70, 635, "Adresas: S. Daukanto g. 19, Kazlų Rūda")
            c.drawString(70, 620, 'Bankas: AB "Swedbank"')
            c.drawString(70, 605, "Atsiskaitomoji sąskaita: ")
            c.drawString(70, 590, 'LT47 7300 0101 3385 164')

            # c.setFont("DejaVuBold", 12)
            # c.drawString(30, 685, "Pardavėjas:")
            # c.setFont("DejaVuSans", 12)
            # c.drawString(30, 670, 'UAB "Pardavėjas"')
            # c.drawString(30, 655, "Įmonės kodas: 112233445")
            # c.drawString(30, 640, "PVM mokėtojo kodas: LT112233445")
            # c.drawString(30, 625, "Adresas: Adreso g. 19, Miestas")
            # c.drawString(30, 610, 'Bankas: AB "Bankas"')
            # c.drawString(30, 595, "Atsiskaitomoji sąskaita: ")
            # c.drawString(30, 580, 'LT11 0000 2222 3333 444')

            # kliento duomenų blokas
            c.setFont("times_bold", 12)
            c.drawString(380, 695, "Pirkėjas:")
            c.setFont("times", 12)
            c.drawString(380, 680, f'{self.buyer}')
            c.drawString(380, 665, f"Įmonės kodas: {self.company_code}")
            c.drawString(380, 650, f"PVM mokėtojo kodas: {self.PVM_code}")
            c.drawString(380, 635, f"Adresas: {self.buyer_address}")

            # 'apmokėti iki' eilutė
            c.setFont("times_bold", 12)
            c.drawString(415, 560, f"Apmokėti iki: {self.pay_due}")

            # paslaugų lentelės dydis ir koordinatės
            col_widths = [40, 230, 55, 40, 65, 65]
            row_heights = [30] * len(table_data)

            # pradiniai lentelės x ir y taškai
            start_x = 70
            start_y = 530

            # teksto dydžio nustatymas
            c.setFont("times", 12)

            # uždedamos stulpelių antraštės
            headers = ['Eil. Nr.', 'Atliktų darbų pavadinimas', 'Mato vnt.', 'Kiekis', 'Vnt. kaina', 'Suma, €']

            # nustatomi antraščių eilutės parametrai
            for col, header in enumerate(headers):
                headers_x_line = start_x + sum(col_widths[:col])  # antraščių pradinis x taškas
                headers_y_line = start_y  # antraščių pradinis y taškas

                header_text_width = pdfmetrics.stringWidth(header, 'times', 12)  # antraščių teksto plotis

                # nubrėžiamos ir sucentruojamos antraštės (pavadinimai)
                c.drawString(headers_x_line + (col_widths[col] - header_text_width) / 2,
                             headers_y_line + (row_heights[0] - 12) / 2, header)
                c.rect(headers_x_line, start_y, col_widths[col], 20, stroke=1, fill=0)  # antraščių celių rėmeliai

            # nustatomi parametrai lentelės eilučių braižymui
            start_y -= 1  # pradinis teksto y taškas perkeliamas žemiau viršutinės lentelės linijos

            # sukuriamas tuščias eilučių aukščio sąrašas
            text_row_heights = []

            for row in range(self.darbu_lentele.rowCount()):
                row_height = 30  # numatytas pradinis eilutės aukštis

                for col in range(self.darbu_lentele.columnCount()):
                    if col == 1:  # darbų aprašymo stulpelis
                        widget = self.darbu_lentele.cellWidget(row, col)
                        if widget is not None and isinstance(widget, QLabel):
                            cell_text = widget.text()  # gaunamas tekstas iš QLabel
                        else:
                            # gaunamas įprastas QTableWidgetItem
                            item = self.darbu_lentele.item(row, col)
                            cell_text = item.text() if item is not None else ''

                        lines = simpleSplit(cell_text, 'times', 12, col_widths[col] - 10)  # tekstas skaidomas į eilutes
                        row_height = max(row_height, 15 * len(lines))  # apskaičiuojamas maksimalus aukštis pagal tekstą
                text_row_heights.append(row_height)  # eilutės aukštis prijungiamas į eilučių aukščio sąrašą

            # nubraižoma lentelė
            try:
                for row in range(self.darbu_lentele.rowCount()):
                    # paskaičiuojamas eilutės aukštis (pagal turinį)
                    row_height = text_row_heights[row]

                    for col in range(self.darbu_lentele.columnCount()):
                        # paskaičiuojamas celės pradžios taškas
                        cell_x = start_x + sum(col_widths[:col])
                        cell_y = start_y - sum(text_row_heights[:row + 1])

                        # darbų aprašymo teksto talpinimas celėje
                        if col == 1:
                            widget = self.darbu_lentele.cellWidget(row, col)
                            if widget is not None and isinstance(widget, QLabel):
                                cell_text = widget.text()  # gaunamas tekstas iš QLabel
                            else:
                                item = self.darbu_lentele.item(row, col)
                                cell_text = item.text() if item is not None else ''

                            # eilučių skaidymas, jeigu tekstas per ilgas
                            lines = simpleSplit(cell_text, 'times', 12, col_widths[col] - 5)
                            # vertikalus pozicionavimas, kad po tekstu liktų šiek tiek tuščios vietos
                            text_y = cell_y + row_height - 15  # nustatoma pirmosios eilutės y pozicija

                            # eilutės aukštis apskaičiuojamas pagal teksto eilučių skaičių
                            for line in lines:  # kiekviena eilutė rašoma atskirai
                                c.drawString(cell_x + 5, text_y, line)
                                text_y -= 15  # perkėlimas į kitą eilutę
                        else:
                            # gaunamas tekstas iš kitų stulpelių
                            item = self.darbu_lentele.item(row, col)
                            cell_text = item.text() if item is not None else ''

                            # paskaičiuojamas teksto plotis
                            text_width = pdfmetrics.stringWidth(cell_text, 'times', 12)

                            # centruojami stulpeliai išskyrus antrą, pridedami maži krašteliai necentruotiems stulpeliams
                            text_x = cell_x + (col_widths[col] - text_width) / 2 if col == 0 or col >= 2 else cell_x + 5

                            # rašomas įprastas centruotas tekstas kituose stulpeliuose
                            text_y = cell_y + row_height - 15  # nustatoma teksto y pozicija
                            c.drawString(text_x, text_y, cell_text)

                        # braižomos celių kraštinės linijos - rėmeliai
                        c.rect(cell_x, cell_y, col_widths[col], row_height, stroke=1, fill=0)

            except Exception as e:
                print(f'Error in table creation: {e}')

            # baigus braižyti lentelę, apskaičiuojama nauja y pozicija
            table_end_y = start_y - sum(text_row_heights)

            # dinamiškai pritaikoma po lentele esančių tekstų vieta
            page_bottom_margin = 50  # puslapio pabaigos paraštė
            text_start_y = table_end_y - 20  # papildomas tarpas tarp lentelės ir tekstų

            # užtikrinama, kad būtų pakankamai vietos parašų sekcijai iki lapo apačios
            signature_height = 140  # apytikslis aukštis, reikalingas parašų blokui

            # pakoregavimas y_offsets, jeigu nėra pakankamai vietos
            if text_start_y - signature_height < page_bottom_margin:
                text_start_y = page_bottom_margin + signature_height

            # tekstas po lentele
            c.setFont("times_bold", 12)
            labels = ['Viso suma:', 'PVM 21 %:', 'Viso suma (su PVM):', 'Mokėtina suma, Eur:']
            y_offsets = [text_start_y - i * 15 for i in range(len(labels))]  # kiekviena etiketė bus rodoma 15 pikselių žemiau nei ankstesnė

            # surašomi sumų pavadinimai
            for label, y_offset in zip(labels, y_offsets):
                c.drawString(340, y_offset, label)

            # teksto po lentele reikšmės (sumos)
            c.setFont("times", 12)

            texts = [
                self.suma_viso,
                self.pvm,
                self.suma_suPVM,
                self.moketina_suma
            ]

            for text, y_offset in zip(texts, y_offsets):
                # nubraižomos sumų eilutės
                c.drawString(510, y_offset, text)

            # PVM 96 str. eilutė
            if self.PVM96_str_checkbox.isChecked():
                c.setFont("times", 12)
                c.drawString(70, y_offsets[-1] - 40, '* Pagal LR PVM įst. 96 str. taikomas atvirkštinis PVM apmokestinimas')

            # mokėtina suma žodžiais
            c.setFont("times_bold", 12)
            suma = self.moketina_suma.replace('\xa0', '').replace(' ', '').replace(',', '.')
            suma = float(suma)  # suma pakeičiama į dešimtainį, kad galėtų konvertuoti į tekstą
            text = self.paversti_skaicius_zodziais(suma)  # konvertuotavimo iš sumos į tekstą metodo iškvietimas priskiriant kintamąjį

            # parašoma mokėtina suma žodžiais ir nubrėžiama linija po ja
            c.drawString(80, y_offsets[-1] - 70, text)
            c.line(70, y_offsets[-1] - 80, 550, y_offsets[-1] - 80)

            # tekstas po linija
            c.setFont("times", 10)
            c.drawString(260, y_offsets[-1] - 90, 'suma žodžiais')

            # parašų blokas
            signature_start_y = page_bottom_margin + 85  # tarpas nuo lapo apačios

            pasirase_combo_variantas = self.kas_israse.currentText()  # QComboBox esantys pasirinkto asmens duomenys

            c.setFont("times_bold", 12)
            c.drawString(70, signature_start_y - 35, 'Išrašė:')  # teksto patalpinimas

            # išrašiusio asmens duomenų iš QComboBox įrašymas
            c.setFont("times", 12)
            c.drawString(70, signature_start_y - 55, f'{pasirase_combo_variantas}')

            c.setFont("times", 10)
            # nubrėžiama linija po sąskaitą išrašiusio asmens duomenimis
            c.line(70, signature_start_y - 60, 270, signature_start_y - 60)
            c.drawString(105, signature_start_y - 70, '(pareigos, vardas, pavardė)')  # tekstas po linija

            # nubrėžiama parašo linija
            c.line(70, signature_start_y - 100, 140, signature_start_y - 100)
            c.drawString(90, signature_start_y - 110, '(parašas)')  # tekstas po linija

            # sąskaitą priėmusio asmens duomenys
            c.setFont("times_bold", 12)
            c.drawString(340, signature_start_y - 35, 'Priėmė:')

            c.setFont("times", 10)
            c.line(340, signature_start_y - 60, 540, signature_start_y - 60)  # nubrėžiama linija
            c.drawString(375, signature_start_y - 70, '(pareigos, vardas, pavardė)')  # tekstas po linija

            # nubrėžiama parašo linija
            c.line(340, signature_start_y - 100, 410, signature_start_y - 100)
            c.drawString(360, signature_start_y - 110, '(parašas)')

            # užbaigiamas PDF failo kūrimas
            c.showPage()
            c.save()
            print("Baigtas PDF failo kūrimas.")

            QMessageBox.information(self, 'Informacija', 'Sąskaita sėkmingai sukurta ir patalpinta išrašytų sąskaitų kataloge.')

        except Exception as e:
            print(f'Error in create_invoice method: {e}')


    def new_invoice_clicked(self):
        try:
            # išvalomi duomenų suvedimo laukeliai
            self.saskaitos_numeris.clear()
            self.projekto_nr.clear()
            self.pirkejas.clear()
            self.imones_kodas.clear()
            self.PVM_kodas.clear()
            self.pirkejo_adresas.clear()
            self.dok_data.setDate(QDate.currentDate())
            self.apmoketi_iki.setDate(QDate.currentDate())

            # išvaloma 'darbu_lentele'
            self.darbu_lentele.clearContents()
            self.darbu_lentele.setRowCount(0)  #nustatoma 0 eilučių

            # išvalomi darbu_lentele suvedimo laukeliai
            self.line_edit1.setText('1')
            self.line_edit2.clear()
            self.combo_box.setCurrentIndex(0)  # nustatoma pradinė reikšmė combo laukelyje
            self.line_edit4.clear()
            self.line_edit5.clear()

            self.line_edit2.setFocus()  # pelės žymeklis padedamas antrame duomenų suvedimo laukelyje

            # išvaloma darbų lentelė
            self.table_data = []
            print(self.table_data)

        except Exception as e:
            print(f"Error in new_invoice_clicked: {str(e)}")



#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\///////////////////////////////////////////
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CreationOfInvoice()
    window.show()
    sys.exit(app.exec_())
