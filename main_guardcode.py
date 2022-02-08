#!/usr/bin/env python3

#This is the main code which will run the inferior threads.

from ppadb.client import Client as AdbClient
import time
from bs4 import BeautifulSoup
import urllib.request
from IPython.display import HTML
import smtplib
import facilities_mon as fm
import pressure_mon as pm
import json
import time
import threading
import sys
import tools


#Initializing starting variables.
print("Initializing settings...")

json_file_path_1="/home/eliade/Desktop/Annealing_Alarming/Python_Grafana/conf_files/main_conf.json"
json_file_path_2="/home/eliade/Desktop/Annealing_Alarming/Python_Grafana/conf_files/facilities_conf.json"
json_file_path_3="/home/eliade/Desktop/Annealing_Alarming/Python_Grafana/conf_files/vacuum_conf.json"
threads = []
stop = False


#Opening json file. Otherwise email.
try:
    with open(json_file_path_1,"r") as file:
        json_conf_1 = json.load(file)
    time.sleep(0.5)
    with open(json_file_path_2,"r") as file2:
    	json_conf_2=json.load(file2)
    time.sleep(0.5)
    with open(json_file_path_3,"r") as file3:
    	json_conf_3=json.load(file3)
    time.sleep(0.5)

except Exception as e:
    print("Cannot open json file. Reason: "+str(e))
    stop = True
    tools.SendEmail_mem()

time.sleep(1)


#Loading important values from json configuration file.
host =json_conf_1["InfluxDB"]["host"]
port =json_conf_1["InfluxDB"]["port"]
database = json_conf_1["InfluxDB"]["database"]
measurement = json_conf_1["InfluxDB"]["msr_name"]
url = json_conf_1["Call-Monitor_Variables"]["url"]
timeout = json_conf_1["Call-Monitor_Variables"]["timeout"]
thp = json_conf_1["Call-Monitor_Variables"]["thp"]
tht = json_conf_1["Call-Monitor_Variables"]["tht"]

time.sleep(1)


#Starting threads
try:
    
    x=threading.Thread(target=fm.Facilities_Monitoring,args = (host, port, database,url, timeout, lambda:stop,), name="Power_Out_Check")
    x.daemon=True
    threads.append(x)

    y=threading.Thread(target=pm.VacAlert, args =(thp, tht, host, port, database, measurement,  lambda: stop,), name="Vac_Alarm_Monitor")
    y.daemon=True
    threads.append(y)


    #Starting defined threads
    for i in threads:
        i.start()
        print("Starting "+str(i.name)+".\n")

    #Entering infinite loop
    while(True):
        time.sleep(30)

#If error encountered (example keyboard interrupt) code initializes closing procedures.
except:
    print("Sending STOP signal.")

    stop=True

    #Waiting for threads to successfully end.
    time.sleep(1)

    #When script ends, values get reset.
    print("Completing ending script protocols!")

    json_conf_2["Call-Monitor_Variables"]["UFT"]=0
    json_conf_2["Call-Monitor_Variables"]["UFM"]=0
    json_conf_3["Call-Monitor_Variables"]["PF"]=0
    json_conf_3["Call-Monitor_Variables"]["TF"]=0
    json_conf_2["Call-Monitor_Variables"]["CN"]=0
    json_conf_2["Call-Monitor_Variables"]["SEU"]=0

    with open(json_file_path_1,"w") as file:
        json.dump(json_conf_1, file,indent=2)
    with open(json_file_path_2,"w") as file:
        json.dump(json_conf_2, file,indent=2)
    with open(json_file_path_3,"w") as file:
        json.dump(json_conf_3, file,indent=2)
        
    time.sleep(1)

    print("Main Finishing Execution.")

    #Exiting program.
    sys.exit()




