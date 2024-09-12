from time import sleep,time,localtime,strftime
from sys import argv
from configparser import ConfigParser
from subprocess import check_output
from prettytable import PrettyTable

config = ConfigParser()
config.read('config.ini', 'utf-8')

npu_num = config.getint('DEFAULT', 'npu_num', fallback=8)
length = config.getint('DEFAULT', 'chart_his_max_length', fallback=30)
threshold1 = config.getint('DEFAULT', 'threshold1', fallback=20)
threshold2 = config.getint('DEFAULT', 'threshold2', fallback=70)


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


COLORS = {
	"red": "\033[1;31m",
	"green": "\033[1;32m",
	"yellow": "\033[1;33m",
	"blue": "\033[1;34m",
	"white": "\033[1;37m",
	"reset": "\033[0m"
}


def color_str(strings, color):
	strings = str(strings)
	return f"{COLORS[color]}{strings}{COLORS['reset']}"


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
    
	color_use = "green"
	if color_mem == "red" or color_utl == "red":
		color_use = "red"
	elif color_mem == "yellow" or color_utl == "yellow":
		color_use = "yellow"
	else :
		pass

	return [color_str(npu_x.id,color_use), color_str(npu_x.temp,color_use), color_str(npu_x.power,color_use), color_str(HBM,color_use), color_str(str(npu_x.ai_core)+"%",color_use), color_str(npu_x.health,color_health),color_str(His("MEM",npu_x.memory_use_percent*100),color_mem),color_str(His("UTL",utl),color_utl)]



def get_smi(is_watch,args):
	timestamp = time()
	npu_avg.avg_init()

	try:
		output = check_output(['npu-smi','info'])
	except Exception as e:
		print(f"Error executing npu-smi info: \n{e}")
		return False

	out = output.decode('utf-8')
	re = out.split('\n|')

	if "npu" in str(table.title):
		table.clear_rows()
	else:
		version = re[1].split('|')
		version = version[0].split(' ')
		version = version[2]

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
	return True


npu_avg = Npu("AVG")
npu_mapping = { i: Npu(i) for i in range(npu_num)}
table = PrettyTable()


if __name__ == '__main__':
	args = argv

	if "watch" in args:
		executing = True
		while executing:
			executing = get_smi("watch",args)
			sleep(1)
	else:
		get_smi("silence",args)
