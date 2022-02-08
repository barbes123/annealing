#this will monitor for pressure and temperature values that exceed a threshhold


from influxdb import InfluxDBClient
import time
import json
import tools
from ppadb.client import Client as AdbClient
import time
from bs4 import BeautifulSoup
import urllib.request
from IPython.display import HTML
import smtplib
import os



def VacAlert(thp,tht, host, port, database, measurement, stop):
    
    #Defining json config file pathing. Change this when moving code from PC to PC.
    json_file_path_1="/home/eliade/Desktop/Annealing_Alarming/Python_Grafana/conf_files/facilities_conf.json"
    json_file_path_2="/home/eliade/Desktop/Annealing_Alarming/Python_Grafana/conf_files/vacuum_conf.json"
	

    #Checking if stop condition is active when first starting the code.
    if stop ():
        print("Conditions not met for vacmon.")
        
    else:
        #Enter while loop
        while(True):
            print("\n#############################\n")


            #Opening json file and checking if it can open. Otherwise sending email
            try:
                #small pause to make sure the threads dont access the file at the same time and encounter error.
                time.sleep(0.5) 

                with open(json_file_path_1,"r") as file1:
                    json_conf_1 = json.load(file1)
                 
                with open(json_file_path_2,"r") as file2:
                    json_conf_2 = json.load(file2)

            except Exception as e:
                print("Cannot open json file. Reason: " + str(e))
                tools.SendEmail_mem()



            #Establishing InfluxDB connection and checking it. Sending email if no connection:
            try:
                client = InfluxDBClient(host=host,port=port,database=database)

            except Exception as e:
                print("Could not establish connection to InfluxDB server. Reason: " + str(e))
                tools.SendEmail(json_conf_1,"INF")




            #Initializing empty working code variables.
            data = []
            pressure = []
            temp = []
            



            #Querying InfluxDB measurement. If error, send email
            try:
                result=client.query('SELECT * FROM '+str(measurement))

            except Exception as e:
                print("Measurement not detected. Reason: " + str(e))
                result = 0
                print("Could not establish connection to InfluxDB server. Reason: " + str(e))
                tools.SendEmail(json_conf_1,"INF")



            #If query was successful
            if result:
                
                try:
                    headings = result.raw['series'][0]['columns']
                    #Retrieving last 20 entries
                    for entry in reversed(result.raw['series'][0]['values'][-20:]): 
                        data.append(entry)  

                except Exception as e:
                    #Send Email if retrieved data is not proper.
                    print("Could not retrieve data from active measurement. Reason: "+str(e))    
                    tools.SendEmail(json_conf_1,"INF")

                #Dividing extracted data into temperature and pressure sensors.
                for entry in data:

                    pressure.append(entry[-2])
                    temp.append(entry[-1])

                #Initializing counter for values over threshhold
                counter = 0
                #Checking extracted values for over limit values (pressure).
                for value in pressure:
                    #If a value is overlimit, the counter increments.
                    if value >= thp:
                        counter+=1

                    #If more than half the extracted values are over limit we trigger the alarm
                    if counter >= 10:
                        print("Threshhold value exceeded for pressure. Calling 3 time sequence.")
                        
                        #Checking alarm flags and updating.
                        if (json_conf_2["Call-Monitor_Variables"]["PF"] == 0):

                            json_conf_2["Call-Monitor_Variables"]["PF"] = 1

                            #Triggering call sequence
                            for phone in json_conf_1["Call-Monitor_Variables"]["phone_array"]:

                                for i in range(3):
                                    print ("Call"+str(i))
                                    tools.SIMCall(phone,json_conf_1)
                                    

                        break
                
                if counter <10:
                    print("\nNo problems detected in monitoring of pressure!")
                    json_conf_2["Call-Monitor_Variables"]["PF"] = 0

                #Resetting counter for values over threshhold
                counter = 0
                #Checking extracted values for over limit values (temperature).
                for value in temp:
                    #If a value is overlimit, the counter increments.
                    if value >= tht:
                        counter+=1

                    #If more than half the extracted values are over limit we trigger the alarm
                    if counter >= 10:
                        
                        #Checking alarm flags and updating.
                        if (json_conf_2["Call-Monitor_Variables"]["TF"] == 0):
                            print("Threshhold value exceeded for temperature. Calling 3 time sequence.")

                            json_conf_2["Call-Monitor_Variables"]["TF"] = 1

                            #Triggering call sequence
                            for phone in json_conf_1["Call-Monitor_Variables"]["phone_array"]:

                                for i in range(3):
                                    print ("Call"+str(i))
                                    tools.SIMCall(phone,json_conf_1)
                                    

                        break

                if counter<10:
                    print("No problems detected in monitoring of temperature!")
                    json_conf_2["Call-Monitor_Variables"]["TF"] = 0
                


            #Pause between read-outs
            time.sleep(30)


            #Checking stop condition.
            if stop():
                print("Stopping Initiated for vacmon_influx!")
                time.sleep(1)
                break


            #Updating json file flags for alarms
            with open(json_file_path_1,"w") as file:
                json.dump(json_conf_1, file,indent=2)
            with open(json_file_path_2,"w") as file:
                json.dump(json_conf_2, file,indent=2)




        
        





