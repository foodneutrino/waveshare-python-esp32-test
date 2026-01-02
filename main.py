import framebuf
import ustruct

from machine import Pin, SPI
from time import sleep

class EPD:
    # Display commands
    PANEL_SETTING                  = 0x00
    POWER_SETTING                  = 0x01
    POWER_OFF                      = 0x02
    POWER_ON                       = 0x04
    BOOSTER_SOFT_START             = 0x06
    DEEP_SLEEP                     = 0x07
    DATA_START_TRANSMISSION_1      = 0x10
    DATA_STOP_TRANSMISSION         = 0x11
    DISPLAY_REFRESH                = 0x12
    DATA_START_TRANSMISSION_2      = 0x13 # Red Pixel Data
    LUT_FOR_VCOM                   = 0x20
    LUT_WHITE_TO_WHITE             = 0x21
    LUT_BLACK_TO_WHITE             = 0x22
    LUT_WHITE_TO_BLACK             = 0x23
    LUT_BLACK_TO_BLACK             = 0x24
    PLL_CONTROL                    = 0x30
    VCOM_AND_DATA_INTERVAL_SETTING = 0x50
    RESOLUTION_SETTING             = 0x61
    VCM_DC_SETTING                 = 0x82

    def __init__(self):
        self.spi_sck = Pin(12)
        self.spi_mosi = Pin(11)
        self.spi_miso = Pin(46) # Not connected, but SPI needs a definition

        self.width = 400
        self.height = 300

        self.spi = SPI(
            2, 
            baudrate=20000000, 
            polarity=0, 
            phase=0, 
            sck=self.spi_sck, 
            mosi=self.spi_mosi, 
            miso=self.spi_miso
        )
        print("SPI Bus Initialized successfully!")
        
        # Test digital pins
        self.cs_pin = Pin(10, Pin.OUT)
        self.dc_pin = Pin(9, Pin.OUT)
        self.reset_pin = Pin(13, Pin.OUT)
        self.busy_pin = Pin(14, Pin.IN)

        self.send_command(self.POWER_SETTING)
        self.send_command(self.PLL_CONTROL)
        self.send_data(0x3C)

        self.send_command(self.POWER_ON)
        # self.send_data2(b'\x27\x01\x00')

    LUT_ALL=[   0x01,	0x0A,	0x1B,	0x0F,	0x03,	0x01,	0x01,	
                0x05,	0x0A,	0x01,	0x0A,	0x01,	0x01,	0x01,	
                0x05,	0x08,	0x03,	0x02,	0x04,	0x01,	0x01,	
                0x01,	0x04,	0x04,	0x02,	0x00,	0x01,	0x01,	
                0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
                0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
                0x01,	0x0A,	0x1B,	0x0F,	0x03,	0x01,	0x01,	
                0x05,	0x4A,	0x01,	0x8A,	0x01,	0x01,	0x01,	
                0x05,	0x48,	0x03,	0x82,	0x84,	0x01,	0x01,	
                0x01,	0x84,	0x84,	0x82,	0x00,	0x01,	0x01,	
                0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
                0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
                0x01,	0x0A,	0x1B,	0x8F,	0x03,	0x01,	0x01,	
                0x05,	0x4A,	0x01,	0x8A,	0x01,	0x01,	0x01,	
                0x05,	0x48,	0x83,	0x82,	0x04,	0x01,	0x01,	
                0x01,	0x04,	0x04,	0x02,	0x00,	0x01,	0x01,	
                0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
                0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
                0x01,	0x8A,	0x1B,	0x8F,	0x03,	0x01,	0x01,	
                0x05,	0x4A,	0x01,	0x8A,	0x01,	0x01,	0x01,	
                0x05,	0x48,	0x83,	0x02,	0x04,	0x01,	0x01,	
                0x01,	0x04,	0x04,	0x02,	0x00,	0x01,	0x01,	
                0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
                0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
                0x01,	0x8A,	0x9B,	0x8F,	0x03,	0x01,	0x01,	
                0x05,	0x4A,	0x01,	0x8A,	0x01,	0x01,	0x01,	
                0x05,	0x48,	0x03,	0x42,	0x04,	0x01,	0x01,	
                0x01,	0x04,	0x04,	0x42,	0x00,	0x01,	0x01,	
                0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
                0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
                0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	
                0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	
                0x02,	0x00,	0x00,	0x07,	0x17,	0x41,	0xA8,	
                0x32,	0x30 ]

    # Hardware reset
    def reset(self):
        self.reset_pin.value(1)
        sleep(100/1000)
        self.reset_pin.value(0)
        sleep(2/1000)
        self.reset_pin.value(1)
        sleep(100/1000)

    def send_command(self, command):
        self.dc_pin.value(0)
        self.cs_pin.value(0)
        self.spi.write(bytearray([command]))
        self.cs_pin.value(1)

    def send_data(self, data):
        self.dc_pin.value(1)
        self.cs_pin.value(0)
        self.spi.write(bytearray([data]))
        self.cs_pin.value(1)

    # send a lot of data   
    def send_data2(self, data):
        self.dc_pin.value(1)
        self.cs_pin.value(0)
        self.spi.write(data)
        self.cs_pin.value(1)

    def ReadBusy(self):        
        while self.busy_pin.value() == 1: 
            sleep(20 / 1000)                
    
    def TurnOnDisplay(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xF7)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()
        
    def TurnOnDisplay_Fast(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xC7)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()
        
    def TurnOnDisplay_Partial(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xFF)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()
        
    def TurnOnDisplay_4GRAY(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xCF)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()

    def init(self):
        # EPD hardware init start
        self.reset()
        self.ReadBusy()

        self.send_command(self.DISPLAY_REFRESH) #SWRESET
        self.ReadBusy()

        # copied from 
        # https://github.com/waveshareteam/e-Paper/blob/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd4in2_V2.py
        self.send_command(0x21)  # Display update control
        self.send_data(0x40)
        self.send_data(0x00)

        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x05)

        self.send_command(0x11)  # data  entry  mode
        self.send_data(0x03)  # X-mode

        self.send_command(0x44) 
        self.send_data(0x00)
        self.send_data(0x31)  

        self.send_command(0x45) 
        self.send_data(0x00)
        self.send_data(0x00)  
        self.send_data(0x2B)
        self.send_data(0x01)

        self.send_command(0x4E) 
        self.send_data(0x00)

        self.send_command(0x4F) 
        self.send_data(0x00)
        self.send_data(0x00)  
        self.ReadBusy()

        return 0


    def Lut(self):
        self.send_command(0x32)
        for i in range(227):
            self.send_data(self.LUT_ALL[i])

        self.send_command(0x3F)
        self.send_data(self.LUT_ALL[227])

        self.send_command(0x03)
        self.send_data(self.LUT_ALL[228])

        self.send_command(0x04)
        self.send_data(self.LUT_ALL[229])
        self.send_data(self.LUT_ALL[230])
        self.send_data(self.LUT_ALL[231])

        self.send_command(0x2c)
        self.send_data(self.LUT_ALL[232])

    def getbuffer(self, fb_or_buf):
        """
        Convert a framebuf.FrameBuffer or bytearray to display buffer format.

        Args:
            fb_or_buf: Either a bytearray (used to create a MONO_HLSB FrameBuffer)
                       or a framebuf.FrameBuffer object

        Returns:
            bytearray ready to send to the display
        """
        # If it's already a bytearray/bytes, return it directly
        # (assumes MONO_HLSB format which matches display format)
        if isinstance(fb_or_buf, (bytearray, bytes)):
            return fb_or_buf

        # If it's a FrameBuffer, extract pixels into a new buffer
        buf = bytearray(int(self.width / 8) * self.height)
        # Fill with white (0xFF)
        for i in range(len(buf)):
            buf[i] = 0xFF

        # Copy pixels from FrameBuffer
        for y in range(self.height):
            for x in range(self.width):
                pixel = fb_or_buf.pixel(x, y)
                if pixel == 0:  # black pixel
                    buf[int((x + y * self.width) / 8)] &= ~(0x80 >> (x % 8))

        return buf
    
    def Clear(self):
        if self.width % 8 == 0:
            linewidth = int(self.width / 8)
        else:
            linewidth = int(self.width / 8) + 1

        self.send_command(0x24)
        self.send_data2(b'\xFF' * int(self.height * linewidth))

        self.send_command(0x26)
        self.send_data2(b'\xFF' * int(self.height * linewidth))

        self.TurnOnDisplay()

    def display(self, image):
        self.send_command(0x24)
        self.send_data2(image)

        self.send_command(0x26)
        self.send_data2(image)

        self.TurnOnDisplay()

    def display_Partial(self, Image):
        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x80)

        self.send_command(0x21)  # Display update control
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x80)

        self.send_command(0x44) 
        self.send_data(0x00)
        self.send_data(0x31)  
        
        self.send_command(0x45) 
        self.send_data(0x00)
        self.send_data(0x00)  
        self.send_data(0x2B)
        self.send_data(0x01)

        self.send_command(0x4E) 
        self.send_data(0x00)

        self.send_command(0x4F) 
        self.send_data(0x00)
        self.send_data(0x00) 

        self.send_command(0x24) # WRITE_RAM
        self.send_data2(Image)  
        self.TurnOnDisplay_Partial()

    def sleep(self):
        self.send_command(self.DEEP_SLEEP)  # DEEP_SLEEP
        self.send_data(0x01)

        sleep(2)

    def exit(self):
        self.spi.close()


def main():
    """
    Initialize an e-paper display and display a greeting message.
    
    This function creates an EPD (E-Paper Display) screen instance,
    initializes it, and displays "Hello World!" on the screen.
    
    Returns:
        None
    """
    edp = EPD()
    print("Resetting the screen...")
    edp.init()
    edp.Clear()

    buf = bytearray(edp.width * edp.height // 8)
    print(f"Created buffer of size: {len(buf)} bytes")
    fb = framebuf.FrameBuffer(buf, edp.width, edp.height, framebuf.MONO_HLSB)
    black = 0x00
    white = 0x01

    print("Displaying 'Hello World!' on the screen...")
    fb.fill(white)
    fb.text('Hello World',30,10,black)
    fb.pixel(30, 10, black)
    fb.hline(30, 30, 10, black)
    fb.vline(30, 50, 10, black)
    fb.line(30, 70, 40, 80, black)
    fb.rect(30, 90, 10, 10, black)
    fb.fill_rect(30, 110, 10, 10, black)
    for row in range(0,36):
        fb.text(str(row),0,row*8,black)
    fb.text('Line 36',0,288,black)
    print(f"Buffer content (first 512 bytes): {buf[:512]}")

    edp.display(edp.getbuffer(buf))
    edp.sleep()

if __name__ == "__main__":
    main()
