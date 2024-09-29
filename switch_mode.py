from machine import Pin
import time
import uos

# False : Aperture Mode / True : Shutter Speed Mode
class ToggleSwitch:
    def __init__(self, pin_number, file_name='switch_state.txt'):
        self.pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)  # 스위치 핀 설정
        self.file_name = file_name
        self.state = self.load_state()  # 초기 상태 로드
        self.last_reading = self.pin.value()  # 초기 스위치 상태
        

    def load_state(self):
        if self.file_exists(self.file_name):
            with open(self.file_name, 'r') as f:
                state = f.read().strip()
                return state == 'True'
        return False  # 기본값은 False

    def file_exists(self, file_name):
        try:
            uos.stat(file_name)  # 파일이 존재하는지 확인
            return True
        except OSError:
            return False

    def save_state(self):
        with open(self.file_name, 'w') as f:
            f.write(str(self.state))

    def update(self):
        current_reading = self.pin.value()  # 현재 스위치 상태 읽기
        if current_reading != self.last_reading:
            if not current_reading:  # 스위치가 눌렸을 때
                time.sleep(0.1)  # 디바운스 처리
                self.state = not self.state  # 상태 반전
                self.save_state()  # 상태 저장
            self.last_reading = current_reading
        return self.state