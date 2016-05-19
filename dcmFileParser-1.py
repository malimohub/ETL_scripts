from datetime import datetime, timedelta 
import pandas as pd 
from pandas import DataFrame 
import requests
import json


class AmscParser(object):
	'''

	EXTRACTS DATA FROM CSV FILE PROVIDED BY AMSC, FORMATS DATA AND PUSH GENERATED CSV FILE TO BOS
	
	'''

	FILE_PATH_TEMPLATE = '/users/malcolmmonroe/desktop/AMSC_DATA/%s'
	STORE_FILE_PATH_TEMPLATE = '/users/malcolmmonroe/desktop/amscBosData/%s.csv'
	
	def __init__(self, filename):
		self.filename = filename
	
	
	def get_file_data(self):
		filePath = self.FILE_PATH_TEMPLATE % self.filename
		openFile = open(filePath, 'r') 
		csv_import = pd.read_csv(openFile, header=None)		
		return csv_import
		
	def change_time(self, timestamps):
		timestampsList = []
		del timestamps[0]	
		shifted_timestamps = [d - timedelta(minutes=15) for d in timestamps]
		pretty_close_timestamps = [d.strftime('%m/%d/%Y %H:%M') for d in shifted_timestamps]
		for timestamp in pretty_close_timestamps:
			expandStamp = list(timestamp)
			if expandStamp[11] == '0':
				del expandStamp[11]
				timestampsList.append(''.join(expandStamp))
			else:
				timestampsList.append(''.join(expandStamp))	
	
		return timestampsList

	
	def push_data_to_bos(self):
		response = requests.post(
			url='http://custom.buildingdashboard.net/dsv/push?datasource=bos://buildingos-csv/amscData',
			files={'data': open(self.STORE_FILE_PATH_TEMPLATE % self.filename, 'rb')}
			)
		try:
			content = response.json()
		except Exception as e:
			return response 	
		return content


	def etl_amsc_data(self):
		fileData = self.get_file_data()
		rawTimestampsBegin = fileData[13][0]
		rawTimestampEnd = fileData[14][0]
		startDate = datetime.strptime(str(fileData[12][0]), '%Y%m%d%H%M%S')
		endDate = datetime.strptime(str(fileData[13][0]), '%Y%m%d%H%M%S')
		dateRangeTimestamps = []
		dateRangeTimestamps.append(startDate)
		while startDate< endDate:
			startDate += timedelta(minutes=15) 
			dateRangeTimestamps.append(startDate)
		
		formattedTimestamps = self.change_time(dateRangeTimestamps) 		
		numberPoints = len(formattedTimestamps)
		totalConsumption = float(fileData[9][0])
		intervalDatum = totalConsumption/int(numberPoints)
		
	 	dataList = [intervalDatum for i in range(len(formattedTimestamps))]	
		d = {fileData[6][0]: dataList}
		data = DataFrame(d)	
		data['Timestamp'] = formattedTimestamps	
		data.to_csv(
			self.STORE_FILE_PATH_TEMPLATE % self.filename,
			index=False
			) 
		response = self.push_data_to_bos()
		return response
