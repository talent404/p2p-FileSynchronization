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

def longlist(path,conn):
	result = []
	for file in os.listdir(path):
		temp = getStats(file)
		result.append(temp)
	resultJson = json.dumps(result)
	conn.send(resultJson)
	pass

def shortlist(a,b,path,conn):
	result = []
	a = datetime.datetime.strptime(a,'%Y/%m/%d')
	b = datetime.datetime.strptime(b,'%Y/%m/%d')
	for file in os.listdir(path):
		temp = getStats(file)
		if datetime.datetime.fromtimestamp(temp['time']) >= a and datetime.datetime.fromtimestamp(temp['time']) <= b:
			result.append(temp)
	resultJson = json.dumps(result)
	conn.send(resultJson)
	pass

def regex(regExp,path,conn):
	result = []
	for file in os.listdir(path):
		if re.search(regExp,file):
			temp = getStats(file)
			result.append(temp)
	resultJson = json.dumps(result)
	conn.send(resultJson)
	pass

def checksum(fileName):
	return hashlib.md5(open(fileName,'rb').read()).hexdigest()

def verify(fileName,conn,path):
	result = []
	value = checksum(fileName)
	for file in os.listdir(path):
		if file == fileName:
			temp = getStats(file)
			result = [{'value':value,'time':temp['time']}]
	resultJson = json.dumps(result)
	conn.send(resultJson)

def checkall(conn,path):
	result = []
	for file in os.listdir(path):
		if os.path.isfile(file):
			temp = getStats(file)
			value = checksum(file)
			result.append({'name':file,'time':temp['time'],'value':value})
	resultJson = json.dumps(result)
	conn.send(resultJson)
	pass


def parseQuery(query,conn):
	command = query.split()
	if command[0] == "index":
		if command[1] == "longlist":
			longlist('.',conn)
		elif command[1] == "shortlist":
			shortlist(command[2],command[3],'.',conn)
		elif command[1] == "regex":
			regex(command[2],'.',conn)
	elif command[0] == "hash":
		if command[1] == "verify":
			verify(command[2],conn,'.')
		elif command[1] == "checkall":
			checkall(conn,'.')
	
port = 12341
server = socket.socket()
host = ""
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen(5)

while True:
	conn,addr = server.accept()
	query = conn.recv(1024)
	parseQuery(query,conn)
	conn.close()