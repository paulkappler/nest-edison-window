
import nest

#Nest Username and Password
username = 'user@domain.com'
password = 'password'

napi = nest.Nest(username, password)
structure = napi.structures[0]
device = structure.devices[0]
time_str = structure.weather.current.datetime.strftime('%Y-%m-%d %H:%M:%S')

print 'Away                           : %s' % structure.away
print 'Inside Temp                    : %s' % device.temperature
print 'Outside Temperature            : %s' % structure.weather.current.temperature

print 'Away Heat                      : %s' % device.away_temperature[0]
print 'Away Cool                      : %s' % device.away_temperature[1]

print 'Mode                           : %s' % device.mode
print 'Fan                            : %s' % device.fan
                                                                            
print 'online                         : %s' % device.online

windowOpen = False

if device.online:
    outsideTemperture = structure.weather.current.temperature
    insideTemperture  = device.temperature
    #default target is away temperature
    lowTarget = device.away_temperature[0]
    highTarget = device.away_temperature[1]
    
    if device.mode == "heat":
        lowTarget = device.target
        if outsideTemperture > insideTemperture:
            windowOpen = True
            print "heat mode and outside > inside open window"
    elif device.mode == "cool":
        highTarget = device.target
        if outsideTemperture < insideTemperture:
            windowOpen = True
            print "cool mode and outside < inside open window"
    elif device.mode == "range":
        lowTarget = device.target[0]
        highTarget = device.target[1]

    if insideTemperture > highTarget:
        if outsideTemperture < insideTemperture:
            windowOpen = True
            print "hot inside cooler outside open window"
    elif insideTemperture < lowTarget:
        if outsideTemperture > insideTemperture:
            windowOpen = True
            print "cool inside warmer outside open window"
    
    print 'High Target                    : %s' % highTarget
    print 'Low  Target                    : %s' % lowTarget
    print 'Window Open                    : %s' % windowOpen




