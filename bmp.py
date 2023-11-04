import smbus
import time

bus = smbus.SMBus(1)

adc_address = 0x4b
# 8 bit to 8 bit ()
#thresh = 570/1024 * 256 - 20
thresh = 120
print(thresh)
count = 0
start_time = time.time()
beat = False

try:
    while True:
        count = 0
        cur_time = time.time()
        while cur_time - start_time < 10:
            data = bus.read_i2c_block_data(adc_address, 0)
            print((0, 255, data[0]))
            if data[0] > thresh:
                count += 1
                beat = True
                print ("beat!!")
            time.sleep(0.1)
            cur_time = time.time()
        start_time = time.time()
        print("BPM: %d" % (count*6))
except KeyboardInterrupt:
    pass


# Maintaining database for users (Name, BPM, timestamp)
# Showing the health of heart based on BPM
# Start and stop button
# Ask for BMI and see if the BPM is reasonable