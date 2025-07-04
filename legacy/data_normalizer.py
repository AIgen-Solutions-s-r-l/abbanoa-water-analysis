"""
Data Normalizer for Water Infrastructure Time Series
Prepares CSV data for BigQuery ingestion with proper schema and formatting
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import re
from typing import Dict, List, Tuple, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WaterDataNormalizer:
    """Normalizes water infrastructure CSV data for BigQuery ingestion"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self.get_default_config()
        self.metadata = {}
        self.column_mapping = {}
        
    @staticmethod
    def get_default_config() -> Dict:
        """Default configuration for data normalization"""
        return {
            "timestamp_formats": [
                "%d/%m/%Y %H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%d-%m-%Y %H:%M:%S"
            ],
            "decimal_separator": ",",
            "thousands_separator": ".",
            "encoding": "utf-8",
            "csv_separator": ";",
            "units_row_index": 1,  # Row containing units (0-based)
            "data_types": {
                "temperature": "FLOAT64",
                "flow_rate": "FLOAT64",
                "pressure": "FLOAT64",
                "volume": "FLOAT64",
                "default": "FLOAT64"
            },
            "bigquery_dataset": "water_infrastructure",
            "bigquery_table_prefix": "sensor_data"
        }
    
    def analyze_csv_structure(self, file_path: str) -> Dict:
        """Analyze CSV structure to understand headers and data types"""
        logger.info(f"Analyzing CSV structure: {file_path}")
        
        # Read first few lines to understand structure
        with open(file_path, 'r', encoding=self.config['encoding']) as f:
            lines = [f.readline().strip() for _ in range(5)]
        
        # Parse headers
        headers_line = lines[0].split(self.config['csv_separator'])
        units_line = lines[1].split(self.config['csv_separator']) if len(lines) > 1 else []
        
        structure = {
            "headers": headers_line,
            "units": units_line,
            "n_columns": len(headers_line),
            "has_units_row": bool(units_line),
            "sample_data": lines[2:] if len(lines) > 2 else []
        }
        
        logger.info(f"Found {structure['n_columns']} columns")
        return structure
    
    def create_column_schema(self, headers: List[str], units: List[str]) -> Dict:
        """Create BigQuery-compatible column schema"""
        schema = []
        column_mapping = {}
        
        for idx, (header, unit) in enumerate(zip(headers, units)):
            # Clean header for BigQuery column name
            clean_name = self._clean_column_name(header, idx)
            
            # Determine data type based on header/unit
            data_type = self._infer_data_type(header, unit)
            
            # Create schema entry
            schema_entry = {
                "name": clean_name,
                "type": data_type,
                "mode": "NULLABLE",
                "description": f"{header} ({unit})" if unit else header
            }
            
            schema.append(schema_entry)
            column_mapping[header] = {
                "clean_name": clean_name,
                "original_name": header,
                "unit": unit,
                "data_type": data_type,
                "index": idx
            }
        
        return {
            "schema": schema,
            "column_mapping": column_mapping
        }
    
    def _clean_column_name(self, name: str, idx: int) -> str:
        """Convert column name to BigQuery-compatible format"""
        if not name or name.startswith('Unnamed'):
            # Handle unnamed columns
            if idx == 0:
                return "date"
            elif idx == 1:
                return "time"
            else:
                return f"metric_{idx}"
        
        # Remove special characters and normalize
        clean = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        clean = re.sub(r'_+', '_', clean)
        clean = clean.strip('_').lower()
        
        # Ensure it starts with a letter
        if clean and clean[0].isdigit():
            clean = f"col_{clean}"
        
        # Limit length
        if len(clean) > 128:
            clean = clean[:128]
        
        return clean or f"col_{idx}"
    
    def _infer_data_type(self, header: str, unit: str) -> str:
        """Infer BigQuery data type from header and unit"""
        header_lower = header.lower()
        unit_lower = unit.lower() if unit else ""
        
        # Check for datetime columns
        if any(dt in header_lower for dt in ['data', 'date', 'ora', 'time', 'timestamp']):
            return "STRING"  # Will be converted to TIMESTAMP later
        
        # Check for specific measurement types
        if 'temperatura' in header_lower or 'temperature' in header_lower:
            return self.config['data_types']['temperature']
        elif 'portata' in header_lower or 'flow' in header_lower:
            return self.config['data_types']['flow_rate']
        elif 'pressione' in header_lower or 'pressure' in header_lower or 'bar' in unit_lower:
            return self.config['data_types']['pressure']
        elif 'volume' in header_lower or 'm3' in unit_lower:
            return self.config['data_types']['volume']
        
        return self.config['data_types']['default']
    
    def normalize_data(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """Normalize CSV data for BigQuery ingestion"""
        logger.info(f"Normalizing data from: {file_path}")
        
        # Analyze structure
        structure = self.analyze_csv_structure(file_path)
        
        # Create schema
        schema_info = self.create_column_schema(
            structure['headers'], 
            structure['units'] if structure['has_units_row'] else [''] * len(structure['headers'])
        )
        
        # Read data
        skiprows = 2 if structure['has_units_row'] else 1
        df = pd.read_csv(
            file_path,
            sep=self.config['csv_separator'],
            decimal=self.config['decimal_separator'],
            thousands=self.config['thousands_separator'],
            encoding=self.config['encoding'],
            skiprows=skiprows,
            header=None,
            names=[col['name'] for col in schema_info['schema']]
        )
        
        logger.info(f"Loaded {len(df)} rows")
        
        # Process datetime columns
        df = self._process_datetime_columns(df, schema_info)
        
        # Convert numeric columns
        df = self._convert_numeric_columns(df, schema_info)
        
        # Add metadata columns
        df = self._add_metadata_columns(df, file_path)
        
        # Validate data
        validation_results = self._validate_data(df)
        
        metadata = {
            "source_file": file_path,
            "processing_timestamp": datetime.now().isoformat(),
            "rows_processed": len(df),
            "schema": schema_info['schema'],
            "column_mapping": schema_info['column_mapping'],
            "validation": validation_results
        }
        
        return df, metadata
    
    def _process_datetime_columns(self, df: pd.DataFrame, schema_info: Dict) -> pd.DataFrame:
        """Process and combine date/time columns into timestamp"""
        
        # Look for date and time columns
        date_col = None
        time_col = None
        
        for col in df.columns:
            if 'date' in col.lower() or col == 'date':
                date_col = col
            elif 'time' in col.lower() or col == 'time':
                time_col = col
        
        if date_col and time_col:
            # Combine date and time
            df['timestamp'] = pd.to_datetime(
                df[date_col].astype(str) + ' ' + df[time_col].astype(str),
                format=self.config['timestamp_formats'][0],
                errors='coerce'
            )
            
            # Drop original columns
            df = df.drop([date_col, time_col], axis=1)
            
            # Move timestamp to first column
            cols = ['timestamp'] + [col for col in df.columns if col != 'timestamp']
            df = df[cols]
            
            logger.info(f"Created timestamp column from {date_col} and {time_col}")
        
        return df
    
    def _convert_numeric_columns(self, df: pd.DataFrame, schema_info: Dict) -> pd.DataFrame:
        """Convert numeric columns to proper data types"""
        
        for col in df.columns:
            if col == 'timestamp':
                continue
                
            # Find column info
            col_info = None
            for mapping in schema_info['column_mapping'].values():
                if mapping['clean_name'] == col:
                    col_info = mapping
                    break
            
            if col_info and 'FLOAT' in col_info['data_type']:
                # Convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')
                logger.debug(f"Converted {col} to numeric")
        
        return df
    
    def _add_metadata_columns(self, df: pd.DataFrame, file_path: str) -> pd.DataFrame:
        """Add metadata columns for tracking"""
        
        df['_ingestion_timestamp'] = datetime.now()
        df['_source_file'] = file_path.split('/')[-1]
        df['_row_hash'] = pd.util.hash_pandas_object(df, index=False)
        
        return df
    
    def _validate_data(self, df: pd.DataFrame) -> Dict:
        """Validate data quality"""
        
        validation = {
            "total_rows": len(df),
            "columns": len(df.columns),
            "missing_values": {},
            "data_types": {},
            "timestamp_range": None,
            "quality_score": 100.0
        }
        
        # Check missing values
        for col in df.columns:
            if col.startswith('_'):
                continue
            missing = df[col].isna().sum()
            if missing > 0:
                validation['missing_values'][col] = {
                    "count": int(missing),
                    "percentage": float(missing / len(df) * 100)
                }
        
        # Check data types
        validation['data_types'] = {col: str(df[col].dtype) for col in df.columns}
        
        # Check timestamp range
        if 'timestamp' in df.columns:
            validation['timestamp_range'] = {
                "min": str(df['timestamp'].min()),
                "max": str(df['timestamp'].max()),
                "gaps": self._detect_time_gaps(df['timestamp'])
            }
        
        # Calculate quality score
        missing_penalty = sum(v['percentage'] for v in validation['missing_values'].values())
        validation['quality_score'] = max(0, 100 - missing_penalty)
        
        return validation
    
    def _detect_time_gaps(self, timestamps: pd.Series) -> List[Dict]:
        """Detect gaps in time series"""
        
        if len(timestamps) < 2:
            return []
        
        # Sort timestamps
        sorted_ts = timestamps.sort_values()
        
        # Calculate differences
        diffs = sorted_ts.diff()
        
        # Find mode (most common interval)
        mode_interval = diffs.mode()[0] if len(diffs.mode()) > 0 else pd.Timedelta(minutes=30)
        
        # Find gaps (more than 2x the mode interval)
        gaps = []
        for i, diff in enumerate(diffs):
            if pd.notna(diff) and diff > 2 * mode_interval:
                gaps.append({
                    "start": str(sorted_ts.iloc[i-1]),
                    "end": str(sorted_ts.iloc[i]),
                    "duration": str(diff)
                })
        
        return gaps[:10]  # Return max 10 gaps
    
    def generate_bigquery_schema(self, df: pd.DataFrame, metadata: Dict) -> List[Dict]:
        """Generate BigQuery schema from normalized dataframe"""
        
        schema = []
        
        # Add timestamp field
        if 'timestamp' in df.columns:
            schema.append({
                "name": "timestamp",
                "type": "TIMESTAMP",
                "mode": "REQUIRED",
                "description": "Measurement timestamp"
            })
        
        # Add measurement fields
        for col in df.columns:
            if col == 'timestamp' or col.startswith('_'):
                continue
                
            # Find original description
            description = col
            for mapping in metadata['column_mapping'].values():
                if mapping['clean_name'] == col:
                    description = mapping.get('description', f"{mapping['original_name']} ({mapping['unit']})")
                    break
            
            schema.append({
                "name": col,
                "type": "FLOAT64",
                "mode": "NULLABLE",
                "description": description
            })
        
        # Add metadata fields
        schema.extend([
            {
                "name": "_ingestion_timestamp",
                "type": "TIMESTAMP",
                "mode": "REQUIRED",
                "description": "When the data was ingested"
            },
            {
                "name": "_source_file",
                "type": "STRING",
                "mode": "REQUIRED",
                "description": "Source CSV filename"
            },
            {
                "name": "_row_hash",
                "type": "INT64",
                "mode": "REQUIRED",
                "description": "Hash for deduplication"
            }
        ])
        
        return schema


def create_bigquery_table_config(schema: List[Dict], metadata: Dict) -> Dict:
    """Create BigQuery table configuration"""
    
    config = {
        "dataset_id": "water_infrastructure",
        "table_id": f"sensor_data_{datetime.now().strftime('%Y%m')}",
        "schema": schema,
        "time_partitioning": {
            "type": "DAY",
            "field": "timestamp"
        },
        "clustering_fields": ["_source_file", "timestamp"],
        "description": f"Water sensor data ingested from {metadata['source_file']}",
        "labels": {
            "environment": "production",
            "data_type": "time_series",
            "source": "csv_import"
        }
    }
    
    return config


# Example usage
if __name__ == "__main__":
    # Initialize normalizer
    normalizer = WaterDataNormalizer()
    
    # Normalize data
    file_path = "RAWDATA/REPORT_NODI_SELARGIUS_AGGREGATI_30_MIN_20241113060000_20250331060000.csv"
    normalized_df, metadata = normalizer.normalize_data(file_path)
    
    # Generate BigQuery schema
    bq_schema = normalizer.generate_bigquery_schema(normalized_df, metadata)
    
    # Create table configuration
    table_config = create_bigquery_table_config(bq_schema, metadata)
    
    # Save outputs
    normalized_df.to_csv('normalized_data.csv', index=False)
    
    with open('bigquery_schema.json', 'w') as f:
        json.dump(bq_schema, f, indent=2)
    
    with open('bigquery_table_config.json', 'w') as f:
        json.dump(table_config, f, indent=2)
    
    with open('normalization_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    print(f"✓ Data normalized: {len(normalized_df)} rows")
    print(f"✓ BigQuery schema saved: {len(bq_schema)} fields")
    print(f"✓ Quality score: {metadata['validation']['quality_score']:.1f}%")
    print(f"\nNext step: Upload to BigQuery using 'bq load' or Python client")