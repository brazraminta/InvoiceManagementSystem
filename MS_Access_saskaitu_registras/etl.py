import pandas as pd

#
# data = pd.Series([10, 20, 30, 40, 50])
# print(data)
#
# data_frame = {
#     'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
#     'Age': [25, 30, 22, 35, 28],
#     'City': ['New York', 'Los Angeles', 'Chicago', 'San Fransisco', 'Miami']
# }
#
# df = pd.DataFrame(data_frame)
# print(df)

#///////////////////////////////////////////////////////
# Chapter 1
# data = pd.read_csv("C:/Users/Raminta/Documents/Programavimas su python 2023-12-18/ETL/Exercise Files/Chapter_1/sample_data.csv")
# df = pd.DataFrame(data)
# print(df.head(5))
# print(df.tail(3))
# print(f'Rows: {df.shape[0]}, columns: {df.shape[1]}')
# print(df.duplicated())
# duplicates = data[data.duplicated()]
# print('Duplicates:', duplicates)

#//////////////////////////////////////////////////////////
# Chapter 2
# sample_csv = pd.read_csv("C:/Users/Raminta/Documents/Programavimas su python 2023-12-18/ETL/Exercise Files/Chapter_2/sample_data_csv.csv", header=None)
# print(sample_csv.head())

sample_excel = pd.read_excel("C:/Users/Raminta/Documents/Programavimas su python 2023-12-18/ETL/Exercise Files/Chapter_2/sample_data_excel.xlsx")
print(sample_excel.head())


