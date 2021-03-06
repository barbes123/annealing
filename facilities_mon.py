#This will mainly monitor the UPS status and Internet Connection
import time
import requests
import json
from IPython.display import HTML
import tools
from ppadb.client import Client as AdbClient
import time
from bs4 import BeautifulSoup
import urllib.request
import smtplib
from influxdb import InfluxDBClient
from datetime import datetime



def Facilities_Monitoring (host, port, database,url, timeout,stop):
    
    #Defining json config file pathing. Change this when moving code from PC to PC.
    json_file_path = "/home/eliade/Desktop/Annealing_Alarming/Python_Grafana/conf_files/facilities_conf.json"


    #Checking if stop condition is active when first starting the code.
    if stop ():
        print("Conditions not met for facilities_mon.")
        
    else:
        #Enter while loop
        while(True):
            print("\n#############################\n")
            timeset=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

            #Opening json file and checking if it can open. Otherwise sending email
            try:   
                with open(json_file_path,"r") as file:
                    json_conf = json.load(file)
                
            except Exception as e:
                print("Cannot open json file. Reason: "+str(e))
                tools.SendEmail_mem()

            #Establishing InfluxDB connection and checking it. Sending email if no connection:
            try:
                client = InfluxDBClient(host=host,port=port,database=database)

            except Exception as e:
                print("Could not establish connection to InfluxDB server. Reason: " + str(e))
                tools.SendEmail(json_conf,"INF")
                tools.SendEmail_mem()



            #Checking UPS activation condition (time of battery is less than 50 min. Normal functioning parameters are battery life >50 min)

            #reading value and configuring alarm flag with its specific value.
            try:
                
                remaining_time,mode = tools.UPS_rd(json_conf)
                json_conf["Call-Monitor_Variables"]["SEU"] = 0
                print("Mode:"+mode)
                if "L" in mode:
                    mode=1
                elif "B" in mode:
                    mode=0

                
                
                json_data=[{
                    "measurement":"UPS_Annealing_Monitor",
                    "time":timeset,
                    "fields": {
                        "mode":mode,         
                        "remaining_time":remaining_time
                    }
                }]
                client.write_points(json_data)
                #Checking UPS mode
                if mode==0 and json_conf["Call-Monitor_Variables"]["UFM"]==0:
                    json_conf["Call-Monitor_Variables"]["UFM"]=1
                    #Initiating call sequence to the persons in charge as alarm is triggered. (Pause of 60 seconds between sequence calls.)
                    for phone in json_conf["Call-Monitor_Variables"]["phone_array"]:

                        for i in range(3):

                            tools.SIMCall(phone, json_conf)
                else:
                    json_conf["Call-Monitor_Variables"]["UFM"]=0
                    
                

                #Checking remaining time of UPS
                if remaining_time <= json_conf["Call-Monitor_Variables"]["remaining_time_th"] and json_conf["Call-Monitor_Variables"]["UFT"]==0:

                    json_conf["Call-Monitor_Variables"]["UFT"]=1
                    #Initiating call sequence to the persons in charge as alarm is triggered. (Pause of 60 seconds between sequence calls.)
                    for phone in json_conf["Call-Monitor_Variables"]["phone_array"]:

                        for i in range(3):

                            tools.SIMCall(phone, json_conf)

                else:
                    json_conf["Call-Monitor_Variables"]["UFT"]=0
                    
                print("UPS Remaining Time:"+str(remaining_time))
                                

            #Sending email if connection to UPS through network failed.
            except:
                if json_conf["Call-Monitor_Variables"]["SEU"] == 0:
                    tools.SendEmail(json_conf, "UPS")
                    json_conf["Call-Monitor_Variables"]["SEU"] = 1



            #Checking internet connection
            try:
                request = requests.get(url=url,timeout=timeout)

                print("\nConnection to Internet is active!\n")
                json_conf["Call-Monitor_Variables"]["SEN"] = 0

               

            except(requests.ConnectionError, requests.Timeout) as exception:
                
                print("No Internet connection detected!\n")
                
                #If request variable encountered an error, in this exception we will issue a call sequence, because of internet outage.
                if (json_conf["Call-Monitor_Variables"]["CN"] == 0):

                    for phone in json_conf["Call-Monitor_Variables"]["phone_array"]:

                        for i in range(3):

                            tools.SIMCall(phone, json_conf)
                            

                    json_conf["Call-Monitor_Variables"]["CN"]=1
                   


            #Checking stop condition.
            if stop():
                print("Stopping Initiated for facilities_mon!")
                time.sleep(1)
                break


            #Updating json file flags for alarms
            with open(json_file_path,"w") as file:
                json.dump(json_conf, file,indent = 2)
        

            #Waiting time
            time.sleep(30)



        
        
                
