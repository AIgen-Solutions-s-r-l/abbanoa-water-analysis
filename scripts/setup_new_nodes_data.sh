#!/bin/bash
# Setup script for new sensor nodes data in BigQuery

echo "=== New Nodes Data Setup ==="
echo ""
echo "This script will help you set up the sensor_readings_ml table"
echo "and load the backup sensor data for the 6 new nodes."
echo ""

# Check if running from correct directory
if [ ! -f "scripts/process_backup_data.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   cd /home/alessio/Customers/Abbanoa"
    exit 1
fi

echo "📋 Prerequisites:"
echo "   - Google Cloud SDK installed and authenticated"
echo "   - BigQuery API enabled"
echo "   - Proper permissions for dataset: water_infrastructure"
echo ""

echo "📊 New nodes to be added:"
echo "   - Distribution nodes: 215542, 215600, 273933"
echo "   - Monitoring nodes: 281492, 288399, 288400"
echo ""

echo "🚀 Steps to complete:"
echo ""
echo "1. Set environment variables:"
echo "   export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcloud/application_default_credentials.json"
echo "   export BIGQUERY_PROJECT_ID=abbanoa-464816"
echo "   export BIGQUERY_DATASET_ID=water_infrastructure"
echo ""

echo "2. Run the data processing script:"
echo "   python3 scripts/process_backup_data.py"
echo ""
echo "   This will:"
echo "   - Create the sensor_readings_ml table"
echo "   - Process all CSV files in RAWDATA/NEW_DATA/BACKUP"
echo "   - Load data with quality scores"
echo "   - Create ML-optimized views"
echo ""

echo "3. Validate the integration:"
echo "   python3 scripts/validate_ml_data.py"
echo ""

echo "4. Test in BigQuery console:"
echo "   SELECT COUNT(DISTINCT node_id) as node_count,"
echo "          COUNT(*) as total_readings"
echo "   FROM \`abbanoa-464816.water_infrastructure.sensor_readings_ml\`"
echo "   WHERE DATE(timestamp) >= CURRENT_DATE() - 30"
echo ""

echo "5. Restart the dashboard:"
echo "   streamlit run src/presentation/streamlit/app.py"
echo ""

echo "📝 Note: The dashboard will show all 9 nodes even before"
echo "    running the data processing script, but actual data"
echo "    for the new nodes will only appear after processing."
echo ""

echo "Ready to proceed? Run the commands above in order."