import pigpio
import time

class LCD:
    def __init__(self, DB=[20, 26, 16, 19], RS=13, E=21, verbose=0):
        self.verbose = verbose
        
        self.DB = DB
        self.RS = RS
        # 0: instruction register
        # 0: data register
        self.E = E

        # pigpio
        self.gpio = pigpio.pi()
        self._gpio_setup()

        # function_set
        self.data_length = 0
        # 0: 4 bit mode
        # 1: 8 bit mode
        self.display_lines = 1
        # 0: 1 line
        # 1: 2 lines
        self.rich_font = 0
        # 0: 5x8 dots
        # 1: 5x10 dots

        # display control
        self.display_enable = 1
        self.cursor_enable = 0
        self.blinking_enable = 0 
        
        # dispaly
        self.ddram = [' '] * 128
        self.ac = 0
        
        # display initialization
        self.initialization()

    def _gpio_setup(self):
        if self.verbose:
            print('gpio_setup')
        self.gpio.set_mode(self.RS, pigpio.OUTPUT)
        self.gpio.set_mode(self.E, pigpio.OUTPUT)
#         self.gpio.set_PWM_dutycycle(self.E, 10)
#         self.gpio.set_mode(self.E, pigpio.OUTPUT)
        for DB in self.DB:
            self.gpio.set_mode(DB, pigpio.OUTPUT)
        self.gpio_cleanup()         

    def gpio_cleanup(self):
        if self.verbose:
            print('gpio_cleanup')
        self.gpio.write(self.RS, 0)
        self.gpio.write(self.E, 0)
        for DB in self.DB:
            self.gpio.write(DB, 0)
            
    def initialization(self):
        if self.verbose:
            print('initialization')
        self._function_set()
        self.display_off()
        self.display_clear()
        self._entry_mode_set()
        self._display_control()
                
    def _function_set(self):
        if self.verbose:
            print('function_set')
        # interface 8 bit long
        inst = int( (1 << 5) | (1 << 4) )       
        for k in range(0,3):
            self._write_8b(inst, RS=0)
            time.sleep(0.01)
        # interface 4 bit long
        inst = int( (1 << 5) | (self.data_length << 4) | (self.display_lines << 3) | (self.rich_font << 2) )
        self._write_8b(inst, RS=0)
        self._write_4b(inst, RS=0)
    
    def display_off(self):
        if self.verbose:
            print('display_off')
        inst = int( (1 << 3) )
        self._write_4b(inst, RS=0)

    def _display_control(self):
        if self.verbose:
            print('display_control')
        inst = int( (1 << 3) | (self.display_enable << 2) | (self.cursor_enable << 1) | (self.blinking_enable << 0) )
        self._write_4b(inst, RS=0)
        
    def display_clear(self):
        if self.verbose:
            print('display_clear')
        # clear ddram
        self.ddram = [' '] * 128
        self.ac = 0
        # instruction
        inst = int(1)
        self._write_4b(inst, RS=0)
        time.sleep(0.01)

    def _entry_mode_set(self):
        if self.verbose:
            print('entry_mode_set')
        inst = int( (1 << 2) | (1 << 1) )
        self._write_4b(inst, RS=0)
        
    def return_home(self):
        if self.verbose:
            print('return home')
        # update DDRAM
        self.ac = 0
        # instruction
        inst = int( (1 << 1) )
        self._write_4b(inst, RS=0)
        time.sleep(0.005)
        
    def cursor_shift(self, direction):
        if self.verbose:
            print('cursor_shift')
        direction = self._shift(direction)
        # instruction
        inst = int( (1 << 4) | (direction << 2) )
        self._write_4b(inst, RS=0)
        
    def display_shift(self, direction):
        if self.verbose:
            print('display_shift')
        direction = self._shift(direction)
        # instruction
        inst = int( (1 << 4) | (1 << 3) | (direction << 2) )
        self._write_4b(inst, RS=0)
        
#     def display_rotate(self):
#         self.display_shift('left')
#         self.gpio.set_PWM_frequency(self.E, 10)
#         self.gpio.set_PWM_dutycycle(self.E, 64)
#         print(self.gpio.get_PWM_frequency(self.E))
        
    def _shift(self, direction):
        # direction
        # 0: left
        # 1: right
        # update DDRAM
        if (direction == 0) | (direction == 'left'):
            direction = 0
            self.ac = self.ac - 1
        else:
            direction = 1
            self.ac = self.ac + 1
        return direction
        
    def jump_line(self, line):
        if self.verbose:
            print('jump_line')
        if line == 1:
            self.set_ddram_address(0)
        else:
            self.set_ddram_address(64)
        
    def set_ddram_address(self, address):
        if self.verbose:
            print('set_ddram_address')
        # update DDRAM
        self.ac = address
        # instruction
        inst = int( (1 << 7) | address )
        self._write_4b(inst, RS=0)

    def write(self, data, RS=1):
        if self.verbose:
            print('write')
        for d in data:
            d0 = ord(d)
            # update DDRAM
            self.ddram[self.ac] = chr(d0)
            self.ac = self.ac + 1
            # instruction
            self._write_4b(d0,RS)

    def _write_4b(self, d, RS=1):
        if self.verbose:
            print('write_4b: ' + bin(d))
        self.gpio.write(self.RS, RS)
        # MSB part
        for k in range(0,4):
            self.gpio.write(self.DB[k], (d >> 7-k) & 1)
        self._data_ready()
        # LSB part
        for k in range(0,4):
            self.gpio.write(self.DB[k], (d >> 3-k) & 1)
        self._data_ready()

    def _write_8b(self, d, RS=1):
        if self.verbose:
            print('write_8b: ' + bin(d))
        self.gpio.write(self.RS, RS)
        for k in range(0,8):
            try:
                self.gpio.write(self.DB[k], (d >> 7-k) & 1)
            except IndexError:
                pass
        self._data_ready()
        
    def _data_ready(self):
        delay = 0.0001
        time.sleep(delay)
        self.gpio.write(self.E, 1)
        #time.sleep(delay)
        #input('press <ENTER> to continue')
        self.gpio.write(self.E, 0)
        
def main():
    lcd = LCD(verbose=1)
    lcd.write('Pieter-Jan is de man')
    lcd.cursor_shift('left')
    lcd.write('l')
    lcd.jump_line(2)
    lcd.write('OOH YEAH!!')
    print(lcd.ddram)

if __name__ == '__main__':
    try:
        main()
        input('Press <ENTER> to continue...')
    finally:
        lcd = LCD()
        lcd.gpio_cleanup()
