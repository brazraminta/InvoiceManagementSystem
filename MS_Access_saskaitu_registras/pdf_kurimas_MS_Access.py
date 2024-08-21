import sys
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PyQt5.QtWidgets import *
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
from PyQt5.QtCore import QDate, Qt
from num2words import num2words
from PyQt5.QtGui import QFont
import subprocess



class CreationOfInvoice(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sąskaitų išrašymo langas")
        self.setGeometry(500, 200, 1250, 770)

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
            self.darbu_lentele.resizeColumnsToContents()

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
            # eil_nr = self.line_edit1.text()
            eil_nr = str(self.darbu_lentele.rowCount() + 1)  # nustatomas naujas Eil. Nr.
            darbu_pavadinimas = self.line_edit2.text()
            mato_vnt = self.combo_box.currentText()
            kiekis = self.line_edit4.text()
            vnt_kaina = self.line_edit5.text()

            # sukuriama nauja lentelės eilutė su gautu tekstu
            row = [eil_nr, darbu_pavadinimas, mato_vnt, kiekis, vnt_kaina]

            # eilutė pridedama prie lentelės
            self.darbu_lentele.insertRow(self.darbu_lentele.rowCount())
            for i, text in enumerate(row):
                self.darbu_lentele.setItem(self.darbu_lentele.rowCount() - 1, i, QTableWidgetItem(text))

            # Išvalomi QLineEdit laukeliai, kad eitų vesti kitus duomenis
            # self.line_edit1.setText(str(self.darbu_lentele.rowCount() + 1))
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


    def suskaiciuoti_suma(self, row, column):
        try:
            if column in (3, 4):
                # gauname 4 ir 5 stulpelio reikšmes
                kiekis_item = self.darbu_lentele.item(row, 3)
                vnt_kaina_item = self.darbu_lentele.item(row, 4)

                if kiekis_item is not None and vnt_kaina_item is not None:
                    kiekis = float(kiekis_item.text())
                    vnt_kaina = float(vnt_kaina_item.text())
                    suma = kiekis * vnt_kaina

                    # sukuriam naują QTableWidgetItem su sandauga
                    suma_item = QTableWidgetItem(f"{suma:.2f}")

                    # self.darbu_lentele.setItem(row, 5, QTableWidgetItem(f"{suma: .2f}"))

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


    def atnaujinti_sumas_po_istrynimo(self):
        try:
            # suma = self.suma_viso_line_edit
            suma = 0

            for i in range(self.darbu_lentele.rowCount()):
                item = self.darbu_lentele.item(i, 5)
                if item is not None and item.text() != '':
                    suma += float(item.text())
            self.suma_viso_line_edit.setText("{:,.2f}".format(float(suma)))

            pvm = (suma * (21 / 100))
            self.pvm_line_edit.setText("{:,.2f}".format(float(pvm)))

            suma_suPVM = (suma + pvm)
            self.suma_suPVM_line_edit.setText("{:,.2f}".format(float(suma_suPVM)))

            if self.PVM96_str_checkbox.isChecked():
                suma_viso_text = self.suma_viso_line_edit.text()
                suma_viso_text = suma_viso_text.replace(',', '')
                self.moketina_suma_line_edit.setText("{:,.2f}".format(float(suma_viso_text)))
            else:
                suma_suPVM_text = self.suma_suPVM_line_edit.text()
                suma_suPVM_text = suma_suPVM_text.replace(',', '')
                self.moketina_suma_line_edit.setText("{:,.2f}".format(float(suma_suPVM_text)))

        except Exception as e:
            print(f"Error in atnaujinti_sumas_po_istrynimo: {str(e)}")

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


    def delete_table_record(self):
        try:
            current_row = self.darbu_lentele.currentRow()
            if current_row >= 0:
                self.darbu_lentele.removeRow(current_row)

                # atnaujinamos sumos
                self.atnaujinti_sumas_po_istrynimo()

            else:
                QMessageBox.warning(self, "Perspėjimas", "Nepasirinktas įrašas!", QMessageBox.Ok)
        except Exception as e:
            print(f"Error in delete_Table_record: {str(e)}")


    def paversti_skaicius_zodziais(selfself, skaicius):
        # skaičius padalinamas į dvi dalis per kablelį
        sveika_dalis, dalis_po_kablelio = str(skaicius).split('.')

        # patikrinama, ar po kablelio yra du skaitmenys, jei ne, pridedamas antras skaičius - 0
        if len(dalis_po_kablelio) == 1:
            dalis_po_kablelio += '0'

        # konvertuojame sveikąją dalį (iki kablelio) į žodžius
        sveika_dalis_zodziais = num2words(int(sveika_dalis), lang='lt')

        return sveika_dalis_zodziais + ' eurai (-ų) ' + dalis_po_kablelio + ' ct'


    def create_invoice_clicked(self, filename):
        try:
            # surinkti duomenis iš formos
            self.saskaitos_numeris = self.saskaitos_numeris.text()
            self.pirkejas = self.pirkejas.text()
            self.imones_kodas = self.imones_kodas.text()
            self.PVM_kodas = self.PVM_kodas.text().upper()
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

            # Gauti vartotojo vardą
            user_name = os.getlogin()

            # OneDrive katalogo kelias
            one_drive_directory = f"C:/Users/{user_name}/OneDrive"

            # nurodom failo įrašymo vietą ir pavadinimą
            text, ok = QInputDialog.getText(self, 'Įveskite failo pavadinimą', f'Sąskaitos numeris: {self.saskaitos_numeris}')
            if ok:
                filename = os.path.join(one_drive_directory, f"{text}.pdf")
                # directory = f"C:/Users/Raminta/Documents/Programavimas su python 2023-12-18/Invoice Management System/Israsytos saskaitos"

                self.create_invoice(filename, self.table_data[0:])

                # patikrinama, ar failas sukurtas ir egzistuoja
                if os.path.exists(filename):
                    print(f'Opening invoice file: {filename}')  # Spausdiname failo kelią, kad patikrintume teisingumą
                    # sukurto pdf dokumento atidarymas peržiūrai
                    os.startfile(filename)
                else:
                    print(f"{filename} file not found.")

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
            font_path = os.path.join(base_path, 'dejavu-sans/DejaVuSans.ttf')
            bold_font_path = os.path.join(base_path, 'dejavu-sans/DejaVuSans-Bold.ttf')

            # užregistruojam lietuviškas raides palaikantį šriftą
            # pdfmetrics.registerFont(TTFont('DejaVuSans', "C:/Users/Raminta/Downloads/dejavu-sans/DejaVuSans.ttf"))
            # pdfmetrics.registerFont(TTFont('DejaVuBold', "C:/Users/Raminta/Downloads/dejavu-sans/DejaVuSans-Bold.ttf"))
            pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
            pdfmetrics.registerFont(TTFont('DejaVuBold', bold_font_path))

            # dokumento antraštės uždėjimas
            c.setFont("DejaVuBold", 22)
            c.drawString(150, 790, "PVM SĄSKAITA FAKTŪRA")  # x - pirmojo simbolio koordinatė

            # sąskaitos numerio eilutė
            c.setFont("DejaVuSans", 14)
            c.drawString(230, 765, f"Serija IND Nr. {self.saskaitos_numeris}")

            # sąskaitos išrašymo data
            c.setFont("DejaVuBold", 12)
            c.drawString(260, 740, f"{self.dok_data}")

            # pardavėjo duomenų blokas
            c.setFont("DejaVuBold", 12)
            c.drawString(30, 685, "Pardavėjas:")
            c.setFont("DejaVuSans", 10)
            c.drawString(30, 670, 'UAB "Indasta"')
            c.drawString(30, 655, "Įmonės kodas: 302716777")
            c.drawString(30, 640, "PVM mokėtojo kodas: LT100006623911")
            c.drawString(30, 625, "Adresas: S.Daukanto g. 19, Kazlų Rūda")
            c.drawString(30, 610, 'Bankas: AB "Swedbank"')
            c.drawString(30, 595, "Atsiskaitomoji sąskaita: ")
            c.drawString(30, 580, 'LT47 7300 0101 3385 164')

            # c.setFont("DejaVuBold", 12)
            # c.drawString(30, 685, "Pardavėjas:")
            # c.setFont("DejaVuSans", 10)
            # c.drawString(30, 670, 'UAB "Pardavėjas"')
            # c.drawString(30, 655, "Įmonės kodas: 112233445")
            # c.drawString(30, 640, "PVM mokėtojo kodas: LT112233445")
            # c.drawString(30, 625, "Adresas: Adreso g. 19, Miestas")
            # c.drawString(30, 610, 'Bankas: AB "Bankas"')
            # c.drawString(30, 595, "Atsiskaitomoji sąskaita: ")
            # c.drawString(30, 580, 'LT11 0000 2222 3333 444')

            # kliento duomenų blokas
            c.setFont("DejaVuBold", 12)
            c.drawString(370, 685, "Pirkėjas:")
            c.setFont("DejaVuSans", 10)
            c.drawString(370, 670, f'{self.pirkejas}')
            c.drawString(370, 655, f"Įmonės kodas: {self.imones_kodas}")
            c.drawString(370, 640, f"PVM mokėtojo kodas: {self.PVM_kodas}")
            c.drawString(370, 625, f"Adresas: {self.pirkejo_adresas}")

            # 'apmokėti iki' eilutė
            c.setFont("DejaVuBold", 12)
            c.drawString(370, 555, f"Apmokėti iki: {self.apmoketi_iki}")

            # paslaugų lentelės dydis ir koordinatės
            col_widths = [40, 210, 60, 50, 80, 80]
            row_heights = [30] * len(table_data)

            # pradiniai x ir y taškai
            start_x = 30
            start_y = 510

            # teksto dydžio nustatymas
            c.setFont("DejaVuSans", 10)

            # uždedamos stulpelių antraštės
            headers = ['Eil. Nr.', 'Atliktų darbų pavadinimas', 'Mato vnt.', 'Kiekis', 'Vnt. kaina', 'Suma, €']

            # nustatomi antraščių eilutės parametrai
            for col, header in enumerate(headers):
                headers_x_line = start_x + sum(col_widths[:col])  # antraščių pradinis x taškas
                headers_y_line = start_y  # antraščių pradinis y taškas

                header_text_width = pdfmetrics.stringWidth(header, 'DejaVuSans', 10)  # antraščių teksto plotis

                # nubrėžiamos antraštės
                c.drawString(headers_x_line + 2 + (col_widths[col] - header_text_width) / 2, headers_y_line + 2 + row_heights[0] - 15, header)
                c.rect(headers_x_line, start_y, col_widths[col], 30, stroke=1, fill=0)

            # sukuriamas tuščias eilučių aukščio sąrašas
            text_row_heights = []

            # nustatomi parametrai lentelės eilučių braižymui
            start_y -= 1  # pradinis teksto y taškas perkeliamas žemiau antraštės

            for row_data in table_data:
                row_height = 30  # pradinis eilutės aukštis
                for col, cell in enumerate(row_data):
                    if col == 1:  # darbų aprašymo stulpelis
                        lines = simpleSplit(cell, 'DejaVuSans', 10, col_widths[col] - 10)
                        row_height = max(row_height, 15 * len(lines))

                text_row_heights.append(row_height)

            # nubraižoma lentelė
            try:
                for row, row_data in enumerate(table_data):
                    for col, cell in enumerate(row_data):
                        # paskaičiuojamas celės pradžios taškas
                        cell_x = start_x + sum(col_widths[:col])
                        cell_y = start_y - sum(text_row_heights[:row + 1])

                        # paskaičiuojamas teksto plotis
                        text_width = pdfmetrics.stringWidth(cell, 'DejaVuSans', 10)

                        # centruojami stulpeliai išskyrus antrą, pridedami maži krašteliai necentruotiems stulpeliams
                        text_x = cell_x + (col_widths[col] - text_width) / 2 if col == 0 or col >= 2 else cell_x + 5
                        text_y = cell_y + text_row_heights[row] - 10  # vertikalus pozicionavimas, kad po tekstu liktų šiek tiek tuščios vietos

                        # darbų aprašymo stulpelio talpinimas celėje
                        if col == 1:
                            lines = simpleSplit(cell, 'DejaVuSans', 10, col_widths[col] - 10)

                            # eilutės aukštis apskaičiuojamas pagal teksto eilučių skaičių
                            # row_heights[row] = max(row_heights[row], 15 * len(lines))
                            for line in lines:
                                c.drawString(cell_x + 5, text_y, line)
                                text_y -= 15  # perkėlimas į kitą eilutę
                        else:
                            c.drawString(text_x, text_y, cell)

                        # braižo celių kraštus-linijas
                        c.rect(cell_x, cell_y, col_widths[col], text_row_heights[row], stroke=1, fill=0)

            except Exception as e:
                print(f'Error in table creation: {e}')

            # apskaičiuojama, kur baigiasi lentelė
            table_end_y = start_y - sum(text_row_heights)

            # dinamiškai pritaikoma po lentele esančių tekstų vieta
            text_start_y = table_end_y - 30  # papildomas tarpas tarp lentelės ir tekstų

            # tekstas po lentele
            c.setFont("DejaVuBold", 10)
            #
            # c.drawString(340, 330, 'Viso suma:')  # x - teksto pradžios taškas plotyje, y - teksto pradžios taškas aukštyje
            # c.drawString(340, 315, 'PVM 21 %:')
            # c.drawString(340, 300, 'Viso suma (su PVM):')
            # c.drawString(340, 285, 'Mokėtina suma, Eur:')

            labels = ['Viso suma:', 'PVM 21 %:', 'Viso suma (su PVM):', 'Mokėtina suma, Eur:']
            y_offsets = [text_start_y - i * 15 for i in range(len(labels))]

            for label, y_offset in zip(labels, y_offsets):
                c.drawString(340, y_offset, label)

            # teksto po lentele reikšmės (sumos)
            c.setFont("DejaVuSans", 10)

            texts = [
                self.suma_viso_line_edit.text(),
                self.pvm_line_edit.text(),
                self.suma_suPVM_line_edit.text(),
                self.moketina_suma_line_edit.text()
            ]

            # y_coords = [
            #     330,
            #     315,
            #     300,
            #     285
            # ]

            for text, y_offset in zip(texts, y_offsets):
            # for i, text in enumerate(texts):
                # paskaičiuojamas teksto plotis
                texts_width = pdfmetrics.stringWidth(text, 'DejaVuSans', 10)

                # apskaičiuoja pradinį teksto tašką
                texts_x = 540 - texts_width  # atima teksto plotį iš norimo pabaigos taško

                # nubraižomos sumų eilutės
                # c.drawString(texts_x, y_coords[i], text)
                c.drawString(text_x, y_offset, text)

            # PVM 96 str. eilutė
            if self.PVM96_str_checkbox.isChecked():
                c.setFont("DejaVuSans", 10)
                # c.drawString(30, 200, '* Pagal LR PVM įst. 96 str. taikomas atvirkštinis PVM apmokestinimas')
                c.drawString(30, y_offsets[-1] - 80, '* Pagal LR PVM įst. 96 str. taikomas atvirkštinis PVM apmokestinimas')  #40

            # mokėtina suma žodžiais
            c.setFont("DejaVuBold", 10)
            suma = float(self.moketina_suma_line_edit.text().replace(',', ''))
            text = self.paversti_skaicius_zodziais(suma)
            # c.drawString(30, 170, text)
            c.drawString(30, y_offsets[-1] - 110, text)  # 70
            # c.line(30, 160, 550, 160)
            c.line(30, y_offsets[-1] - 120, 550, y_offsets[-1] - 120)  #80

            c.setFont("DejaVuSans", 8)
            # c.drawString(200, 150, 'suma žodžiais')
            c.drawString(200, y_offsets[-1] - 130, 'suma žodžiais')  # 90

            # parašai
            pasirase_combo_variantas = self.kas_israse.currentText()
            c.setFont("DejaVuBold", 10)
            # c.drawString(30, 100, 'Išrašė:')
            c.drawString(30, y_offsets[-1] - 215, 'Išrašė:')  #130
            c.setFont("DejaVuSans", 10)
            # c.drawString(30, 80, f'{pasirase_combo_variantas}')
            c.drawString(30, y_offsets[-1] - 235, f'{pasirase_combo_variantas}')  #150

            c.setFont("DejaVuSans", 8)
            pareigos_text = 'pareigos, vardas, pavardė'
            pareigos_text_width = c.stringWidth(pareigos_text, 'DejaVuSans', 8)
            # c.drawString(30, 60, pareigos_text)
            c.drawString(30, y_offsets[-1] - 255, pareigos_text)  # 170
            # c.line(30, 75, 30 + pareigos_text_width, 75)
            c.line(30, y_offsets[-1] - 240, 30 + pareigos_text_width, y_offsets[-1] - 240)  #155

            parasas_text = 'parašas'
            # parasas_text_width = c.stringWidth(parasas_text, 'DejaVuSans', 10)
            # c.drawString(30, 10, parasas_text)
            c.drawString(30, y_offsets[-1] - 300, parasas_text)  # 215
            line_length = 50
            # c.line(30, 20, 30 + line_length, 20)
            c.line(30, y_offsets[-1] - 290, 30 + line_length, y_offsets[-1] - 290)  #205

            c.setFont("DejaVuBold", 10)
            # c.drawString(340, 100, 'Priėmė:')
            c.drawString(340, y_offsets[-1] - 215, 'Priėmė:')  #130

            c.setFont("DejaVuSans", 8)
            # c.drawString(340, 60, pareigos_text)
            c.drawString(340, y_offsets[-1] - 255, pareigos_text)  #170
            # c.line(340, 75, 340 + pareigos_text_width, 75)
            c.line(340, y_offsets[-1] - 240, 340 + pareigos_text_width, y_offsets[-1] - 240)  #155

            # c.drawString(340, 10, parasas_text)
            c.drawString(340, y_offsets[-1] - 300, parasas_text)  #215
            # c.line(340, 20, 340 + line_length, 20)
            c.line(340, y_offsets[-1] - 290, 340 + line_length, y_offsets[-1] - 290)  #205

            # Finalize the PDF
            c.showPage()
            c.save()
            print("Finished generating the table.")

            QMessageBox.information(self, 'Informacija', 'Sąskaita sėkmingai sukurta ir patalpinta išrašytų sąskaitų kataloge')

        except Exception as e:
            print(f'Error in create_invoice method: {e}')


    def new_invoice_clicked(self):
        try:
            # išvalomi suvedimo laukeliai
            self.saskaitos_numeris.setText("")
            self.projekto_nr.setText("")
            self.pirkejas.setText("")
            self.imones_kodas.setText("")
            self.PVM_kodas.setText("")
            self.pirkejo_adresas.setText("")
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

            self.line_edit2.setFocus()

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
