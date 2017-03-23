import socket 
import json
import os
import datetime
import re
import hashlib
import time 

def getStats(fileName,path):
	temp = {}
	temp['name'] = fileName
	temp['time'] = os.stat(path+'/'+fileName).st_mtime
	temp['size'] = os.stat(path+'/'+fileName).st_size
	if os.path.isdir(path+'/'+fileName):
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

def checksum(fileName,path):
	return hashlib.md5(open(path+'/'+fileName,'rb').read()).hexdigest()

def verify(fileName,path):
	result = []
	value = checksum(fileName,path)
	for file in os.listdir(path):
		if file == fileName:
			temp = getStats(file,path)
			result = [{'value':value,'time':temp['time']}]
	return result

def checkall(path):
	result = []
	for file in os.listdir(path):
		if os.path.isfile(path+'/'+file):
			temp = getStats(file,path)
			value = checksum(file,path)
			result.append({'name':file,'time':temp['time'],'value':value})
	return result

def checkSync(Folder2,Folder1):
	downlaodList = []
	count = 0
	for stats2 in Folder2:
		for stats in Folder1:
			if stats['name'] == stats2['name'] and stats['value'] != stats2['value'] and datetime.datetime.fromtimestamp(stats2['time'])<= datetime.datetime.fromtimestamp(stats['time']):
				downlaodList.append(stats2)
			elif stats2['name']!=stats['name']:
				count+=1
		if count == len(Folder1):
			downlaodList.append(stats2)
			count = 0

	return downlaodList

def getList(client):
	output = client.send('hash checkall')
	ass =  parseOutput('hash checkall',client,client,1) #clientUdp is not used so lite
	client.close()
	return ass

def downloadFiles(client,path):
	downlaodList = checkSync(getList(client),checkall(path))
	for files in downlaodList:
		client = socket.socket()
		client.connect((host,port))
		client.send('download TCP '+files['name'])
		parseOutput('download TCP '+files['name'],client,client,0)
		print files['permissions']
		os.chmod(path+'/'+files['name'],int(files['permissions'],8))
		client.close()


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
			with open('folder1/'+query.split()[2], 'wb') as f:
				while True:
					print('receiving data...')
					data = client.recv(1024)
					if not data:
						break
					f.write(data)
		elif query.split()[1] == "UDP":
			with open(query.split()[2],'wb') as f:
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
port = 20000
portUdp = 20001
client = socket.socket()

startTime = time.time()

clientUdp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
clientUdp.bind((host,portUdp))

while True:
	client = socket.socket()
	client.connect((host,port))
	query = raw_input("prompt>")

	currentTime = time.time()
	if currentTime-startTime > 10:
		downloadFiles(client,'folder1')
		startTime = currentTime
	else:
		client.send(query)	
		print "passed query"
		output = parseOutput(query,client,clientUdp,0)
		print "broken"
		client.close()