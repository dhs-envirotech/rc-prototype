import smbus
import time
from hmc5883l import hmc5883l

compass = hmc5883l()

while True:
    print(compass.heading())
    time.sleep(1)
