from time import sleep,time,localtime,strftime
import sys
from configparser import ConfigParser
import subprocess
from prettytable import PrettyTable

npu_num = 8
length = 30
threshold1 = 20
threshold2 = 70

config = ConfigParser()
file_name = 'config.ini'
config.read(file_name, 'utf-8')

sections = config.sections()
if len(sections) > 0:
	for i in sections:
		for j in config.options(i):
			arg_init = config[i][j]
			if arg_init == "npu_num":
				npu_num = int(arg_init)
			elif arg_init == "chart_his_max_length":
				length = int(arg_init)
			elif arg_init == "use_threshold1":
				threshold1 = int(arg_init)
			elif arg_init == "use_threshold1":
				threshold2 = int(arg_init)

class Npu():
	def __init__(self, id):
		self.id = id
		self.model = "ascent ?"
		self.temp = -274
		self.power = -1.0
		self.max_memory = -1
		self.memory_use = -1
		self.memory_use_percent = -1.0
		self.ai_core = -1
		self.cpu_use = -1.0
		self.health = "-1"
		self.process = list()

	def info(self):
		print("npu info:")
		print("id:"+str(self.id))
		print("model:"+str(self.model))
		print("temp:"+str(self.temp))
		print("power:"+str(self.power))
		print("max_memory:"+str(self.max_memory))
		print("memory_use:"+str(self.memory_use))
		print("memory_use_percent:"+str(100*self.memory_use_percent)+"%")
		print("ai_core:"+str(self.ai_core))
		print("health:"+str(self.health))

	def avg_init(self):
		self.temp = "NA"
		self.power = 0.0
		self.max_memory = 0
		self.memory_use = 0
		self.memory_use_percent = 0.0
		self.ai_core = 0
		self.cpu_use = 0.0
		self.health = "UNKNOWN"

def color_str(strings, color):
	strings = str(strings)
	if color == "red":
		strings = "\033[1;31m" + strings + "\033[0m"
	elif color == "green":
		strings = "\033[1;32m" + strings + "\033[0m"
	elif color == "yellow":
		strings = "\033[1;33m" + strings + "\033[0m"
	elif color == "blue":
		strings = "\033[1;34m" + strings + "\033[0m"
	elif color == "white":
		strings = "\033[1;37m" + strings + "\033[0m"
	return strings

def His(name,value):
	per = str(round(value,1))
	len1 = round(value * length / 100)
	len2 = length - len1 + 6 - len(per)
	his = name + ": " + "\u2588" * len1 + " " * len2 + per + "%"
	return his

def Threshold(value):
	if value <= threshold1:
		return "green"
	elif value <= threshold2:
		return "yellow"
	else :
		return "red"

def color_row(npu_x):
	color_mem = Threshold(npu_x.memory_use_percent * 100)
	color_utl = Threshold(npu_x.ai_core)
	utl = npu_x.ai_core
	if npu_x.health == "OK":
		color_health = "green"
	elif npu_x.health == "Warning":
		color_health = "yellow"
	elif npu_x.health == "Alarm" or npu_x.health == "Critical" or npu_x.health == "UNKNOWN":
		color_health = "red"

	HBM = str(npu_x.memory_use) + ' / ' + str(npu_x.max_memory)
	if color_mem == "red" or color_utl == "red":
		return [color_str(npu_x.id,"red"), color_str(npu_x.temp,"red"), color_str(npu_x.power,"red"), color_str(HBM,"red"), color_str(str(npu_x.ai_core)+"%","red"), color_str(npu_x.health,color_health),color_str(His("MEM",npu_x.memory_use_percent*100),color_mem),color_str(His("UTL",utl),color_utl)]
	elif color_mem == "yellow" or color_utl == "yellow":
		return [color_str(npu_x.id,"yellow"), color_str(npu_x.temp,"yellow"), color_str(npu_x.power,"yellow"), color_str(HBM,"yellow"), color_str(str(npu_x.ai_core)+"%","yellow"), color_str(npu_x.health,color_health),color_str(His("MEM",npu_x.memory_use_percent*100),color_mem),color_str(His("UTL",utl),color_utl)]
	else :
		return [color_str(npu_x.id,"green"), color_str(npu_x.temp,"green"), color_str(npu_x.power,"green"), color_str(HBM,"green"), color_str(str(npu_x.ai_core)+"%","green"), color_str(npu_x.health,color_health),color_str(His("MEM",npu_x.memory_use_percent*100),color_mem),color_str(His("UTL",utl),color_utl)]

def get_smi(is_watch,args):
	table = PrettyTable()

	timestamp = time()
	output = subprocess.check_output(['npu-smi','info'])
	out = output.decode('utf-8')
	re = out.split('\n|')

	version = re[1].split('|')
	version = version[0].split(' ')
	version = version[2]

	npu_avg.avg_init()

	table.title = "npu-smi " + version
	table.field_names = ['NPU','Temp(C)','Pow(W)',' HBM-Usage(MB) ','NPU-Util',' Health ',"Memory Utilization","NPU Utilization"]

	for i in range(4,npu_num*2+4,2):
		tem = re[i].split('|')
		tem0 = tem[0].split(' ')
		tem0 = [x for x in tem0 if x != '']
		tem_id = int(tem0[0])
		npu_mapping[tem_id].model = str(tem0[1])
		tem1 = tem[1].split(' ')
		tem1 = [x for x in tem1 if x != '']
		npu_mapping[tem_id].health = str(tem1[0])
		tem2 = tem[2].split(' ')
		tem2 = [x for x in tem2 if x != '']
		npu_mapping[tem_id].power = float(tem2[0])
		npu_mapping[tem_id].temp = int(tem2[1])
	
		tem = re[i+1].split('|')
		tem2 = tem[2].split(' ')
		tem2 = [x.replace('/','') for x in tem2 if x != '' and x != '/']
		npu_mapping[tem_id].ai_core = int(tem2[0])
		npu_mapping[tem_id].memory_use = int(tem2[3])
		npu_mapping[tem_id].max_memory = int(tem2[4])
		npu_mapping[tem_id].memory_use_percent = round(float(tem2[3]) / float(tem2[4]), 3)
	
		npu_avg.power = npu_avg.power + npu_mapping[tem_id].power
		npu_avg.max_memory = npu_avg.max_memory + npu_mapping[tem_id].max_memory
		npu_avg.memory_use = npu_avg.memory_use + npu_mapping[tem_id].memory_use
		npu_avg.ai_core = npu_avg.ai_core + npu_mapping[tem_id].ai_core
		
		table.add_row(color_row(npu_mapping[tem_id]))
	
	if is_watch == "watch":
		print("\033[H")
		print("\033[1B")
		print("\033[J")

		local_time = localtime(timestamp)
		formatted_time = strftime("%Y-%m-%d %H:%M:%S", local_time)

		print(formatted_time + ' ' * 122 +"Press " + color_str("q","red") + " to quit")

	npu_avg.power = round(npu_avg.power,1)
	npu_avg.memory_use_percent = round(npu_avg.memory_use/npu_avg.max_memory,3)
	npu_avg.memory_use = round(npu_avg.memory_use,1)
	npu_avg.ai_core = round(npu_avg.ai_core/8)
	npu_avg.health = "OK"
	table.add_row(color_row(npu_avg))
	print(table)

if __name__ == '__main__':
	npu0 = Npu(0)
	npu1 = Npu(1)
	npu2 = Npu(2)
	npu3 = Npu(3)
	npu4 = Npu(4)
	npu5 = Npu(5)
	npu6 = Npu(6)
	npu7 = Npu(7)
	npu_avg = Npu("AVG")

	npu_mapping = {
		0: npu0,
		1: npu1,
		2: npu2,
		3: npu3,
		4: npu4,
		5: npu5,
		6: npu6,
		7: npu7,
	}

	args = sys.argv

	if args.count("watch") >= 1:
		while True:
			get_smi("watch",args)
			sleep(1)
	else:
		get_smi("silence",args)
