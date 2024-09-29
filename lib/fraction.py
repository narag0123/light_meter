class Fraction:
    def __init__(self, numerator=1, denominator=1):
        self.numerator = numerator
        self.denominator = denominator

    def __str__(self):
        if self.denominator == 1:
            return f"{self.numerator}"
        return f"{self.numerator}/{self.denominator}"
    
    def to_float(self):
        return self.numerator / self.denominator

    @staticmethod
    def float_to_shutter_speed(x, enables_val, tolerance=1e-6):
        
        # 가장 가까운 셔터 스피드 찾기
        closest_speed = min(enables_val, key=lambda f: abs(f - x))
        
        if closest_speed == int(closest_speed):
            return Fraction(int(closest_speed), 1)
        else:
            denominator = round(1 / closest_speed)
            numerator = round(denominator * closest_speed)
            return Fraction(numerator, denominator)

    @staticmethod
    def float_to_aperture(x, enables_val, tolerance=1e-6):
        
        # 가장 가까운 셔터 스피드 찾기
        closest_speed = min(enables_val, key=lambda f: abs(f - x))
        
        return closest_speed

# 예시 사용
# decimal_number1 = 210.2
# shutter_speed_fraction1 = Fraction.float_to_shutter_speed(decimal_number1)
# print(f"{decimal_number1}는 {shutter_speed_fraction1}로 나타낼 수 있습니다.")

