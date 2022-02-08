# Annealing_Alarm

## This is a code description to better understand the system.

### Start servers:
start android debugging server: sudo adb start-server;

start influxdb server: sudo systemctl start influxdb;

### Scripts descriptions:

#### facilities_mon 
                    
                    Monitors:

                    -Internet - issues call;

                    -UPS remaining_time < 50 minutes - issues call;

                    -JSON loading - sends email;

                    -Connection to UPS - sends email.


#### vacmon_influx   

                    Monitors:

                    -Pressure value over limit - issues call;

                    -JSON loading - sends email;

                    -Connection to InfluxDB - sends email;

                    -Connection to measurement of InfluxDB - sends email;

                    -No data or corrupt data in InfluxDB - sends email.


#### tools 

                    Contains working functions:

                    -SIMCall - initiates phone call;

                    -UPS_rd - reads status of UPS;

                    -SendEmail - sends email when json config is loaded properly;

                    -SendEmail_mem() - sends email to alert that json config did not load properly.


#### main_guardcode - Main code that runs inferior threads;


#### app_conf.json - Configuration files;


### Hints and information:

Please change pathing in json_file_path variable in respective scripts when downloading this code to your PC.

For more questions contact George Nitescu, ELI-NP, ELIADE.