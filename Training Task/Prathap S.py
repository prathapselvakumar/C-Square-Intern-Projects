import pandas
exel_file="data.xlsx"
data_frame=pandas.read_excel("data.xlsx")
data_frame['result'] = data_frame.apply(lambda x:"looser" if x['sales'] < x['target'] else "winner", axis=1)
print(data_frame)
data_frame.to_excel('data.xlsx')

