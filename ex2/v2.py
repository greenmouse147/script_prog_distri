#!/usr/bin/python
# coding: utf-8
import threading #import Thread, RLock #multi-threading
import time # for pause
import random #for random choice in dict

import logging
#logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *


#define vars an lock
global global_ports_opened
global global_ports_closed
global global_ports_to_scan 
global global_address_to_scan
global_address_to_scan = ""
global_ports_opened = []
global_ports_closed = []
global_ports_to_scan = []

verrou = threading.RLock() #pour bloquer la ressource

def demandeobligatoire(question,typedem="text"):
	"""
		Fonction de demande d'input obligatoire
		Oblige l'utilisater à entrer une réponse différende de '' et qui correspond au type demandé
		Elle prend en argument le texte pour le input (question)
		le type de la var à renvoyer 
		Types : (typedem)
			text -> string
			pass -> string (Mais lors de la demande n'affiche pas ce qui est entré)
			int ->  Entier
		+ Gestion des erreur

		Renvoie la variable demandée (tempon)
	"""
	if typedem=="pass":
		while 1:
			tempon = getpass.getpass(question)
			if tempon != '': break
	elif typedem == "int":
		while 1:
			try:
				tempon = int(input(question))
				if tempon != '': break
			except:
				print("Veuillez entrer un nombre")
	else:
		while 1:
			tempon = input(question)
			if tempon != '': break
	return tempon


class scanner(threading.Thread):
	"""
	Class qui permet de scanner un port
	que l'on peut ensuite appeler via nomthread.start()
	"""

	def __init__(self,Thread):
		"""constructeur de la classe scanner
		retourne un objet Thread"""
		threading.Thread.__init__(self)
		
	def run(self):
		"""Fonction de scan"""
		global global_ports_opened
		global global_ports_closed
		global global_ports_to_scan
		global global_address_to_scan
		
		while len(global_address_to_scan) > 0 :
			#on lock la ressource
			with verrou:
				#on prend un port
				try : 
					dst_port = global_ports_to_scan.pop()
				except	:
					break
			
			response = sr1(IP(dst=global_address_to_scan)/TCP(dport=dst_port, flags="S"),verbose=False, timeout=10)

			if response:
				# flags is 18 if SYN,ACK received
				if response[TCP].flags == 18:
					global_ports_opened.append(dst_port)
			else : 
				global_ports_closed.append(dst_port)



print("##########MENU##########")
print("Script de Scan Syn scapy")
 
global_address_to_scan = demandeobligatoire("Entrez une adresse : ")

valide = False
while valide == False :
	print("1 : scanner un  port")
	print("2 : scanner un  range")
	
	choix = demandeobligatoire("Entrez une option: ",typedem="int")
	
	if choix == 1 :
		while 1 : 
			port = demandeobligatoire("Entrez un port : ", typedem="int")
			if port > 0 and port < 65535:
				global_ports_to_scan.append(port)
				valide  = True 
				break
			else : 
				print("Veuillez entrer un nombre entre 0 et 65535")
				
	elif choix == 2 :
		while 1 :
			range_min = demandeobligatoire("Entrez le premier port du range :", typedem='int')
			range_max = demandeobligatoire("Entrez le dernier du range :" , typedem='int')
			if range_min < range_max : 
				if range_min > 0 and range_min < 65534 :
					if range_max > 1 and range_max < 65535 : 
						for i in range(range_min,range_max+1) :
							global_ports_to_scan.append(i)
						valide = True
						break
					else : 
						print("ERROR : Le dernier port du range est incorrect")
				else :
					print("ERROR : Le premier port du range est incorrect")
			else :
				print("ERROR : le premier port est supérieur au dernier port du range")
	
print("########################")	
while 1 : 
	nbthread = demandeobligatoire("Combien de Thread, voulez vous utiliser ? ", typedem='int')
	if nbthread > 0 :
		break
	
#Création des threads
liste_thread = [] #liste contenant les thread
for i in range (0,nbthread): #on fait 200 thread
	liste_thread.append(scanner(str(i)))


	
for unthread in liste_thread : #lancement des threads
	try:
		unthread.start()
		time.sleep(0.01)
	except:
		print ("Error: unable to start thread %s" % unthread)	
 

for unthread in liste_thread : 
	unthread.join() #on attend que les thread soient finis
	  

print("Ports ouverts sur l'hote " + global_address_to_scan + ": " + str(global_ports_opened))
print("Ports fermés sur l'hote " + global_address_to_scan + ": "  + str(global_ports_closed))

