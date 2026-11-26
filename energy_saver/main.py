"""Program entry point."""

from energy_saver.app import EnergyApp


def main():
    """Start the application and handle Ctrl+C gracefully."""
    app = EnergyApp()
    try:
        app.run()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram interrupted. Goodbye!")


if __name__ == "__main__":
    main()
