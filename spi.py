import mraa
import time
print("loading SPI...")
class SPI:
    def __init__(self, selGPIO = 33):
        # Setup Gpio
        self.mosi = mraa.Gpio(31)#GP44
        self.miso = mraa.Gpio(45)#GP45
        self.ssell = mraa.Gpio(46)#GP47
        self.sclk = mraa.Gpio(32)#GP46
        self.sselw= mraa.Gpio(33)#GP48

        self.ssel= mraa.Gpio(selGPIO)

        self.mosi.dir(mraa.DIR_OUT_LOW)
        self.miso.dir(mraa.DIR_IN)
        self.ssell.dir(mraa.DIR_OUT_HIGH)
        self.sselw.dir(mraa.DIR_OUT_HIGH)
        self.sclk.dir(mraa.DIR_OUT_HIGH)


        #call get_status twice to clear then update flags after reset
        self.get_status()
        self.get_status()



    def sleepns(self,ns):
        time.sleep(ns/1000000000.0)

    def spi_raw(self,input):
        self.sclk.write(1)
        self.ssel.write(1)
        self.sleepns(350) #setup of chip select
        self.ssel.write(0)
        self.sleepns(10) #hold of chip select 10 

        output = 0
        for i in range(7,-1,-1):
            self.sclk.write(0)
            self.sleepns(25) #data setup time
            self.mosi.write( (input >> i) & 0x1 )
            output |= self.miso.read() << i 
            self.sleepns(100) #data hold=20ns and clock low=75ns
            self.sclk.write(1)
            self.sleepns(75) # clock high time

        self.ssel.write(1)
        self.sleepns(800)
        return output


    #L6470 Commands using spi_raw
    def get_param(self, param, length):
        self.spi_raw(0x20 | (0x1f & param))
        byte2 = 0
        byte1 = 0
        if length == 3:
            byte2 = self.spi_raw(0x0)
        if length >= 2:
            byte1 = self.spi_raw(0x0)
        byte0 = self.spi_raw(0x0)
        return byte0 | byte1 << 8 | byte2 << 16

    def set_param(self, param, value, length):
        self.spi_raw(0x1f & param)
        if length == 3:
            self.spi_raw(0xff & (value >> 16) )
        if length >= 2:
            self.spi_raw(0xff & (value >> 8) )
        self.spi_raw(0xff & value)


    def move(self, dir, value):
        self.spi_raw(0x40 | dir)
        self.spi_raw(0xff & (value >> 16) )
        self.spi_raw(0xff & (value >> 8) )
        self.spi_raw(0xff & value)

    def run(self, dir, spd):
        self.spi_raw(0x50 | dir)
        self.spi_raw(0x0f & (spd >> 16) )
        self.spi_raw(0xff & (spd >> 8) )
        self.spi_raw(0xff & spd)


    def go_to(self, value):
        self.spi_raw(0x60 )
        self.spi_raw(0xff & (value >> 16) )
        self.spi_raw(0xff & (value >> 8) )
        self.spi_raw(0xff & value)

    def go_until(self, dir, spd):
        #Go at spd until SW goes low, then copy position to mark
        self.spi_raw(0x8A | dir)
        self.spi_raw(0x0f & (spd >> 16) )
        self.spi_raw(0xff & (spd >> 8) )
        self.spi_raw(0xff & spd)

    def release_sw(self, dir):
        #Go at min speed until SW goes high, then copy position to mark
        #if min speed is too low use 5 step/s
        self.spi_raw(0x9A | dir)

    def go_home(self):
        self.spi_raw(0x70)

    def go_mark(self):
        self.spi_raw(0x78)



    def soft_hi_z(self):
        self.spi_raw(0xA0)                                

    def hard_hi_z(self):
        self.spi_raw(0xA8)

    def soft_stop(self):
        self.spi_raw(0xB0)


    def hard_stop(self):
        self.spi_raw(0xB8)


    def get_status(self):
        self.spi_raw(0xD0)
        byte1 = self.spi_raw(0x0)
        byte0 = self.spi_raw(0x0)
        self.status = byte0 | byte1 << 8
        return self.status

    def check_ocd(self):
        #Over Current Detection Active Low
        return (self.status & 0x1000) == 0

    def check_stall(self):
        #Parse last call to the status command for a stall
        #stall detection active low
        return (self.status & 0x6000) != 0x6000

    def check_busy(self):
        #Parse last call to the status command for a busy
        #busy active low
        return (self.status & 0x0002) == 0


    def check_uvlo(self):
        #Under Voltage Locout Active Low
        return (self.status & 0x0200) == 0

    def reset_pos(self):
        self.spi_raw(0xD8)     

    def get_pos(self):
        return self.get_param(1,3)

    def set_pos(self, pos):
        self.set_param(1,pos,3)

    def get_mark(self):
        return self.get_param(3,3)

    def set_mark(self, pos):
        self.set_param(3,pos,3)

    def get_acc(self):
        #acceleration step/s^2 = ACC*2^-40/tick^2 tick = 250 ns
        #resolution is 14.55 step/s^2
        #defaut is 0x08A
        return self.get_param(0x5,2)

    def set_acc(self, pos):
        self.set_param(0x5,pos,2)

    def get_dec(self):
        #acceleration step/s^2 = ACC*2^-40/tick^2 tick = 250 ns
        #resolution is 14.55 step/s^2
        #defaut is 0x08A
        return self.get_param(0x6,2)

    def set_dec(self, pos):
        self.set_param(0x6,pos,2)

    def reset_device(self):
        self.spi_raw(0xC0)

    def set_max_speed(self, max_speed):
        #step/sec = SPEED * 2^-28 / tick where tick is 250 ns
        #The available range is from 0 to 15625 step/s
        #resolution of 0.015 step/s.
        #default 0x41
        self.set_param(7,max_speed,2)

    def get_max_speed(self):
        return self.get_param(7,2)

    def get_ocd_th(self):
        return self.get_param(0x13,1)


    def set_ocd_th(self, value):
        # 0x0 = 375 mA
        # 0x1 = 750 mA
        # 0xE = 5.625A
        # 0xF = 6A
        #default 0x8 = 3.38 A
        self.set_param(0x13,value,1)

    def set_stall_th(self, value):
        #0x0 = 31.25 mA
        #0x1 = 62. mA
        #default 0x40 = 2.03 A
        #0x7F = 4 A
        self.set_param(0x14,value,1)

    def get_stall_th(self):
        return self.get_param(0x14,1)


    def set_sw_mode(self, soft):
        config = self.get_param(0x18, 2)
        soft_config = 0
        if soft:
            soft_config = 0x0010
        self.set_param(0x18, (config & 0xFFEF) | soft_config, 2)

    def get_sw_mode(self):
        return (self.get_param(0x18, 2) & 0x10) == 0x10

    def set_k_val_hold(self, value):
        self.set_param(0x9,value,1)

    def get_k_val_hold(self):
        return self.get_param(0x09,1)

    def set_k_val(self, k_val):
        self.set_param(0x9,k_val,1)                                     
        self.set_param(0xA,k_val,1)                                     
        self.set_param(0xB,k_val,1)                                     
        self.set_param(0xC,k_val,1)

    def quiet_hi_z(self):
        k_val = self.get_k_val_hold()
        while k_val > 0:
            k_val = k_val - 1
            self.set_k_val_hold(k_val)
        self.hard_hi_z()
        self.set_k_val_hold(self.k_val)

    def quiet_stop_from_hi_z(self):
        k_val = 0
        self.set_k_val_hold(0)
        self.soft_stop()
        self.busy_wait()
        while k_val < self.k_val:
            k_val = k_val + 1
            self.set_k_val_hold(k_val)

    def busy_wait(self):
        self.get_status()
        while self.check_busy():
            self.get_status()

    def open(self):
        self.quiet_stop_from_hi_z()
        self.go_mark()
        self.busy_wait()
        self.quiet_hi_z()

    def close(self):
        self.quiet_stop_from_hi_z()
        self.go_home()
        self.busy_wait()
        self.quiet_hi_z()

    def open_to(self, pos):
        self.quiet_stop_from_hi_z()
        self.go_to(0x3fffff - int(175000*pos))
        self.busy_wait()
        self.quiet_hi_z()



    def set_open(self):
        self.set_pos(0x3fffff - 175000)



    def default(self):
        self.k_val = 0x41
        self.quiet_hi_z()
        self.reset_device()
        self.set_max_speed(5)
        self.set_ocd_th(0x6) # just over 2 amps
        self.set_stall_th(0x25)
        self.set_k_val(self.k_val)
        self.set_acc(1)
        self.set_dec(1)
        self.set_mark(0x3fffff - 175000)



if __name__ == "__main__":
    windows = SPI()
    windows.default()
    lock = SPI(selGPIO = 46)
    lock.default()
    lock.set_k_val(128)
    lock.set_mark(600000)


