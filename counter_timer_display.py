import tkinter as tk
from tkinter import ttk
import RPi.GPIO as GPIO
import time
import threading
import requests
from datetime import datetime
import math  # Import the math module for rounding

#Lucy

class SwitchStatusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Switch Status")
        self.root.configure(bg='black')  # Set the background color to black

        self.switch_pin = 37
        self.switch_closed_time = None
        self.is_counting = False

        # Set up GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Create a style for the labels
        style = ttk.Style()
        style.configure("TLabel", font=('Helvetica', 40), foreground='white')  # Set text color to white

        # Create a label to display the elapsed time
        self.time_label = ttk.Label(root, text="Break Length: 0:00", style="TLabel", background='black')
        self.time_label.pack(pady=20, anchor=tk.CENTER)

        # Create a label to display the switch status
        self.status_label = ttk.Label(root, text="Mic #1: OFF", style="TLabel", background='black')
        self.status_label.pack(pady=10, anchor=tk.CENTER)

        # Create a label to display the current time
        self.time_now_label = ttk.Label(root, text="", style="TLabel", background='black')
        self.time_now_label.pack(side=tk.LEFT, anchor=tk.SW, padx=2, pady=10)

        # Create a button to close the application (labeled 'x')
        self.quit_button = ttk.Button(root, text="", command=self.quit_app, style="TButton")
        self.quit_button.pack(side=tk.TOP, anchor=tk.NE, padx=10, pady=10)

        # Create a label to display the temperature
        self.temperature_label = ttk.Label(root, text="", style="TLabel", background='black')
        self.temperature_label.pack(side=tk.RIGHT, anchor=tk.SE, padx=10, pady=10)

        # Start updating elapsed time continuously
        self.update_switch_status_thread = threading.Thread(target=self.update_switch_status, daemon=True)
        self.update_elapsed_time_thread = threading.Thread(target=self.update_elapsed_time, daemon=True)
        self.update_temperature_thread = threading.Thread(target=self.update_temperature, daemon=True)
        self.update_current_time_thread = threading.Thread(target=self.update_current_time, daemon=True)

        self.update_switch_status_thread.start()
        self.update_elapsed_time_thread.start()
        self.update_temperature_thread.start()
        self.update_current_time_thread.start()

        # Full screen
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', self.exit_full_screen)

        # Style for the Quit button
        style.configure("TButton", font=('Helvetica', 10), background='black', foreground='white')

    def update_switch_status(self):
        while True:
            switch_status = not GPIO.input(self.switch_pin)

            # Update the label text based on the logic status
            status_text = "ON" if switch_status else "OFF"
            self.status_label.config(text=f"Mic #1: {status_text}")

            if switch_status:
                # Start the timer when the logic status is ON
                if not self.is_counting:
                    self.switch_closed_time = time.time()
                    self.is_counting = True
            elif self.is_counting:
                # Pause or reset the timer when the logic status is OFF
                elapsed_time = int(time.time() - self.switch_closed_time)
                minutes, seconds = divmod(elapsed_time, 60)
                self.time_label.config(text=f"Break Length:{minutes}:{seconds:02d}")
                self.is_counting = False

            time.sleep(0.1)  # Adjust sleep time based on your needs

    def update_elapsed_time(self):
        # Update the elapsed time label continuously
        while True:
            if self.is_counting:
                elapsed_time = int(time.time() - self.switch_closed_time)
                minutes, seconds = divmod(elapsed_time, 60)
                self.time_label.config(text=f"Break Length:  {minutes}:{seconds:02d}")

            time.sleep(0.1)  # Adjust sleep time based on your needs

    def update_current_time(self):
        # Update the current time label continuously
        while True:
            current_time = datetime.now().strftime("%I:%M:%S %p")
            self.time_now_label.config(text=f" {current_time}")
            time.sleep(1)  # Update every second

    def update_temperature(self):
        while True:
            try:
                # Replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key
                api_key = '258e5efcec0be075592aa50d55cf7426'
                city = 'Findlay'
                country_code = 'US'
                unit = 'imperial'  # You can change to 'metric' for Celsius

                # API endpoint for current weather data
                api_url = f'http://api.openweathermap.org/data/2.5/weather?q={city},{country_code}&appid={api_key}&units={unit}'

                # Requesting weather data
                response = requests.get(api_url)
                response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

                data = response.json()

                # Extracting temperature information and rounding up
                temperature = data['main']['temp']
                temperature_rounded = math.ceil(temperature)
                self.temperature_label.config(text=f' {temperature_rounded}°F')

            except Exception as e:
                print(f"Error fetching temperature: {e}")
                print("Full API response:", response.text)

            # Update temperature every 30 minutes
            time.sleep(1800)

    def quit_app(self):
        # Clean up GPIO before quitting
        GPIO.cleanup()
        self.root.destroy()

    def exit_full_screen(self, event=None):
        self.root.attributes('-fullscreen', False)

if __name__ == "__main__":
    root = tk.Tk()
    app = SwitchStatusApp(root)

    root.mainloop()
