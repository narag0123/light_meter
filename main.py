from time import sleep, ticks_ms, ticks_diff
from machine import Pin, SPI, I2C
from lib.ssd1351 import SSD1351

from lib.bh1750 import BH1750
from ev_calc import ExposureCalculator
from lib.fraction import Fraction
from switch_mode import ToggleSwitch

from font.font_loop import font_display_roboto_black_12
from font.font_loop import font_display_roboto_black_20
from font.font_loop import font_display_roboto_black_30
from font.font_loop import font_display_roboto_black_40
from font.font_loop import font_display_roboto_black_50

from font.font_loop import font_display_roboto_normal_10

YELLOW = 0x00D5FF
PURPLE = 0xF0F000
WHITE = 0xFFFFFF
BLACK = 0x000000
RED = 0x00FF00
BLUE = 0xFF0000
GREEN = 0x0000FF


# SPI DISPLAY SETTING
sck = Pin(10)
mosi = Pin(11)
cs = Pin(13)
dc = Pin(12)
rst = Pin(14)
spi = SPI(1, baudrate=10000000, polarity=0, phase=0, sck=sck, mosi=mosi)
# OLED INIT
oled = SSD1351(128, 128, spi, cs, dc, rst)
oled.init_display()
oled.fill(0x000)

# I2C0 LIGHTMETER SETTING
scl = Pin(1)
sda = Pin(0)
i2c0 = I2C(0, scl=scl, sda=sda, freq=100000)
# LIGHTMETER INIT 
bh1750 = BH1750(0x23, i2c0)


    
# SWITCH MODE SETTING
switch = ToggleSwitch(pin_number=15)

previous_mode = switch.state


ss_enables = [1/16000 ,1/8000, 1/4000, 1/2000, 1/1000, 1/500, 1/250, 1/125, 1/60, 1/30, 1/15, 1/8, 1/4, 1/2, 1, 2, 4, 8, 15, 30, 60]

fstops_enables =  [100, 22, 16, 11, 8.0, 5.6, 4.0, 2.8, 2.0, 1.7, 1.4, 0.0]


iso_enables = [50, 100, 200, 200, 400, 800, 1600]


def save_values_to_file(f_index, ss_index, iso_index, filename="settings.txt"):
    with open(filename, "w") as file:
        file.write(f"{f_index},{ss_index},{iso_index}")  # 값들을 쉼표로 구분하여 저장

def read_values_from_file(filename="settings.txt"):
    try:
        with open(filename, "r") as file:
            data = file.read().strip()  # 파일 내용 읽고 공백 제거
            f, s, iso = map(int, data.split(","))  # 쉼표로 나누어 실수형으로 변환
            return f, s, iso
    except (OSError, ValueError):
        return None, None, None  # 파일이 없거나 잘못된 형식일 경우 None 반환

# 파일에서 값 읽기
f_index, ss_index, iso_index = read_values_from_file()

f = fstops_enables[f_index]
ss = ss_enables[ss_index]
iso = iso_enables[iso_index]

if f_index is not None and ss_index is not None and iso_index is not None:
    print(f"저장된 인덱: F={f_index}, S={ss_index}, ISO={iso_index}")
    print(f"저장된 값: F={f}, S={ss}, ISO={iso}")
else:
    print("저장된 설정이 없습니다.")



# 버튼으로 f,ss, iso 제
btn_iso_up = Pin(16, Pin.IN, Pin.PULL_UP)  # 스위치 핀 설정
btn_iso_down = Pin(17, Pin.IN, Pin.PULL_UP)  # 스위치 핀 설정
btn_f_ss_down = Pin(18, Pin.IN, Pin.PULL_UP)  # 스위치 핀 설정
btn_f_ss_up = Pin(19, Pin.IN, Pin.PULL_UP)  # 스위치 핀 설정

# 디바운스 시간 (밀리초 단위)
DEBOUNCE_TIME = 200
last_iso_up_time = 0
last_iso_down_time = 0
last_f_ss_down_time = 0
last_f_ss_up_time = 0

def iso_button_up_callback(pin):
    global iso_index, iso, last_iso_up_time
    current_time = ticks_ms()
    if ticks_diff(current_time, last_iso_up_time) > DEBOUNCE_TIME:
        iso_index += 1
        if iso_index >= len(iso_enables):
            iso_index = 0
        iso = iso_enables[iso_index]
        print("ISO 증가: iso_index:", iso_index)
        print("ISO 값:", iso)
        save_values_to_file(f_index, ss_index, iso_index)
        last_iso_up_time = current_time

def iso_button_down_callback(pin):
    global iso_index, iso, last_iso_down_time
    current_time = ticks_ms()
    if ticks_diff(current_time, last_iso_down_time) > DEBOUNCE_TIME:
        iso_index -= 1
        if iso_index < 0:
            iso_index = len(iso_enables) - 1
        iso = iso_enables[iso_index]
        print("ISO 감소: iso_index:", iso_index)
        print("ISO 값:", iso)
        save_values_to_file(f_index, ss_index, iso_index)
        last_iso_down_time = current_time

def f_ss_button_down_callback(pin):
    global f, f_index, ss, ss_index, last_f_ss_down_time
    current_time = ticks_ms()
    if ticks_diff(current_time, last_f_ss_down_time) > DEBOUNCE_TIME:
        if current_mode:
            ss_index += 1
            if ss_index >= len(ss_enables) - 1:
                ss_index = 1
            ss = ss_enables[ss_index]
        else:
            f_index += 1
            if f_index >= len(fstops_enables) - 1:
                f_index = 1
            f = fstops_enables[f_index]
        save_values_to_file(f_index, ss_index, iso_index)
        last_f_ss_down_time = current_time

def f_ss_button_up_callback(pin):
    global f, f_index, ss, ss_index, last_f_ss_up_time
    current_time = ticks_ms()
    if ticks_diff(current_time, last_f_ss_up_time) > DEBOUNCE_TIME:
        if current_mode:
            ss_index -= 1
            if ss_index < 1:
                ss_index = len(ss_enables) - 2
            ss = ss_enables[ss_index]
        else:
            f_index -= 1
            if f_index < 1:
                f_index = len(fstops_enables) - 2
            f = fstops_enables[f_index]
        save_values_to_file(f_index, ss_index, iso_index)
        last_f_ss_up_time = current_time
        
# 버튼이 눌릴 때 호출되는 인터럽트 설정
btn_iso_up.irq(trigger=Pin.IRQ_FALLING, handler=iso_button_up_callback)
btn_iso_down.irq(trigger=Pin.IRQ_FALLING, handler=iso_button_down_callback)
btn_f_ss_down.irq(trigger=Pin.IRQ_FALLING, handler=f_ss_button_down_callback)
btn_f_ss_up.irq(trigger=Pin.IRQ_FALLING, handler=f_ss_button_up_callback)


while 1:
    lux = bh1750.measurement
    if lux > 0:
        str_lux = str(round(lux))
    else:
        str_lux = 0


    oled.fill(0)

    calculator = ExposureCalculator(lux)
    # 버튼이 눌릴 때 호출되는 인터럽트 설정

    # 스위치 상태 업데이트
    current_mode = switch.update()
    print(current_mode)
    
    # font_display_roboto_black_12(oled, 0, 0, "START LINE", 0xffffff)
    # font_display_roboto_black_12(oled, 0, 83, "______________", 0xffffff)
    
    decimal_aperture = calculator.calculate_aperture(ss, iso)
    aperture = Fraction.float_to_aperture(decimal_aperture, fstops_enables, current_mode)
    str_aperture = str(aperture)
    
    decimal_shutter_speed = calculator.calculate_shutter_speed(f, iso)
    shutter_speed = Fraction.float_to_shutter_speed(decimal_shutter_speed, ss_enables, current_mode)
    str_shutter_speed = str(shutter_speed)
    
    oled.draw_rect(15, 50, 50, 40, None, 0xffffff, radius=0, border_thickness=1)
    oled.draw_rect(64, 50, 51, 40, None ,0xffffff, radius=0, border_thickness=1)
    
    if current_mode:
#        font_display_roboto_black_12(oled, 28, 115, "APERTURE", 0xe55242)
#        font_display_roboto_black_12(oled, 21, 101, "APERTURE", 0x00FFFF)
        font_display_roboto_black_12(oled, 20, 100, "APERTURE", PURPLE)

#        font_display_roboto_black_50(oled, 35, -5, f"{str_aperture[0]}{str_aperture[1:3]}", 0x00ffd5)
        if aperture == 100:
            font_display_roboto_black_40(oled, 21, 2, f"BULB", 0x0000FF)
            font_display_roboto_black_40(oled, 19, 0, f"BULB", 0x00FF00)
        elif aperture == 0.0:
            font_display_roboto_black_40(oled, 17, 2, f"DARK", 0x00FFFF)
            font_display_roboto_black_40(oled, 15, 0, f"DARK", 0xFF0000)            
        else:
            font_display_roboto_black_12(oled, 20, 20, "F / ", 0xffffff)
            font_display_roboto_black_40(oled, 40, 0, f"{str_aperture[0]}{str_aperture[1:3]}", WHITE)
        # Present S/S
        length_ss = len(str(Fraction.float_to_shutter_speed(ss, ss_enables, current_mode)))
        font_display_roboto_black_12(oled, 30, 55, "SS", YELLOW)
        if length_ss == 6:
            font_display_roboto_normal_10(oled, 25, 73, f"{Fraction.float_to_shutter_speed(ss, ss_enables, current_mode)}", 0xffffff)
        elif length_ss == 5:
            font_display_roboto_black_12(oled, 23, 70, f"{Fraction.float_to_shutter_speed(ss, ss_enables, current_mode)}", 0xffffff)            
        elif length_ss == 3:
            font_display_roboto_black_12(oled, 30, 70, f"{Fraction.float_to_shutter_speed(ss, ss_enables, current_mode)}", 0xffffff)
        elif length_ss == 2:
            font_display_roboto_black_12(oled, 32, 70, f"{Fraction.float_to_shutter_speed(ss, ss_enables, current_mode)}", 0xffffff)
        elif length_ss == 1:
            font_display_roboto_black_12(oled, 35, 70, f"{Fraction.float_to_shutter_speed(ss, ss_enables, current_mode)}", 0xffffff)
        else:
            font_display_roboto_black_12(oled, 25, 70, f"{Fraction.float_to_shutter_speed(ss, ss_enables, current_mode)}", 0xffffff)
        
        # Present ISO
        font_display_roboto_black_12(oled, 80, 55, "ISO", YELLOW)
        if len(str(iso)) == 2:
            font_display_roboto_black_12(oled, 85, 70, f"{iso}", 0xffffff)
        elif len(str(iso)) == 3:
            font_display_roboto_black_12(oled, 80, 70, f"{iso}", 0xffffff)
        else:
            font_display_roboto_black_12(oled, 75, 70, f"{iso}", 0xffffff)

    else: 
        font_display_roboto_black_12(oled, 20, 100, "ST. SPEED", PURPLE)
        length_ss = len(str_shutter_speed)
        print(str_shutter_speed)
        
        if str_shutter_speed == "1/16000":
            font_display_roboto_black_40(oled, 21, 2, f"BULB", 0x0000FF)
            font_display_roboto_black_40(oled, 19, 0, f"BULB", 0x00FF00)
        elif  str_shutter_speed == "60":
            font_display_roboto_black_40(oled, 17, 2, f"DARK", 0x00FFFF)
            font_display_roboto_black_40(oled, 15, 0, f"DARK", 0xFF0000)            
        else:
            if length_ss == 1:
                font_display_roboto_black_40(oled, 50, 5, f"{str_shutter_speed}", WHITE)
            elif length_ss == 2:
                font_display_roboto_black_40(oled, 40, 5, f"{str_shutter_speed}", WHITE)            
            elif length_ss == 3:
                font_display_roboto_black_12(oled, 30, 20, f"{str_shutter_speed[0]} / ", WHITE)
                font_display_roboto_black_40(oled, 50, 0, f"{str_shutter_speed[2:]}", WHITE)   
            elif len(str_shutter_speed) == 4:
                font_display_roboto_black_12(oled, 20, 20, f"{str_shutter_speed[0]} / ", WHITE)
                font_display_roboto_black_40(oled, 40, 0, f"{str_shutter_speed[2:]}", WHITE)        
            elif len(str_shutter_speed) == 5:
                font_display_roboto_black_12(oled, 20, 20, f"{str_shutter_speed[0]} / ", WHITE)
                font_display_roboto_black_40(oled, 40, 0, f"{str_shutter_speed[2:]}", WHITE)
            else:
                font_display_roboto_black_12(oled, 20, 20, f"{str_shutter_speed[0]} / ", WHITE)
                font_display_roboto_black_30(oled, 40, 8, f"{str_shutter_speed[2:]}", WHITE)                
   
         # Present S/S
        font_display_roboto_black_12(oled, 35, 55, "F", YELLOW)
        font_display_roboto_black_12(oled, 30, 70, f"{Fraction.float_to_aperture(f, fstops_enables, current_mode)}", WHITE)
        
        # Present ISO
        font_display_roboto_black_12(oled, 80, 55, "ISO", YELLOW)
        if len(str(iso)) == 2:
            font_display_roboto_black_12(oled, 85, 70, f"{iso}", 0xffffff)
        elif len(str(iso)) == 3:
            font_display_roboto_black_12(oled, 80, 70, f"{iso}", 0xffffff)
        else:
            font_display_roboto_black_12(oled, 75, 70, f"{iso}", 0xffffff)



    

    
    #oled.draw_rect(0, 0, 10, 10, 0xFF0000, 0x000, radius=0, border_thickness=1)
    #oled.draw_rect(10, 0, 10, 10, 0x00FF00 ,0x000, radius=0, border_thickness=1)
    #oled.draw_rect(20, 0, 10, 10, 0x0000FF ,0x000, radius=0, border_thickness=1)

    oled.show()
    sleep(0.5)
