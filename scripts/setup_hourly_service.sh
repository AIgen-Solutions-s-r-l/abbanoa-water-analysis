#!/bin/bash
# Setup script for hourly data generation service

set -e

echo "Setting up hourly data generation service..."

# Create systemd service file
sudo tee /etc/systemd/system/abbanoa-hourly-data.service > /dev/null << EOF
[Unit]
Description=Abbanoa Hourly Synthetic Data Generator
After=network.target postgresql.service

[Service]
Type=oneshot
User=$USER
WorkingDirectory=/home/alessio/Customers/Abbanoa
ExecStart=/usr/bin/python3 /home/alessio/Customers/Abbanoa/scripts/hourly_data_generator.py
StandardOutput=journal
StandardError=journal

# Restart on failure
Restart=on-failure
RestartSec=60
EOF

# Create systemd timer
sudo tee /etc/systemd/system/abbanoa-hourly-data.timer > /dev/null << EOF
[Unit]
Description=Run Abbanoa Hourly Data Generator every hour
Requires=abbanoa-hourly-data.service

[Timer]
# Run every hour at :15 (to avoid conflicts with other hourly jobs)
OnCalendar=*-*-* *:15:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Create logs directory
mkdir -p /home/alessio/Customers/Abbanoa/logs

# Make the Python script executable
chmod +x /home/alessio/Customers/Abbanoa/scripts/hourly_data_generator.py

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the timer
sudo systemctl enable abbanoa-hourly-data.timer
sudo systemctl start abbanoa-hourly-data.timer

echo "✅ Hourly data generation service installed successfully!"
echo ""
echo "Useful commands:"
echo "  - Check timer status: sudo systemctl status abbanoa-hourly-data.timer"
echo "  - Check service status: sudo systemctl status abbanoa-hourly-data.service"
echo "  - View logs: sudo journalctl -u abbanoa-hourly-data.service -f"
echo "  - Run manually: sudo systemctl start abbanoa-hourly-data.service"
echo "  - Stop timer: sudo systemctl stop abbanoa-hourly-data.timer"
echo "  - Disable timer: sudo systemctl disable abbanoa-hourly-data.timer"
echo ""
echo "The service will run every hour at :15 minutes past the hour."
