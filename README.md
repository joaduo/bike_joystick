# bike_joystick
Use a standing bike as a joystick controller (arduino + python)


## Installation

Works on linux (need to port to windows, but not yet)

1. Get the repo
2. Flash arduino_bike_pulse.ino.c into a arduino
3. Make the circuit
    * connect power to bike sensor (outgoing energy)
    * connect incoming energy (pulse) from bike sensor to
       * input pin 2
       * a resistence and then to ground of arduino
4. Connect arduino to USB
5. Fix device name in rpm_listener.py (i need to add command parameter)
    `def get_bike_calculated(timeout=0.5, max_guess=3, arduino_dev='/dev/ttyACM0'):`
6. Run the joystick (probably you need to run as root, or give permissions to the serial device)
    `python bike_gamepad/bike_joystick.py --rpm-button 250 --wheel-button 160`

