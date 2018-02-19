#!/usr/bin/python

import threading #import Thread, RLock #multi-threading
import time # for pause
import random #for random choice in dict

#define vars an lock
global global_magasin
global global_production_is_terminated
global global_consommation_is_terminated
global_magasin = {"burger":1,"salade":1,"coucous":1}
global_production_is_terminated = 0
global_consommation_is_terminated = 0

#permetra à la fonction stock de checker que les deux autres thread sont terminés


verrou = threading.RLock() #pour bloquer la ressource


class produire(threading.Thread):
    """
    Class qui permet de produire
    elle construit un thread,
    que l'on peut ensuite appeler via nomthread.start()
    """

    def __init__(self,Thread):
        """constructeur de la classe Produire retourne un objet Thread"""
        threading.Thread.__init__(self)
        
    def run(self):
        """Fonction de production, fournit 100 articles"""
        compteur = 0
        global global_production_is_terminated
        while compteur < 100 :
            # on prend au hasard un elem dans le dico (nom)
            #pas besoin deverrou car lecture seule
            i = random.choice(list(global_magasin.keys()))
            #on lock la ressource
            with verrou:
                #on ajoute au magasin
                global_magasin[i] += 1
            print("LOG : Produit :"+i) 

            attente = 0.2
            attente += random.randint(1,10)/100
            time.sleep(attente)
            compteur +=1
        print("LOG production terminée"+ "compteur" +str(compteur))
        global_production_is_terminated += 1
            
class consommer(threading.Thread):
    """
    Fonction de consomation, consomme 100 articles"
    """
    def __init__(self,Thread):
        """constructeur de la classe consommer retourne un objet Thread"""
        threading.Thread.__init__(self)
        
    def run(self):
        compteur = 0
        global global_consommation_is_terminated
        while compteur < 100 :
            while 1:
                #ce while sert à prendre un menu dispo, si le menu n'est pas dispo, plutot que d'attendre ;
                #on reprend tout de suite un autre menu
                i = random.choice(list(global_magasin.keys())) 
                with verrou:
                    #si notre menu est dispo, on le consomme
                    if global_magasin[i] > 0 :
                        global_magasin[i] -= 1
                        break
                    
            print("LOG : Consomé:"+i)
            attente = 0.2
            attente += random.randint(1,10)/100
            time.sleep(attente)
            compteur +=1

        print("LOG consommation terminée" + "compteur" +str(compteur))            
        global_consommation_is_terminated = 1
    
class stock(threading.Thread):
        """Class pour afficher les stock"""

        def __init__(self,Thread):
            """Constructeur de la classe stock, retourne un objet thread"""
            threading.Thread.__init__(self)

        def run(self):
            while 1:
                print("\nStocks :")
                for elem in global_magasin :
                        print( str(elem)+ ":" +str(global_magasin[elem]) ) 
                attente = 10
                time.sleep(attente)
                #si la prod et la conso sont terminés, on termine le thread
                print(global_production_is_terminated)
                print(global_consommation_is_terminated)
                if global_production_is_terminated == 1 and global_consommation_is_terminated == 1 :
                    print("\nLes stocks finaux sont :")
                    for elem in global_magasin :
                        print( str(elem)+ ":" +str(global_magasin[elem]) ) 

                    break


# Create two threads as follows
thread_produire = produire("Thread_produire")
thread_consommer = consommer("Thread_consommer")
thread_stock = stock("Thread_stock")

#on tente de les lancer
try:
    thread_produire.start()
    thread_consommer.start()
    thread_stock.start()
except:
   print ("Error: unable to start thread")

#on attends que les threads se terminnent
thread_produire.join()
thread_consommer.join()
thread_stock.join()
