import mraa
import time

# Setup
opengpio = mraa.Gpio(15)
closegpio = mraa.Gpio(14) 

closegpio.dir(mraa.DIR_OUT)
opengpio.dir(mraa.DIR_OUT)

opengpio.write(0)
closegpio.write(0)
time.sleep(0.1)

opengpio.write(1)
time.sleep(0.5)
opengpio.write(0)



