import pandas as pd
from pandas import DataFrame
import xlrd


def gasBuster(fileName,csvName, year):
	wb = xlrd.open_workbook('/Users/malcolmmonroe/downloads/{}'.format(fileName)) 
	sheet = wb.sheet_by_index(0)
	rawData = []
	if year == 2012:
		for i in range(4,58):
			rawData.append(sheet.col_slice(i,3,172))
	else:
		for i in range(4,57):
			print sheet.col_slice(i,7,175)[0]	
			rawData.append(sheet.col_slice(i,7,175))
	
	print len(rawData)
	data = []
	for l in rawData:
	        for el in l:
	                data.append(el)
	print len(data)
	print year
	if year == 2014:
		dates = pd.date_range('1/1/2014 00:00:00', '12/31/2014 23:59:59', freq='1H')
		dF = DataFrame({'Timestamp': dates})
	
	elif year == 2013:
		dates = pd.date_range('1/1/2013 00:00:00', '12/31/2013 23:59:59', freq='1H')	
		dF = DataFrame({'Timestamp': dates})

	else:
		dates = pd.date_range('1/1/2012 00:00:00', '12/31/2012 23:59:59', freq='1H')  
                dF = DataFrame({'Timestamp': dates})


	values = []
	for i in range(len(dates)):
		values.append(data[i])
	
	print len(values)

	def stripper():
		strippedData = lambda x: str(x).split(':')[-1]
		return strippedData
	
	dF['value'] = values 
	dF['values'] = dF['value'].apply(stripper())
	for idx, value in enumerate(dF['values']):
		if value == "''":
			dF['values'][idx] = '0'

	print dF[:5]

	dF.to_csv('/users/malcolmmonroe/downloads/{}'.format(csvName), columns= ['Timestamp', 'values'], index=False)

