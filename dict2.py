import socket 
import json
import os
import datetime
import re
import hashlib

def getStats(fileName,path):
	temp = {}
	temp['name'] = fileName
	temp['time'] = os.stat(path+'/'+fileName).st_mtime
	temp['size'] = os.stat(path+'/'+fileName).st_size
	temp['permissions'] = oct(os.stat(path+'/'+fileName).st_mode & 0777)
	print temp['permissions']
	if os.path.isdir(path+'/'+fileName):
		temp['type'] = 'dir'
	else:
		temp['type'] = 'file'
	return temp

def longlist(path,conn):
	result = []
	for file in os.listdir(path):
		temp = getStats(file,path)
		result.append(temp)
	resultJson = json.dumps(result)
	conn.send(resultJson)
	pass

def shortlist(a,b,path,conn):
	result = []
	a = datetime.datetime.strptime(a,'%Y/%m/%d')
	b = datetime.datetime.strptime(b,'%Y/%m/%d')
	for file in os.listdir(path):
		temp = getStats(file,path)
		if datetime.datetime.fromtimestamp(temp['time']) >= a and datetime.datetime.fromtimestamp(temp['time']) <= b:
			result.append(temp)
	resultJson = json.dumps(result)
	conn.send(resultJson)
	pass

def regex(regExp,path,conn):
	result = []
	for file in os.listdir(path):
		if re.search(regExp,file):
			temp = getStats(file,path)
			result.append(temp)
	resultJson = json.dumps(result)
	conn.send(resultJson)
	pass

def checksum(fileName,path):
	return hashlib.md5(open(path+'/'+fileName,'rb').read()).hexdigest()

def verify(fileName,conn,path):
	result = []
	value = checksum(fileName,path)
	for file in os.listdir(path):
		if file == fileName:
			temp = getStats(file,path)
			result = [{'value':value,'time':temp['time']}]
	resultJson = json.dumps(result)
	conn.send(resultJson)

def checkall(conn,path):
	result = []
	for file in os.listdir(path):
		if os.path.isfile(path+'/'+file):
			temp = getStats(file,path)
			value = checksum(file,path)
			result.append({'name':file,'time':temp['time'],'value':value,'permissions':temp['permissions']})
	resultJson = json.dumps(result)
	conn.send(resultJson)
	pass

def tcpDownload(path,conn,fileName):
	file = open(path+'/'+fileName,'rb')
	tempBytes = file.read(1024)
	while tempBytes:
		conn.send(tempBytes)
		tempBytes = file.read(1024)
	file.close()
	pass

def udpDownload(path,serverUdp,portUdp,conn,fileName):
	file = open(path+'/'+fileName,'rb')
	tempBytes = file.read(1024)
	while tempBytes:
		serverUdp.sendto(tempBytes,("",portUdp))
		tempBytes = file.read(1024)
	file.close()
	conn.send('udpDone')
	pass

def parseQuery(query,conn,serverUdp,portUdp,path):
	command = query.split()
	if command[0] == "index":
		if command[1] == "longlist":
			longlist(path,conn)
		elif command[1] == "shortlist":
			shortlist(command[2],command[3],path,conn)
		elif command[1] == "regex":
			regex(command[2],path,conn)
	elif command[0] == "hash":
		if command[1] == "verify":
			verify(command[2],conn,path)
		elif command[1] == "checkall":
			checkall(conn,path)
	elif command[0] == "download":
		if command[1] == "TCP":
			tcpDownload(path,conn,command[2])
		elif command[1] == "UDP":
			udpDownload(path,serverUdp,portUdp,conn,command[2])	
port = 20000
portUdp = 20001

server = socket.socket()
serverUdp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

host = ""

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen(5)


while True:
	conn,addr = server.accept()
	query = conn.recv(1024)
	parseQuery(query,conn,serverUdp,portUdp,'folder2')
	conn.close()