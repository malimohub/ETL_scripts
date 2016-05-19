from calendar import monthrange 
from pandas import DataFrame 
import pandas
import sys
from datetime import datetime, timedelta
from pandas import date_range
import argparse



class BreakData(object):
	
	def __init__(self, dataMonth, dataYear,  monthTotalValue, bosID, filePath):
		self.dataMonth = dataMonth
		self.dataYear = dataYear
		self.monthTotalValue = monthTotalValue
		self.bosID = bosID
	 	self.filePath = filePath

	
	def get_month_number_days(self):
		monthData = monthrange(self.dataYear, self.dataMonth)
		numberOfDays = monthData[1]
		return numberOfDays

	def get_broken_out_data(self, numberOfDays, scale):
			dayValue = self.monthTotalValue * scale / float(numberOfDays)
			return dayValue 

	
	def save_data_to_csv(self, data):
		fileStatus = data.to_csv(self.filePath,index=False, cols=['timestamp', self.bosID]) 
		return fileStatus

	
	def break_out_the_data(self, scale):
		numberDays = self.get_month_number_days()
		start = str(self.dataYear) + '-' + str(self.dataMonth) + '-' + '01' 
		end = (datetime(self.dataYear, self.dataMonth, 1) + timedelta(days=numberDays) - timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
		monthRng = date_range(start, end, freq='15min')
		data = DataFrame(monthRng, columns=['timestamp'])
		value = self.get_broken_out_data(len(data['timestamp']), scale)		
		#print len(data['timestamp'])
		#print self.monthTotalValue
		data[self.bosID] = value
		fileSaveStatus = self.save_data_to_csv(data) 	
		return fileSaveStatus




def break_data(dataMonth, dataYear, monthTotalValue, scale,  bosID, filePath):
	print 'Progam Starting.....'	
	#print dataMonth
	dataSpread = BreakData(dataMonth, dataYear, monthTotalValue, bosID, filePath)
	data = dataSpread.break_out_the_data(scale)
	print 'Program Complete'

















if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Distribute monthly data in 15 minute intervals across entire month and save to .csv file' ) 
	parser.add_argument('-m', metavar='month', type=int, help='Month of provided data')
	parser.add_argument('-y', metavar='year', type=int, help='Year of provided data')
	parser.add_argument('-v', metavar='value', type=int, help='Value of data')
	parser.add_argument('-s', metavar='scale', type=int, default=1, help='Applied if data needs to be scaled')
	parser.add_argument('-id', metavar='BOS id', type=str, help='BuildingOS ID as found on overiew page')
	parser.add_argument('-f', metavar='filePath', type=str, help='Path to desired csv save location')
	args = parser.parse_args()
	function = break_data(args.m, args.y, args.v, args.s, args.id, args.f)
