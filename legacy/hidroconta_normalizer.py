"""
Hidroconta Data Normalizer for Teatinos Site
Handles Italian CSV format with semicolon delimiters and comma decimal separators
"""

import pandas as pd
from datetime import datetime
import os
import glob
import json
import hashlib


class HidrocontaNormalizer:
    """Normalizer for Hidroconta sensor data from Teatinos site"""

    def __init__(self):
        self.data_types = {
            "analog": "Analog sensor readings (pressure, etc.)",
            "consumption": "Daily consumption measurements",
            "consumption-flow": "Flow rate measurements",
            "consumption-hours": "Hourly consumption data",
            "solar": "Solar panel voltage readings",
        }

        self.units_mapping = {
            "Bar": "pressure_bar",
            "m3/h": "flow_rate_m3h",
            "m3": "volume_m3",
            "V": "voltage_v",
            "L/min": "flow_rate_lmin",
        }

    def identify_data_type(self, filename):
        """Identify the type of data based on filename"""
        filename_lower = filename.lower()

        if "analog" in filename_lower:
            return "analog"
        elif "consumption-flow" in filename_lower:
            return "consumption-flow"
        elif "consumption-hours" in filename_lower:
            return "consumption-hours"
        elif "consumption" in filename_lower:
            return "consumption"
        elif "solar" in filename_lower:
            return "solar"
        else:
            return "unknown"

    def extract_metadata_from_filename(self, filename):
        """Extract metadata from Hidroconta filename format"""
        # Example: 20230611000000-20250618180312-analog-Teatinos-PCR-4-AI00 Entrada.csv
        basename = os.path.basename(filename)
        parts = basename.replace(".csv", "").split("-")

        metadata = {
            "filename": basename,
            "site": "Teatinos",
            "system": "Hidroconta",
            "data_type": self.identify_data_type(basename),
        }

        # Extract date range
        if len(parts) >= 2:
            try:
                start_date = datetime.strptime(parts[0], "%Y%m%d%H%M%S")
                end_date = datetime.strptime(parts[1], "%Y%m%d%H%M%S")
                metadata["date_range_start"] = start_date.isoformat()
                metadata["date_range_end"] = end_date.isoformat()
            except:
                pass

        # Extract PCR unit
        for part in parts:
            if "PCR" in part:
                metadata["pcr_unit"] = part
                break

        # Extract sensor info
        if "AI00" in basename:
            metadata["sensor_type"] = "AI00"
            if "Entrada" in basename:
                metadata["sensor_location"] = "Entrada"
            elif "Salida" in basename:
                metadata["sensor_location"] = "Salida"
        elif "AI01" in basename:
            metadata["sensor_type"] = "AI01"
            if "Entrada" in basename:
                metadata["sensor_location"] = "Entrada"
            elif "Salida" in basename:
                metadata["sensor_location"] = "Salida"
        elif "C00" in basename:
            metadata["sensor_type"] = "C00"

        return metadata

    def read_hidroconta_csv(self, file_path):
        """Read Hidroconta CSV with Italian format"""
        try:
            # Read first few lines to understand structure
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [f.readline().strip() for _ in range(5)]

            # Extract header description (first line)
            description = lines[0].strip('"')

            # Find data start line (usually line 3, but let's be safe)
            data_start_line = 2
            for i, line in enumerate(lines[2:], start=2):
                if "Data/Ora" not in line and line.count(";") >= 1:
                    data_start_line = i
                    break

            # Read the actual data
            df = pd.read_csv(
                file_path,
                delimiter=";",
                decimal=",",  # Italian decimal separator
                skiprows=data_start_line,
                encoding="utf-8",
                parse_dates=[0],
                date_parser=lambda x: pd.to_datetime(
                    x, format="%Y/%m/%d %H:%M:%S", errors="coerce"
                ),
            )

            # Clean column names
            df.columns = df.columns.str.strip().str.replace('"', "")

            # Rename columns to standard format
            if len(df.columns) >= 2:
                df = df.rename(
                    columns={df.columns[0]: "datetime", df.columns[1]: "value"}
                )

                # Add unit column if it exists
                if len(df.columns) >= 3:
                    df = df.rename(columns={df.columns[2]: "unit"})

            # Remove empty rows
            df = df.dropna(subset=["datetime", "value"])

            # Add metadata columns
            metadata = self.extract_metadata_from_filename(file_path)
            df["_source_file"] = metadata["filename"]
            df["_data_type"] = metadata["data_type"]
            df["_pcr_unit"] = metadata.get("pcr_unit", "Unknown")
            df["_sensor_type"] = metadata.get("sensor_type", "Unknown")
            df["_sensor_location"] = metadata.get("sensor_location", "Unknown")
            df["_description"] = description

            return df, metadata, description

        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
            return pd.DataFrame(), {}, ""

    def normalize_teatinos_data(self, data_folder):
        """Normalize all Hidroconta data from Teatinos site"""

        csv_files = glob.glob(os.path.join(data_folder, "*.csv"))

        if not csv_files:
            raise ValueError(f"No CSV files found in {data_folder}")

        print(f"Found {len(csv_files)} Hidroconta files to process")

        all_data = []
        metadata_summary = {
            "files_processed": 0,
            "total_records": 0,
            "data_types": {},
            "pcr_units": set(),
            "date_range": {},
            "processing_errors": [],
        }

        for file_path in csv_files:
            print(f"Processing: {os.path.basename(file_path)}")

            try:
                df, file_metadata, description = self.read_hidroconta_csv(file_path)

                if df.empty:
                    metadata_summary["processing_errors"].append(
                        f"Empty data: {file_path}"
                    )
                    continue

                # Add processing metadata
                df["_ingestion_timestamp"] = pd.Timestamp.now()
                df["_row_id"] = range(len(df))

                # Create unique row hash
                df["_row_hash"] = df.apply(
                    lambda row: hashlib.md5(
                        f"{row['datetime']}{row['value']}{row['_source_file']}{row['_row_id']}".encode()
                    ).hexdigest(),
                    axis=1,
                )

                all_data.append(df)

                # Update metadata
                metadata_summary["files_processed"] += 1
                metadata_summary["total_records"] += len(df)

                data_type = file_metadata.get("data_type", "unknown")
                if data_type not in metadata_summary["data_types"]:
                    metadata_summary["data_types"][data_type] = []
                metadata_summary["data_types"][data_type].append(
                    file_metadata["filename"]
                )

                pcr_unit = file_metadata.get("pcr_unit", "Unknown")
                metadata_summary["pcr_units"].add(pcr_unit)

                # Track date range
                if not df.empty:
                    file_min_date = df["datetime"].min()
                    file_max_date = df["datetime"].max()

                    if "min_date" not in metadata_summary["date_range"]:
                        metadata_summary["date_range"]["min_date"] = file_min_date
                        metadata_summary["date_range"]["max_date"] = file_max_date
                    else:
                        if file_min_date < metadata_summary["date_range"]["min_date"]:
                            metadata_summary["date_range"]["min_date"] = file_min_date
                        if file_max_date > metadata_summary["date_range"]["max_date"]:
                            metadata_summary["date_range"]["max_date"] = file_max_date

            except Exception as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                print(error_msg)
                metadata_summary["processing_errors"].append(error_msg)

        if not all_data:
            raise ValueError("No valid data found in any files")

        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)

        # Convert metadata summary for JSON serialization
        metadata_summary["pcr_units"] = list(metadata_summary["pcr_units"])
        if "min_date" in metadata_summary["date_range"]:
            metadata_summary["date_range"]["min_date"] = metadata_summary["date_range"][
                "min_date"
            ].isoformat()
            metadata_summary["date_range"]["max_date"] = metadata_summary["date_range"][
                "max_date"
            ].isoformat()

        # Add overall statistics
        metadata_summary["data_quality"] = {
            "total_records": len(combined_df),
            "missing_values": combined_df["value"].isna().sum(),
            "duplicate_hashes": combined_df["_row_hash"].duplicated().sum(),
            "date_coverage_days": (
                (
                    pd.to_datetime(metadata_summary["date_range"]["max_date"])
                    - pd.to_datetime(metadata_summary["date_range"]["min_date"])
                ).days
                if metadata_summary["date_range"]
                else 0
            ),
        }

        print("\n✅ Processing complete:")
        print(f"   📁 Files processed: {metadata_summary['files_processed']}")
        print(f"   📊 Total records: {metadata_summary['total_records']}")
        print(f"   🔧 PCR units: {', '.join(metadata_summary['pcr_units'])}")
        print(
            f"   📅 Date range: {metadata_summary['date_range'].get('min_date', 'N/A')} to {metadata_summary['date_range'].get('max_date', 'N/A')}"
        )

        return combined_df, metadata_summary

    def create_bigquery_schema(self, df, metadata):
        """Create BigQuery schema for Hidroconta data"""

        schema = [
            {
                "name": "datetime",
                "type": "TIMESTAMP",
                "mode": "REQUIRED",
                "description": "Date and time of measurement",
            },
            {
                "name": "value",
                "type": "FLOAT64",
                "mode": "NULLABLE",
                "description": "Measured value",
            },
            {
                "name": "unit",
                "type": "STRING",
                "mode": "NULLABLE",
                "description": "Unit of measurement (Bar, m3/h, m3, V, etc.)",
            },
            {
                "name": "_source_file",
                "type": "STRING",
                "mode": "REQUIRED",
                "description": "Source CSV filename",
            },
            {
                "name": "_data_type",
                "type": "STRING",
                "mode": "REQUIRED",
                "description": "Type of measurement (analog, consumption, solar, etc.)",
            },
            {
                "name": "_pcr_unit",
                "type": "STRING",
                "mode": "REQUIRED",
                "description": "PCR unit identifier (PCR-4, PCR-5)",
            },
            {
                "name": "_sensor_type",
                "type": "STRING",
                "mode": "NULLABLE",
                "description": "Sensor type (AI00, AI01, C00)",
            },
            {
                "name": "_sensor_location",
                "type": "STRING",
                "mode": "NULLABLE",
                "description": "Sensor location (Entrada, Salida)",
            },
            {
                "name": "_description",
                "type": "STRING",
                "mode": "NULLABLE",
                "description": "Original data description in Italian",
            },
            {
                "name": "_ingestion_timestamp",
                "type": "TIMESTAMP",
                "mode": "REQUIRED",
                "description": "When the data was processed and ingested",
            },
            {
                "name": "_row_id",
                "type": "INT64",
                "mode": "REQUIRED",
                "description": "Row identifier within source file",
            },
            {
                "name": "_row_hash",
                "type": "STRING",
                "mode": "REQUIRED",
                "description": "Hash for deduplication",
            },
        ]

        return schema


def main():
    """Main function to process Hidroconta data"""

    data_folder = "RAWDATA/Studio Dati (Hidroconta)"

    if not os.path.exists(data_folder):
        print(f"❌ Data folder not found: {data_folder}")
        return

    # Initialize normalizer
    normalizer = HidrocontaNormalizer()

    try:
        # Process all data
        print("🚀 Processing Hidroconta data from Teatinos site...")
        df, metadata = normalizer.normalize_teatinos_data(data_folder)

        # Save normalized data
        output_file = "teatinos_hidroconta_normalized.csv"
        df.to_csv(output_file, index=False)
        print(f"💾 Normalized data saved to: {output_file}")

        # Save metadata
        metadata_file = "teatinos_hidroconta_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2, default=str)
        print(f"📋 Metadata saved to: {metadata_file}")

        # Create BigQuery schema
        schema = normalizer.create_bigquery_schema(df, metadata)
        schema_file = "teatinos_hidroconta_schema.json"
        with open(schema_file, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"🗄️ BigQuery schema saved to: {schema_file}")

        # Display summary
        print("\n📊 Data Summary:")
        print("   🏢 Site: Teatinos (Hidroconta)")
        print(f"   📁 Files: {metadata['files_processed']}")
        print(f"   📊 Records: {metadata['total_records']:,}")
        print(f"   🔧 PCR Units: {', '.join(metadata['pcr_units'])}")
        print(f"   📈 Data Types: {', '.join(metadata['data_types'].keys())}")

        if metadata["processing_errors"]:
            print(f"   ⚠️ Errors: {len(metadata['processing_errors'])}")
            for error in metadata["processing_errors"]:
                print(f"      • {error}")

        print("\n✅ Ready for BigQuery import!")
        print("   Dataset: teatinos_infrastructure")
        print("   Table: sensor_data")
        print(f"   Schema: {schema_file}")
        print(f"   Data: {output_file}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
