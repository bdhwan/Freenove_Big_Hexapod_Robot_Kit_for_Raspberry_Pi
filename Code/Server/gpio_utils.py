# -*- coding: utf-8 -*-
"""
GPIO utility functions for pin management
Helps prevent 'GPIO busy' errors when restarting the server
"""
import time


def release_gpio_pin(pin_number: int):
    """
    Release a GPIO pin if it's currently in use.
    This helps prevent 'GPIO busy' errors when restarting the server.
    
    Args:
        pin_number: GPIO pin number to release
    """
    try:
        import lgpio
        # Try to open lgpio handle and release the pin
        handle = lgpio.gpiochip_open(0)
        try:
            # Try to claim the pin as input (which releases it from output)
            lgpio.gpio_claim_input(handle, pin_number, lgpio.SET_PULL_NONE)
            # Then release it
            lgpio.gpio_free(handle, pin_number)
        except Exception:
            # Pin might not be claimed, try to free it anyway
            try:
                lgpio.gpio_free(handle, pin_number)
            except Exception:
                pass
        finally:
            lgpio.gpiochip_close(handle)
    except ImportError:
        # lgpio not available, try alternative method with RPi.GPIO
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.cleanup(pin_number)
        except Exception:
            pass
    except Exception:
        # If all else fails, just continue silently
        pass


def release_gpio_pins(pin_numbers: list):
    """
    Release multiple GPIO pins if they're currently in use.
    
    Args:
        pin_numbers: List of GPIO pin numbers to release
    """
    for pin in pin_numbers:
        release_gpio_pin(pin)
    # Small delay to ensure pins are released
    time.sleep(0.1)

