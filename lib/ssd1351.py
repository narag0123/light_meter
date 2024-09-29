from micropython import const
from machine import Pin, SPI
import framebuf
import time

# def rgb_to_565(color):
#     """RGB 값을 16비트 RGB565 형식으로 변환합니다."""
#     g = (color >> 16) & 0xFF  # R 추출
#     b = (color >> 8) & 0xFF   # G 추출
#     r = (color >> 0) & 0xFF   # B 추출
#     
#     new_r = (r & 0xF8) << 8
#     new_g = (g & 0xFC) << 3
#     new_b = b >> 3
# 
#     return  new_r | new_g | new_b

# def rgb_to_565(color):
#     r = (color >> 16) & 0xFF
#     g = (color >> 8) & 0xFF
#     b = color & 0xFF
#     """RGB 값을 16비트 RGB565 형식으로 변환합니다."""
#     return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def rgb_to_565(color):
    """RGB888 hex 코드를 16비트 RGB565 형식으로 변환합니다."""
    r = (color >> 16) & 0xFF  # 상위 8비트에서 Red 추출
    g = (color >> 8) & 0xFF   # 중간 8비트에서 Green 추출
    b = color & 0xFF          # 하위 8비트에서 Blue 추출

    new_r = (r & 0xF8) << 8       # Red 상위 5비트 변환
    new_g = (g & 0xFC) << 3       # Green 상위 6비트 변환
    new_b = b >> 3                # Blue 상위 5비트 변환

    return new_r | new_g | new_b   # RGB565 형식으로 합산



# OLED 명령어
SSD1351_CMD_SETCOLUMN = const(0x15)
SSD1351_CMD_SETROW = const(0x75)
SSD1351_CMD_WRITERAM = const(0x5C)
SSD1351_CMD_DISPLAYOFF = const(0xAE)
SSD1351_CMD_DISPLAYON = const(0xAF)
SSD1351_CMD_SETREMAP = const(0xA0)

class SSD1351(framebuf.FrameBuffer):
    def __init__(self, width, height, spi, cs, dc, rst):
        self.width = width
        self.height = height
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.buffer = bytearray(self.width * self.height * 2)  # 16-bit 컬러 사용

        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        
        # 핀 설정
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=1)

        
        # 초기화
        self.reset()
        self.init_display()

    def reset(self):
        self.rst(1)
        time.sleep(0.1)
        self.rst(0)
        time.sleep(0.1)
        self.rst(1)
        time.sleep(0.1)

    def write_cmd(self, cmd):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, data):
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([data]))
        self.cs(1)

    def init_display(self):
        self.write_cmd(SSD1351_CMD_DISPLAYOFF)  # 디스플레이 끄기
        self.write_cmd(SSD1351_CMD_SETREMAP)  # 메모리 매핑 설정
        self.write_data(0x74)
        self.write_cmd(SSD1351_CMD_DISPLAYON)  # 디스플레이 켜기
        

    def draw_char(self, x, y, glyph, width, height, color):
        # 글자 렌더링
        for i in range(height):
            for j in range(width):
                byte_idx = i * ((width + 7) // 8) + (j // 8)
                bit_idx = 7 - (j % 8)
                if glyph[byte_idx] & (1 << bit_idx):
   
                    rgb565_color = rgb_to_565(color)  # RGB -> RGB565 변환
                    self.pixel(x + j, y + i, rgb565_color)
                    
    def draw_rect(self, x, y, width, height, fill_color, color, radius=0, border_thickness=1):

        if fill_color is not None:
            # 24비트 RGB 색상을 16비트 RGB565로 변환]
            fill_color = rgb_to_565(fill_color)

            # 사각형을 그리기
            for i in range(height):
                for j in range(width):
                    self.pixel(x + j, y + i, fill_color)
                    

        # 24비트 RGB 색상을 16비트 RGB565로 변환
        color = rgb_to_565(color)

        # 사각형 외곽선을 그리기 (radius 적용)
        for i in range(height):
            for j in range(width):
                # 둥근 모서리를 고려하여 외곽선을 그릴지 말지 결정
                if radius > 0:
                    # 좌상단 모서리: 180도 회전
                    if (i < radius and j < radius) and (((radius - i) ** 2 + (radius - j) ** 2) > radius ** 2):
                        continue
                    # 좌하단 모서리: 270도 회전
                    if (i >= height - radius and j < radius) and ((i - (height - radius)) ** 2 + (radius - j) ** 2 > radius ** 2):
                        continue
                    # 우상단 모서리: 90도 회전
                    if (i < radius and j >= width - radius) and ((j - (width - radius)) ** 2 + (radius - i) ** 2 > radius ** 2):
                        continue
                    # 우하단 모서리: 변경 없음
                    if (i >= height - radius and j >= width - radius) and ((i - (height - radius)) ** 2 + (j - (width - radius)) ** 2 > radius ** 2):
                        continue
                
                # 외곽선을 그리기 (상, 하, 좌, 우 테두리만)
                if (
                    i < border_thickness or i >= height - border_thickness or  # 상단/하단 외곽선
                    j < border_thickness or j >= width - border_thickness      # 좌측/우측 외곽선
                ):
                    self.pixel(x + j, y + i, color)




    def fill(self, color):
        super().fill(color)

    def show(self):
        # 화면에 표시
        self.write_cmd(SSD1351_CMD_SETCOLUMN)
        self.write_data(0x00)
        self.write_data(self.width - 1)
        self.write_cmd(SSD1351_CMD_SETROW)
        self.write_data(0x00)
        self.write_data(self.height - 1)
        self.write_cmd(SSD1351_CMD_WRITERAM)
        
        self.cs(0)
        self.dc(1)
        self.spi.write(self.buffer)
        self.cs(1)