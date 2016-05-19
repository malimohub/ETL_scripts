import argparse 
import openpyxl
import os 
import pandas as pd 
from pandas import DataFrame 
from datetime import timedelta



class WbParser(object):

	def __init__(self, dataCoordinates, titles_to_ignore):
		self.dataCoordinates = dataCoordinates
		self.titles_to_ignore = titles_to_ignore


	def get_workbooks(self):
		filesDir = os.getcwd()
		files = os.listdir(filesDir)
		workbooks = [{f: openpyxl.load_workbook(filesDir +'/' + f)} for f in files if '.xlsx' in f or '.xlsm' in f or '.xltx' in f or ',.xltm' in f]
		return workbooks


	def get_workbook_sheets(self, workbooks):
		listOfWorkbooks = [{wb.keys()[0]: {wb.values()[0]: wb.values()[0].get_sheet_names()}} for wb in workbooks]
		 
		for wbDict in listOfWorkbooks:
			fileName = wbDict.keys()[0]
			for sheetName in wbDict[fileName][wbDict[fileName].keys()[0]]:
				if sheetName in self.titles_to_ignore:
					del wbDict[fileName][wbDict[fileName].keys()[0]][wbDict[fileName][wbDict[fileName].keys()[0]].index(sheetName)]
			
			
		return listOfWorkbooks
	

	def get_workbook_data(self, workbookSheets):
		dataCoords = self.dataCoordinates.split(',')
		for workbookData in workbookSheets:
			fileName = workbookData.keys()[0]
			wb = workbookData[fileName].keys()[0]
			sheetTitles = workbookData[fileName][wb]  
			
			for sheet in sheetTitles:
				#testWorkSheetTitle = workbookData[workbook][0]
				sheets = wb.get_sheet_by_name(sheet)
				startDateDataTuple = sheets[dataCoords[0]:dataCoords[1]]
				energyCapDataTuple  = sheets[dataCoords[2]: dataCoords[3]]
				startDates = []
				energyCapData = []
				for startDataList in startDateDataTuple:
					for startData in startDataList:
						startDates.append(startData.value)
			
				endDates = [startDate + timedelta(-1) for startDate in startDates]
				del endDates[0]
				del startDates[-1]
				dateData = {'StartDate': startDates}
				data = DataFrame (dateData)
				data['EndDate'] = endDates
				cost = []
				energyCapData = []
				for energyCapDataList in energyCapDataTuple:
					for energyCapDatum in energyCapDataList:
						ecValue = energyCapDatum.value
						if type(ecValue) == long or type(ecValue) == int or type(ecValue) == float:
							energyCapData.append(ecValue)
							if 'ELEC' in fileName:
								cost.append(ecValue*0.0537)
							elif 'GAS' in fileName:
								cost.append(ecValue*.975) 
						else:
							valuePosition = len(energyCapData)
							print 'Please correct data point in ' + str(sheets.title) + ' on ' + str(startDates[valuePosition]) 
							cost.append(0)
							energyCapData.append(0)
				if 'ELEC' in fileName:
					data['ConsumptionUnit'] = 'kWh'
					meterId = sheets.title + '_electricity'
					data['Meterid'] = meterId
					data['AccountNumber'] = sheets.title + '_electrical_bills'
				elif 'GAS' in fileName:
					data['ConsumptionUnit'] = 'therms'
					meterId = sheets.title + '_gas'
					data['Meterid'] = meterId
					data['AccountNumber'] = sheets.title + '_gas_bills'

				data['Consumption'] = energyCapData
				data['Cost'] = cost
				data = data.set_index('StartDate')	
				data.to_csv(meterId +'.csv', header=['EndDate', 'ConsumptionUnit', 'Meterid', 'AccountNumber', 'Consumption', 'Cost'])

		return data


	def pull_workbook_data(self):
		workbooks = self.get_workbooks()
	
		#testFile = [workbooks[0]]
		workbookSheets = self.get_workbook_sheets(workbooks) 
		workbookData = self.get_workbook_data(workbookSheets)


		return workbookData
		

				
					



def parse_workbooks(dataCoordinates, ignore):
	titles_to_ignore = ignore.split(',')
	print 'The following sheets will be ignored: ' 
	print titles_to_ignore
	print 'First StartDate Cell Coordinates Entered: ' +  dataCoordinates
	parser = WbParser(dataCoordinates, titles_to_ignore)
	data = parser.pull_workbook_data()
	print data



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Extract & Upload Bill data that is contained in excel workbooks with multiple sheets' )
	parser.add_argument('-dataCoords', metavar='Start Date Cell Coordinates', type=str, help='Please enter the cell coordinates for the first start date value for bill data') 
	parser.add_argument('-ignore', metavar='Sheets to Ignore', type=str, help='Enter the title of the sheets you would like to ignore. Enclose list of sheet titles with single quotes.')
	args = parser.parse_args()
	function = parse_workbooks(args.dataCoords, args.ignore)


