import pickle
import requests
import spi

windows_pos = 0
lock_pos = 0

try:
    with open('objs.pickle') as f:
        [windows_pos,lock_pos] = pickle.load(f)
        
except:
    print("file not found using defaults")
    
windows = spi.SPI()
windows.default()
windows.set_pos(windows_pos)


lock = spi.SPI(selGPIO = 46)
lock.default()
lock.set_k_val(128)
lock.set_mark(600000)
lock.set_pos(lock_pos)

r = requests.get("https://autodiscover.kappler.us/internet_test/id/5")

print (r.text)

windows_pos = windows.get_pos()
lock_pos = lock.get_pos()

with open('objs.pickle', 'w') as f:
    pickle.dump([windows_pos,lock_pos], f)
