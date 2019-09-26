from outputdevices import display
from outputdevices.guidance import Guidance
from outputdevices.display import Display


class Publisher:

    guidance = Guidance()
    display = Display()

    def general_publish(self):
        display.emotion_factor = 0
        # Publishing values to Bluetooth
