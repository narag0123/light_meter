from lib.ssd1351 import SSD1351



from font.roboto_black_12 import get_ch as get_roboto_black_12
from font.roboto_black_20 import get_ch as get_roboto_black_20
from font.roboto_black_30 import get_ch as get_roboto_black_30
from font.roboto_black_40 import get_ch as get_roboto_black_40
from font.roboto_black_50 import get_ch as get_roboto_black_50

from font.roboto_normal_10 import get_ch as get_roboto_black_10


def font_display_roboto_black_40(oled, x,y,text,color):
    for ch in text:
        glyph, height, width = get_roboto_black_40(ch)
        oled.draw_char(x,y,glyph, width, height, color)
        x += width
        
def font_display_roboto_black_12(oled, x,y,text,color):
    for ch in text:
        glyph, height, width = get_roboto_black_12(ch)
        oled.draw_char(x,y,glyph, width, height, color)
        x += width
        
def font_display_roboto_black_20(oled, x,y,text,color):
    for ch in text:
        glyph, height, width = get_roboto_black_20(ch)
        oled.draw_char(x,y,glyph, width, height, color)
        x += width
                
def font_display_roboto_black_30(oled, x,y,text,color):
    for ch in text:
        glyph, height, width = get_roboto_black_30(ch)
        oled.draw_char(x,y,glyph, width, height, color)
        x += width
                        
def font_display_roboto_black_50(oled, x,y,text,color):
    for ch in text:
        glyph, height, width = get_roboto_black_50(ch)
        oled.draw_char(x,y,glyph, width, height, color)
        x += width
                                
def font_display_roboto_normal_10(oled, x,y,text,color):
    for ch in text:
        glyph, height, width = get_roboto_black_10(ch)
        oled.draw_char(x,y,glyph, width, height, color)
        x += width