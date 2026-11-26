"""Input validation helpers.

Each function keeps asking (while loop) until the user enters a valid
value, so the rest of the program never receives bad data.
"""

import math


def get_text(prompt, max_length=40):
    """Ask for non-empty text up to max_length characters."""
    while True:
        value = input(prompt).strip()
        if not value:
            print("  [!] This field cannot be empty. Please try again.")
        elif len(value) > max_length:
            print(f"  [!] Please keep it under {max_length} characters.")
        else:
            return value


def get_float(prompt, minimum=0.0, maximum=None):
    """Ask for a decimal number within [minimum, maximum]."""
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
        except ValueError:
            print("  [!] Please enter a number (e.g. 1500 or 2.5).")
            continue
        if not math.isfinite(value):  # reject "nan" and "inf"
            print("  [!] Please enter a real number.")
        elif value < minimum:
            print(f"  [!] Value must be at least {minimum:g}.")
        elif maximum is not None and value > maximum:
            print(f"  [!] Value must not exceed {maximum:g}.")
        else:
            return value


def get_int(prompt, minimum=0, maximum=None):
    """Ask for a whole number within [minimum, maximum]."""
    while True:
        raw = input(prompt).strip()
        if not raw.lstrip("-").isdigit():
            print("  [!] Please enter a whole number.")
            continue
        value = int(raw)
        if value < minimum or (maximum is not None and value > maximum):
            upper = maximum if maximum is not None else "any"
            print(f"  [!] Please enter a number from {minimum} to {upper}.")
        else:
            return value


def get_yes_no(prompt):
    """Ask a yes/no question and return True for yes, False for no."""
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("y", "yes"):
            return True
        elif answer in ("n", "no"):
            return False
        else:
            print("  [!] Please answer 'y' or 'n'.")
