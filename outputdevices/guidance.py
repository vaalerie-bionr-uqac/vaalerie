
import ASUS.GPIO as gpio


class Guidance:

    steering = 0
    speed = 0

    def __init__(self):
        # 26 is IN
        self.rear_light_pin = 11
        self.steering_pin = 13
        self.speed_pin = 15
        self.hz = 250

        self.initialize_gpio()

    def control_steering(self, steering_input):
        # Rotate servo to position required from -12.5 to 12.5 (map 180 = 12.5 & 0 = 2.5)
        self.steering.ChangeDutyCycle(steering_input)

    def control_speed(self, speed_input):
        # Control motor speed from duty cycle (map 2.5 to 12.5)
        self.speed.ChangeDutyCycle(speed_input)

    def brake_is_on(self, state):
        # Open rear lights when brakes are applied
        gpio.output(self.rear_light_pin, int(state))

    def initialize_gpio(self):
        # Setup TINKERBOARD GPIO's
        gpio.setwarnings(False)
        gpio.setmode(gpio.BOARD)

        # Setup GPIO inputs and outputs
        gpio.setup(self.rear_light_pin, gpio.OUT)
        gpio.setup(self.steering_pin, gpio.OUT)
        gpio.setup(self.speed_pin, gpio.OUT)

        # Outputs controls
        self.steering = gpio.PWM(self.steering_pin, self.hz)
        self.steering.start(2.5)  # Start servo at 0 degrees

        self.speed = gpio.PWM(self.speed_pin, self.hz)
        self.speed.start(2.5)  # Initialize with 0 speed
