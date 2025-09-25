#!/bin/bash

# Run initial backup
echo "$(date): Running initial backup..."
python /app/models_backup.py

# Start cron daemon
echo "$(date): Starting cron daemon..."
cron

# Check if cron is running
if pgrep cron > /dev/null; then
    echo "$(date): Cron daemon started successfully"
else
    echo "$(date): ERROR: Cron daemon failed to start"
    exit 1
fi

# Show cron logs in real time
echo "$(date): Monitoring cron logs..."
tail -f /var/log/cron.log