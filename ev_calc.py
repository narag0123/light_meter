from math import log2, sqrt
from lib.fraction import Fraction



class ExposureCalculator:
    def __init__(self, lux, calibration_constant=1):
        self.lux = lux  # 조도 값 (lux)
        self.calibration_constant = calibration_constant  # 노출계 보정 상수 
        print(f'lux: {round(lux)}')
       
    
    def calculate_exposure_value(self):
        # 기본 노출 값 (EV) 계산 (ISO 100 기준)
        if self.lux == 0:
            return 0
        else:
            ev = log2(self.lux / self.calibration_constant) 
#            print(f'ev: {round(ev,1)}')
            return ev

    def calculate_shutter_speed(self, f, iso):
        # 주어진 f-stop과 ISO에서 셔터 속도 계산
        shutter_speed = (100 * f**2) / (2 ** self.calculate_exposure_value() * iso)

#        print(f'ss: {shutter_speed}')
        return shutter_speed

    def calculate_aperture(self, shutter_speed, iso):
        # 주어진 셔터 속도와 ISO에서 조리개 값(F-stop) 계산
#        ev_iso = self.calculate_exposure_value() + log2(iso / 100)
#        aperture = sqrt(shutter_speed * (2 ** ev_iso))  # N = sqrt(t * 2^EV_ISO)
        aperture = sqrt(shutter_speed * (2**self.calculate_exposure_value()) * (iso/100))
#        print(f'aperture: {aperture}')
        return aperture

    def calculate_iso(self, shutter_speed, f):
        # 주어진 셔터 속도와 f-stop에서 ISO 값 계산
        ev = self.calculate_exposure_value()
        ev_iso = log2(f**2 / shutter_speed)  # 2^EV_ISO = N^2 / t
        iso = 100 * (2 ** (ev_iso - ev))  # ISO = 100 * 2^(EV_ISO - EV)
        return iso

# 사용 예시
# lux = 500  # 측정된 lux 값
# calculator = ExposureCalculator(lux)

# f/2.8, ISO 100일 때 적정 셔터 속도 계산
# f = 2.8
# iso = 100
# shutter_speed = calculator.calculate_shutter_speed(f, iso)
# print(f"적정 셔터 속도: 1/{round(1/shutter_speed)}초")

# lux가 250일 때, 셔터 속도 1/125초, ISO 100일 때 적정 조리개 값 계산
# lux = 250
# calculator.lux = lux
# shutter_speed = 1/125
# f_value = calculator.calculate_aperture(shutter_speed, iso)
# print(f"적정 조리개 값: f/{round(f_value, 1)}")

# lux 250, f/4, 셔터 속도 1/60일 때 ISO 값 계산
# shutter_speed = 1/60
# f = 4
# iso_value = calculator.calculate_iso(shutter_speed, f)
# print(f"적정 ISO 값: {round(iso_value)}")
