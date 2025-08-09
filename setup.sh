#!/bin/bash


### Setup python virtual environment ###

VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "Virtual environment not found. Creating one in '$VENV_DIR'..."
  # Execute the command to create the venv
  python3 -m venv "$VENV_DIR"
else
  echo "Virtual environment '$VENV_DIR' already exists."
fi

source ./.venv/bin/activate
pip install -r ./requirements.txt


### Setup webserver to start on bootup ###

SERVICE_NAME="led-webserver.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"
SCRIPT_NAME="simple_raspi_led_web_server.py"

# Check for root privileges
if [[ $EUID -ne 0 ]]; then
   echo "Error: This script must be run with sudo to enable the web-server on raspi boot."
   exit 1
fi

# Determine the user who ran sudo
if [ -z "$SUDO_USER" ]; then
    echo "Error: Cannot determine the user who ran sudo."
    exit 1
fi
RUN_USER="$SUDO_USER"

# Define paths based on the current working directory
WORKING_DIR=$(pwd)
SCRIPT_PATH="$WORKING_DIR/$SCRIPT_NAME"
VENV_PYTHON="$WORKING_DIR/.venv/bin/python"

# Validate that the Python script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: '$SCRIPT_NAME' not found in the current directory."
    echo "Please run this script from the directory containing '$SCRIPT_NAME'."
    exit 1
fi

# Validate that the venv Python executable exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: venv Python interpreter not found at '$VENV_PYTHON'."
    echo "Please ensure a '.venv' directory exists here."
    exit 1
fi

# Create the systemd service file
echo "Creating service file using Python from the virtual environment..."
cat > $SERVICE_FILE <<EOF
[Unit]
Description=Python LED Web Server (venv)
After=network.target

[Service]
# This is the crucial change:
ExecStart=$VENV_PYTHON $SCRIPT_PATH
WorkingDirectory=$WORKING_DIR
Restart=always
User=$RUN_USER

[Install]
WantedBy=multi-user.target
EOF

# Add the user to the 'gpio' group
echo "Adding user '$RUN_USER' to the 'gpio' group..."
usermod -a -G gpio $RUN_USER

# Reload systemd and start the service
echo "Reloading systemd and starting the service..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

echo ""
echo "Setup complete."
echo "To check status, run: sudo systemctl status $SERVICE_NAME"
echo "To view logs, run: sudo journalctl -fu $SERVICE_NAME"