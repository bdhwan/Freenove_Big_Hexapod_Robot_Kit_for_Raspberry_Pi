import time
from gpiozero import OutputDevice
from gpio_utils import release_gpio_pin

class Buzzer:
    def __init__(self):
        """Initialize the Buzzer class."""
        self.PIN = 17                            # Set the GPIO pin for the buzzer
        # Try to release the pin before initializing to prevent 'GPIO busy' errors
        release_gpio_pin(self.PIN)
        time.sleep(0.1)  # Small delay to ensure pin is released
        self.buzzer_pin = OutputDevice(self.PIN) # Initialize the buzzer pin

    def set_state(self, state: bool) -> None:
        """Set the state of the buzzer."""
        self.buzzer_pin.on() if state else self.buzzer_pin.off() # Turn on or off the buzzer based on the state

    def close(self) -> None:
        """Close the buzzer pin."""
        self.buzzer_pin.close()           # Close the buzzer pin to release the GPIO resource

if __name__ == '__main__':
    try:
        buzzer = Buzzer()                 # Create an instance of the Buzzer class
        buzzer.set_state(True)            # Turn on the buzzer
        time.sleep(3)                     # Wait for 3 second
        buzzer.set_state(False)           # Turn off the buzzer
    finally:
        buzzer.close()                    # Ensure the buzzer pin is closed when the program is interrupted



