import smbus
import time
import numpy as np
import math
from statistics import *

bus = smbus.SMBus(1)

ADC_ADDRESS = 0x4b

# 8 bit to 8 bit ()
#thresh = 570/1024 * 256 - 20
thresh = 120
prev_beat = 0

print("Threshold set at ",thresh)
count = 0
start_time = time.time()
beat = 0

try:
    while True:
        count = 0
        cur_time = time.time()
        
        time_interval_beat = []
        rms_arr = []
        
        while cur_time - start_time < 10:
    
            #Read sensor input from ADC
            data = bus.read_i2c_block_data(ADC_ADDRESS, 0)
            print(data[0])
            
            if data[0] > thresh:
                #BPM
                beat = time.time()
                print ("Beat: ", data[0])
                
                #RMSSD ( 19ms - 48-50ms ) - ideal values
                if count > 0:
                    time_interval_beat.append(round(abs((beat - prev_beat)*1000),2))
                
                prev_beat = beat
                count += 1
            
            time.sleep(0.15)
            cur_time = time.time()
            
        # Calculating RMSSD value
        
        for i in range(1, len(time_interval_beat)):
            rms_arr.append(abs(time_interval_beat[i] - time_interval_beat[i-1]))
        
        rms = math.sqrt(np.square(rms_arr).mean())
        print("Time interval between successive beats for the past ten seconds\n",time_interval_beat)
        print("\n", rms_arr)
        print("RMSSD: ", rms)
        print("BPM: %d" % (count*6))
        time.sleep(3)
        start_time = time.time()
except KeyboardInterrupt:
    pass


# Maintaining database for users (Name, BPM, timestamp)
# Showing the health of heart based on BPM
# Start and stop button
# Ask for BMI and see if the BPM is reasonable