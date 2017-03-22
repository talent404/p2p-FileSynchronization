import socket 
import json
import os
import datetime
import re
import hashlib


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
	hashlib.md5(open(fileName,'rb').read()).hexdigest()

def verify(fileName):
	value = checksum(fileName)
	for file in os.listdir(path):
		if file == fileName:
			temp = getStats(file)
			print value,temp['time']
def checkall():
	pass

def parseOutput(query,client,clientUdp):
	b = ''
	if query.split()[0] != "download":
		while True:
			a = client.recv(1024)
			b+=a
			if a[len(a)-1]==']':
				jsonOutput = json.loads(b)
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


def parseQuery(query):
	command = query.split()
	if command[0] == "index":
		if command[1] == "longlist":
			longlist('.')
		elif command[1] == "shortlist":
			shortlist(command[2],command[3],'.')
		elif command[1] == "regex":
			regex(command[2],'.')
	elif command[0] == "hash":
		if command[1] == "verify":
			verify(command[2])
		elif command[1] == "checkall":
			checkall()


host = ""
port = 12341
portUdp = 12342
client = socket.socket()

clientUdp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
clientUdp.bind((host,portUdp))

data = ['the letter a','the letter b']


while True:
	client = socket.socket()
	client.connect((host,port))
	query = raw_input("prompt>")
	client.send(query)	
	print "passed query"
	output = parseOutput(query,client,clientUdp)
	print "broken"
	client.close()
#fgdsfdsf
# sdf