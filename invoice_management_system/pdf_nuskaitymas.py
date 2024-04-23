# import PyPDF2
from PyPDF2 import PdfReader
import tkinter as tk
from tkinter import ttk
from docx import Document
import csv
import re  # Python regular expressions modulis, rasti ir ištraukti reikiamam tekstui


def read_file():
    try:
        #/////////  pdf failo nuskaitymas  ///////////////////
        # inputFile = "C:/Users/Raminta/Documents/Ivairus/Dacia pirkimui/Avansine saskaita.pdf"
        # inputFile = "C:/Users/Raminta/Documents/Programavimas su python 2023-12-18/Invoice Management System/Saskaitos/2020.03.30.pdf"
        # pdf = open(inputFile, 'rb')

        # pdf_reader = PdfReader(pdf)
        # page = pdf_reader.pages[0] # get the first page
        # invoice_text = page.extract_text()

        # print(invoice_text)

        #/////////  docx failo nuskaitymas   ////////////////
        # # nuskaityti docx (konvertuotus failus iš pdf)
        # inputFile = "C:/Users/Raminta/Downloads/2020.03.30.ocr.docx"
        # doc = Document(inputFile)
        #
        # # extract text from the .docx file
        # fullText = []
        # for para in doc.paragraphs:
        #     fullText.append(para.text)
        #
        # # create a new tkinter window
        # root = tk.Tk()
        # text = tk.Text(root)
        # # text.insert(tk.INSERT, invoice_text) # čia jeigu pdf nuskaitymą rodyti (nepaversto į docx formatą
        #
        # scrollbar = tk.Scrollbar(root, command=text.yview)
        # text.configure(yscrollcommand=scrollbar.set)
        # text.insert(tk.INSERT, '\n'.join(fullText))
        # text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        #
        # # run the tkinter main loop
        # root.mainloop()

        #/////////   csv failo nuskaitymas   /////////
        #
        # inputFile = "C:/Users/Raminta/Downloads/2020.03.30.ocr.csv"
        #
        # root = tk.Tk()
        # frame = ttk.Frame(root)
        # frame.pack(fill='both', expand=True)
        #
        # tree = ttk.Treeview(frame)
        # vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        # hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        #
        # tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        # tree.grid(column=0, row=0, sticky='nsew')
        # vsb.grid(column=1, row=0, sticky='ns')
        # hsb.grid(column=0, row=1, sticky='ew')
        #
        # frame.grid_columnconfigure(0, weight=1)
        # frame.grid_rowconfigure(0, weight=1)
        #
        # # Open the .csv file with 'utf-8' encoding
        # with open(inputFile, 'r', encoding='utf-8') as file:
        #     reader = csv.reader(file)
        #     for i, row in enumerate(reader):
        #         if i == 0:
        #             # Display the column names on the first row
        #             tree["columns"] = row
        #             for column in row:
        #                 tree.heading(column, text=column)
        #         else:
        #             # Insert the data on the subsequent rows
        #             tree.insert('', 'end', values=row)
        #
        # root.mainloop()

        #/////////////   .txt failo nuskaitymas /////////////////
        inputFile = "C:/Users/Raminta/Downloads/2020.03.30.ocr.txt"
        # inputFile = "C:/Users/Raminta/Downloads/Mokestinis_pranesimas_2020.08.13.ocr.txt"

        with open(inputFile, 'r', encoding='utf-8') as file:
            text_content = file.read()

            # find the text after 'Apmokėti iki:'
            match = re.search(r'(mokėt.*?)(\d{4}-\d{2}-\d{2})',text_content)  # ieško vienos datos

            if match:
                extracted_text = match.group(2)
            else:
                extracted_text = "Tekstas apie apmokėjimo datą nerastas."

            root = tk.Tk()
            text = tk.Text(root)
            text.insert(tk.INSERT, extracted_text)
            text.pack()

            root.mainloop()


    except Exception as e:
        print(f"Error from read_file: {e}")

read_file()
