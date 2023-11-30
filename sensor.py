import smbus
import time
import numpy as np
import math
import random

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
time_interal_beat = []

#RMSSD ( 19ms - 48-50ms ) - ideal values
def calculate_rms():
    global time_interval_beat
    rms_arr = []
    for i in range(1, len(time_interval_beat)):
        rms_arr.append(round(abs(time_interval_beat[i] - time_interval_beat[i-1]),2))

    # Calculating RMSSD value
    rms = math.sqrt(np.square(rms_arr).mean())
    print("Time interval between successive beats for the past ten seconds\n",time_interval_beat)
    print("RMS array: ", rms_arr)

    return rms

try:
    while True:
        count = 0
        cur_time = time.time()

        time_interval_beat = []

        while cur_time - start_time < 10:

            #Read sensor input from ADC
            #data = bus.read_i2c_block_data(ADC_ADDRESS, 0)
            data = [random.randrange(0,255)]
            print(data[0])

            if data[0] > thresh:
                #BPM
                beat = time.time()
                print ("Beat: ", data[0])

                if count > 0:
                    time_interval_beat.append(round(abs((beat - prev_beat)*1000),2))

                prev_beat = beat
                count += 1

            time.sleep(0.15)
            cur_time = time.time()

        print("RMS: ", calculate_rms())
        print("BPM: %d" % (count*6))
        time.sleep(30)
        start_time = time.time()

except KeyboardInterrupt:
    pass


# Maintaining database for users (Name, BPM, timestamp)
# Showing the health of heart based on BPM
# Start and stop button
# Ask for BMI and see if the BPM is reasonable