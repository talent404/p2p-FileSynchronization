import socket 
import json
import os
import datetime
import re
import hashlib


def getStats(fileName):
	temp = {}
	temp['name'] = fileName
	temp['time'] = os.stat(fileName).st_mtime
	temp['size'] = os.stat(fileName).st_size
	if os.path.isdir(fileName):
		temp['type'] = 'dir'
	else:
		temp['type'] = 'file'
	return temp

def beautyPrint(jsonOutput):
	for fileStats in jsonOutput:
		for stat in fileStats:
			if stat=='time':
				print datetime.datetime.fromtimestamp(fileStats[stat]),
			else:
				print fileStats[stat],
		print "\n",
	pass

def checksum(fileName):
	return hashlib.md5(open(fileName,'rb').read()).hexdigest()

def verify(fileName,path):
	result = []
	value = checksum(fileName)
	for file in os.listdir(path):
		if file == fileName:
			temp = getStats(file)
			result = [{'value':value,'time':temp['time']}]
	return result

def checkall(path):
	result = []
	for file in os.listdir(path):
		if os.path.isfile(file):
			temp = getStats(file)
			value = checksum(file)
			result.append({'name':file,'time':temp['time'],'value':value})
	return result

def checkSync(Folder1,Folder2):
	downlaodList = []
	for stats in Folder1:
		for stats2 in Folder2:
			if stats['name'] == stats2['name'] and stats['value'] != stats2['value'] and stats['time'] <= stats2['time']:
				downlaodList.append(stats2)
	return downlaodList

def getList(client):
	output = client.send('hash checkall')
	return parseOutput('hash checkall',client,client,1) #clientUdp is not used so lite

def downloadFiles(client):
	downlaodList = checkSync(getList(client),checkall('.'))
	for files in downlaodList:
		client.send('download TCP '+files['name'])
		parseOutput('download TCP '+files['name'],client,client,0)


def parseOutput(query,client,clientUdp,returnValue):
	b = ''
	if query.split()[0] != "download":
		while True:
			a = client.recv(1024)
			b+=a
			if a[len(a)-1]==']':
				jsonOutput = json.loads(b)
				if returnValue==1:
					return jsonOutput
				beautyPrint(jsonOutput)
				break
	elif query.split()[0] == "download":
		if query.split()[1] == "TCP":
			with open(query.split()[2]+"_downloaded", 'wb') as f:
				while True:
					print('receiving data...')
					data = client.recv(1024)
					if not data:
						break
					f.write(data)
		elif query.split()[1] == "UDP":
			with open(query.split()[2]+"_downloaded",'wb') as f:
				while True:
					print "receiving data..."
					dataUdp , addrUdp = clientUdp.recvfrom(1024)
					print dataUdp
					udpEnd = client.recv(1024)
					print 'h'+udpEnd+'h'
					if udpEnd == "udpDone":
						f.write(dataUdp)
						break
					f.write(dataUdp)

host = ""
port = 12343
portUdp = 12344
client = socket.socket()

clientUdp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
clientUdp.bind((host,portUdp))

while True:
	client = socket.socket()
	client.connect((host,port))
	query = raw_input("prompt>")
	client.send(query)	
	print "passed query"
	output = parseOutput(query,client,clientUdp,0)
	print "broken"
	client.close()