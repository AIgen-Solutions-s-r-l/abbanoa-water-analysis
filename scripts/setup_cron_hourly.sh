#!/bin/bash
# Alternative: Setup hourly data generation using cron

set -e

echo "Setting up hourly data generation with cron..."

# Create logs directory
mkdir -p /home/alessio/Customers/Abbanoa/logs

# Make the Python script executable
chmod +x /home/alessio/Customers/Abbanoa/scripts/hourly_data_generator.py

# Add to crontab (runs at :15 every hour)
CRON_CMD="/usr/bin/python3 /home/alessio/Customers/Abbanoa/scripts/hourly_data_generator.py >> /home/alessio/Customers/Abbanoa/logs/hourly_cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "hourly_data_generator.py"; then
    echo "⚠️  Cron job already exists. Removing old entry..."
    crontab -l | grep -v "hourly_data_generator.py" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "15 * * * * $CRON_CMD") | crontab -

echo "✅ Cron job installed successfully!"
echo ""
echo "The script will run every hour at :15 minutes past the hour."
echo ""
echo "Useful commands:"
echo "  - View crontab: crontab -l"
echo "  - Edit crontab: crontab -e"
echo "  - View logs: tail -f /home/alessio/Customers/Abbanoa/logs/hourly_cron.log"
echo "  - Remove cron job: crontab -l | grep -v 'hourly_data_generator.py' | crontab -"
