import socket 
import json
import os
import datetime
import re
import hashlib

def getStats(fileName):
	temp = {}
	temp['time'] = os.stats(fileName).st_mtime
	temp['size'] = os.stats(fileName).st_size
	temp['name'] = fileName
	if os.path.isdir(fileName):
		temp['type'] = 'dir'
	else:
		temp['type'] = 'file'

def longlist(path,conn):
	result = []
	for file in os.path.listdir(path):
		temp = getStats(file)
		result.append(temp)
	resultJson = json.dumps(result)
	conn.send(resultJson)
	pass

def shortlist(a,b,path,conn):
	result = []
	for file in os.path.listdir(path):
		temp = getStats(file)
		if datetime.datetime.fortimestamp(temp['time']) >= a and datetime.datetime.fortimestamp(temp['time']) <= b:
			result.append(temp)
	resultJson = json.dumps(result)
	conn.send(resultJson)
	pass

def regex(regExp,path,conn):
	result = []
	for file in os.path.listdir(path):
		if re.search(regExp,file):
			temp = getStats(file)
			result.append(temp)
	
	pass

def checksum(fileName):
	hashlib.md5(open(fileName,'rb').read()).hexdigest()

def verify(fileName,conn):
	value = checksum(fileName)
	for file in os.listdir(path):
		if file == fileName:
			temp = getStats(file)
			print value,temp['time']
def checkall(conn):
	pass


def parseQuery(query,conn):
	command = query.split()
	if command[0] == "index":
		if command[1] == "longlist":
			longlist('.',conn)
		elif command[1] == "shortlist":
			shortlist(command[2],command[3],'.')
		elif command[1] == "regex":
			regex(command[2],'.')
	elif command[0] == "hash":
		if command[1] == "verify":
			verify(command[2])
		elif command[1] == "checkall":
			checkall()
