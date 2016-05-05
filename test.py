#Nest Username and Password
username = 'user@domain.com'
password = 'password'


import mraa
import time
import nest
import sys
import traceback

print "Setup GPIO..."

opengpio = mraa.Gpio(15)
closegpio = mraa.Gpio(14)
closegpio.dir(mraa.DIR_OUT)
opengpio.dir(mraa.DIR_OUT)

window_is_open = False

def window_reset():
    """Clear window GPIO"""
    print "Window Reset..."

    opengpio.write(0)
    closegpio.write(0)
    time.sleep(0.1)

def window_close():
    """reset and close window"""
    window_reset()

    print "Window Close..."
    closegpio.write(1)
    time.sleep(0.5)
    closegpio.write(0)
    window_is_open = False

def window_open():
    """reset and open window"""
    window_reset()

    print "Window Open..."
    opengpio.write(1)
    time.sleep(0.5)
    opengpio.write(0)
    window_is_open = True

window_reset()


temperature_margin = 3.0

while True:
    try:

        window_should_open = False
        print "Setup Nest..."

        napi = nest.Nest(username, password)
        structure = napi.structures[0]
        device = structure.devices[0]


        if device.online:
            time_str = structure.weather.current.datetime.strftime('%Y-%m-%d %H:%M:%S')

            print 'Time                           : %s' % time_str
            print 'Away                           : %s' % structure.away
            print 'Inside Temp                    : %s' % device.temperature
            print 'Outside Temperature            : %s' % structure.weather.current.temperature

            print 'Away Heat                      : %s' % device.away_temperature[0]
            print 'Away Cool                      : %s' % device.away_temperature[1]

            print 'Mode                           : %s' % device.mode
            print 'Fan                            : %s' % device.fan

            print 'online                         : %s' % device.online

            outsideTemperture = structure.weather.current.temperature
            insideTemperture  = device.temperature
            #default target is away temperature
            lowTarget = device.away_temperature[0]
            highTarget = device.away_temperature[1]
            
            if device.mode == "heat":
                lowTarget = device.target
                if outsideTemperture > insideTemperture:
                    window_should_open = True
                    print "heat mode and outside > inside open window"
            elif device.mode == "cool":
                highTarget = device.target
                if outsideTemperture < insideTemperture:
                    if insideTemperture > (highTarget - temperature_margin):
                        window_should_open = True
                        print "cool mode and outside < inside open window"
            elif device.mode == "range":
                lowTarget = device.target[0]
                highTarget = device.target[1]

            if insideTemperture > highTarget:
                if outsideTemperture < insideTemperture:
                    window_should_open = True
                    print "hot inside cooler outside open window"
            elif insideTemperture < lowTarget:
                if outsideTemperture > insideTemperture:
                    window_should_open = True
                    print "cool inside warmer outside open window"
            
            print 'High Target                    : %s' % highTarget
            print 'Low  Target                    : %s' % lowTarget
            print 'Window Open                    : %s' % window_should_open

            if window_should_open:
                window_open()
            else:
                window_close()
    except Exception:
        traceback.print_exc()

    print "Sleep 15 minutes"
    sys.stdout.flush()
    time.sleep(60*15)








