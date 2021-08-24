import pandas as pd
#sheetname = '시트명 or 숫자' , header = 숫자 skiprow=숫자
xlsx = pd.read_excel('./sample.xlsx')

#상위 데이터 확인
print(xlsx.head())
print()
print(xlsx.tail())
print()
print(xlsx.shape)


