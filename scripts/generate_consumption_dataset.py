#!/usr/bin/env python3
"""
Synthetic Water Consumption Dataset Generator

This script generates realistic synthetic water consumption data for 50,000 users
from August 1, 2023 to June 30, 2025, incorporating seasonal trends, weather patterns,
user behavior, holidays, and geographic variations.

Author: AI Water Management System
Date: 2025-01-28
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta, date
from typing import List, Dict, Tuple, Generator
import os
import math
from tqdm import tqdm
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

class WaterConsumptionGenerator:
    """
    Generates synthetic water consumption data with realistic patterns.
    """
    
    def __init__(self, start_date: str = '2023-08-01', end_date: str = '2025-06-30', num_users: int = 50000):
        """
        Initialize the water consumption generator.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            num_users: Number of users to generate
        """
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        self.num_users = num_users
        self.dates = self._generate_date_range()
        self.num_days = len(self.dates)
        
        # Districts with different characteristics
        self.districts = {
            'Cagliari_Centro': {'coastal': True, 'tourism_factor': 1.4, 'base_temp_offset': 2.0},
            'Quartu_SantElena': {'coastal': True, 'tourism_factor': 1.2, 'base_temp_offset': 1.5},
            'Assemini_Industrial': {'coastal': False, 'tourism_factor': 0.8, 'base_temp_offset': 0.5},
            'Monserrato_Residential': {'coastal': False, 'tourism_factor': 0.9, 'base_temp_offset': 0.0},
            'Selargius_Distribution': {'coastal': False, 'tourism_factor': 1.0, 'base_temp_offset': -0.5}
        }
        
        # User type distributions and characteristics
        self.user_types = {
            'residential': {
                'probability': 0.75,
                'base_consumption': 250,  # liters per day
                'weekend_factor': 1.15,
                'holiday_factor': 1.1,
                'temp_sensitivity': 8.0,  # additional liters per degree above 25°C
                'variability': 0.25
            },
            'commercial': {
                'probability': 0.20,
                'base_consumption': 800,
                'weekend_factor': 0.7,
                'holiday_factor': 0.4,
                'temp_sensitivity': 15.0,
                'variability': 0.35
            },
            'industrial': {
                'probability': 0.05,
                'base_consumption': 5000,
                'weekend_factor': 0.8,
                'holiday_factor': 0.3,
                'temp_sensitivity': 20.0,
                'variability': 0.15
            }
        }
        
        logger.info(f"Initialized generator: {self.num_users} users, {self.num_days} days ({start_date} to {end_date})")
    
    def _generate_date_range(self) -> List[date]:
        """Generate list of dates from start to end date."""
        dates = []
        current_date = self.start_date
        while current_date <= self.end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
        return dates
    
    def _generate_holidays(self) -> List[date]:
        """
        Generate list of holidays and special dates.
        Includes Italian holidays and summer peak periods.
        """
        holidays = []
        
        # Fixed holidays for each year
        years = list(range(self.start_date.year, self.end_date.year + 1))
        
        for year in years:
            # New Year's Day
            holidays.append(date(year, 1, 1))
            # Epiphany
            holidays.append(date(year, 1, 6))
            # Liberation Day
            holidays.append(date(year, 4, 25))
            # Labour Day
            holidays.append(date(year, 5, 1))
            # Republic Day
            holidays.append(date(year, 6, 2))
            # Assumption of Mary
            holidays.append(date(year, 8, 15))
            # All Saints' Day
            holidays.append(date(year, 11, 1))
            # Immaculate Conception
            holidays.append(date(year, 12, 8))
            # Christmas Day
            holidays.append(date(year, 12, 25))
            # St. Stephen's Day
            holidays.append(date(year, 12, 26))
            
            # Summer vacation period (peak tourism)
            for day in range(15, 32):  # July 15-31
                if day <= 31:
                    holidays.append(date(year, 7, day))
            for day in range(1, 16):  # August 1-15
                holidays.append(date(year, 8, day))
        
        # Filter holidays within our date range
        holidays = [h for h in holidays if self.start_date <= h <= self.end_date]
        return holidays
    
    def _generate_users(self) -> pd.DataFrame:
        """
        Generate user metadata including user_id, user_type, and district.
        """
        logger.info("Generating user metadata...")
        
        users = []
        district_names = list(self.districts.keys())
        
        for i in range(self.num_users):
            user_id = f"USER_{i+1:06d}"
            
            # Assign user type based on probabilities
            rand = random.random()
            if rand < self.user_types['residential']['probability']:
                user_type = 'residential'
            elif rand < self.user_types['residential']['probability'] + self.user_types['commercial']['probability']:
                user_type = 'commercial'
            else:
                user_type = 'industrial'
            
            # Assign district (roughly equal distribution with some variation)
            district = random.choice(district_names)
            
            users.append({
                'user_id': user_id,
                'user_type': user_type,
                'district': district
            })
        
        users_df = pd.DataFrame(users)
        logger.info(f"Generated {len(users_df)} users")
        logger.info(f"User type distribution:\n{users_df['user_type'].value_counts()}")
        logger.info(f"District distribution:\n{users_df['district'].value_counts()}")
        
        return users_df
    
    def _calculate_temperature(self, date_obj: date, district: str) -> float:
        """
        Calculate realistic temperature for a given date and district.
        Uses sinusoidal model with noise and district-specific offsets.
        """
        # Day of year (0-365)
        day_of_year = date_obj.timetuple().tm_yday
        
        # Base temperature using sinusoidal model (Sardinia climate)
        # Peak summer ~35°C, winter ~15°C, mean ~25°C
        base_temp = 25 + 10 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
        
        # Add district-specific offset
        district_offset = self.districts[district]['base_temp_offset']
        base_temp += district_offset
        
        # Add random daily variation
        daily_variation = np.random.normal(0, 3)  # ±3°C standard deviation
        
        temperature = base_temp + daily_variation
        
        # Ensure realistic bounds
        temperature = max(5, min(45, temperature))
        
        return round(temperature, 1)
    
    def _calculate_consumption(self, user_type: str, district: str, date_obj: date, 
                              temperature: float, is_holiday: bool, is_weekend: bool) -> float:
        """
        Calculate daily water consumption for a user based on multiple factors.
        """
        user_config = self.user_types[user_type]
        district_config = self.districts[district]
        
        # Base consumption
        base_consumption = user_config['base_consumption']
        
        # Apply weekend factor
        if is_weekend:
            base_consumption *= user_config['weekend_factor']
        
        # Apply holiday factor
        if is_holiday:
            base_consumption *= user_config['holiday_factor']
        
        # Temperature effect (irrigation, cooling, etc.)
        if temperature > 25:
            temp_increase = (temperature - 25) * user_config['temp_sensitivity']
            base_consumption += temp_increase
        
        # Seasonal irrigation effect (residential users, summer months)
        if user_type == 'residential':
            month = date_obj.month
            if month in [6, 7, 8, 9]:  # Summer irrigation season
                irrigation_factor = 1.2 + 0.1 * math.sin(2 * math.pi * (month - 6) / 4)
                base_consumption *= irrigation_factor
        
        # Tourism effect (coastal districts in summer)
        if district_config['coastal'] and date_obj.month in [6, 7, 8]:
            tourism_boost = district_config['tourism_factor']
            if user_type in ['commercial', 'residential']:
                base_consumption *= tourism_boost
        
        # Add user-specific variability
        variability = user_config['variability']
        variation_factor = np.random.normal(1.0, variability)
        variation_factor = max(0.3, min(2.0, variation_factor))  # Bound the variation
        
        final_consumption = base_consumption * variation_factor
        
        # Apply small random losses (leaks, measurement errors)
        loss_factor = 1 + np.random.uniform(0.005, 0.02)  # 0.5-2% losses
        final_consumption *= loss_factor
        
        # Ensure non-negative and reasonable bounds
        final_consumption = max(10, final_consumption)  # Minimum 10 liters per day
        
        return round(final_consumption, 2)
    
    def _generate_consumption_batch(self, users_batch: pd.DataFrame, output_dir: str) -> None:
        """
        Generate consumption data for a batch of users and save to CSV.
        Memory-efficient batch processing.
        """
        logger.info(f"Processing batch of {len(users_batch)} users...")
        
        holidays = set(self._generate_holidays())
        
        # Process each district separately for memory efficiency
        for district in users_batch['district'].unique():
            district_users = users_batch[users_batch['district'] == district]
            
            consumption_data = []
            
            for _, user in tqdm(district_users.iterrows(), 
                              desc=f"Processing {district}", 
                              total=len(district_users)):
                
                for date_obj in self.dates:
                    # Calculate date-specific factors
                    temperature = self._calculate_temperature(date_obj, district)
                    is_holiday = date_obj in holidays
                    is_weekend = date_obj.weekday() >= 5  # Saturday=5, Sunday=6
                    
                    # Calculate consumption
                    consumption = self._calculate_consumption(
                        user['user_type'], 
                        district, 
                        date_obj, 
                        temperature, 
                        is_holiday, 
                        is_weekend
                    )
                    
                    consumption_data.append({
                        'user_id': user['user_id'],
                        'date': date_obj.strftime('%Y-%m-%d'),
                        'user_type': user['user_type'],
                        'district': district,
                        'temperature_c': temperature,
                        'is_holiday': is_holiday,
                        'consumption_liters': consumption
                    })
            
            # Save district data to CSV
            district_df = pd.DataFrame(consumption_data)
            output_file = os.path.join(output_dir, f'water_consumption_{district}.csv')
            district_df.to_csv(output_file, index=False)
            
            logger.info(f"Saved {len(district_df)} records to {output_file}")
            
            # Clear memory
            del consumption_data, district_df
    
    def generate_dataset(self, output_dir: str = 'consumption_data', batch_size: int = 10000) -> None:
        """
        Generate the complete synthetic water consumption dataset.
        
        Args:
            output_dir: Directory to save CSV files
            batch_size: Number of users to process in each batch
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Starting dataset generation...")
        logger.info(f"Total records to generate: {self.num_users * self.num_days:,}")
        
        # Generate users
        users_df = self._generate_users()
        
        # Process users in batches to manage memory
        for i in range(0, len(users_df), batch_size):
            batch_users = users_df.iloc[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{math.ceil(len(users_df)/batch_size)}")
            
            self._generate_consumption_batch(batch_users, output_dir)
        
        # Generate summary statistics
        self._generate_summary_report(output_dir)
        
        logger.info(f"Dataset generation completed! Files saved in '{output_dir}'")
    
    def _generate_summary_report(self, output_dir: str) -> None:
        """
        Generate a summary report of the dataset.
        """
        logger.info("Generating summary report...")
        
        summary = {
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'date_range': f"{self.start_date} to {self.end_date}",
            'num_users': self.num_users,
            'num_days': self.num_days,
            'total_records': self.num_users * self.num_days,
            'districts': list(self.districts.keys()),
            'user_types': list(self.user_types.keys()),
            'random_seed': RANDOM_SEED
        }
        
        # Save summary as JSON
        import json
        summary_file = os.path.join(output_dir, 'dataset_summary.json')
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Summary report saved to {summary_file}")


def main():
    """
    Main function to run the water consumption dataset generator.
    """
    print("🚰 Synthetic Water Consumption Dataset Generator")
    print("=" * 60)
    
    # Configuration
    START_DATE = '2023-08-01'
    END_DATE = '2025-06-30'
    NUM_USERS = 50000
    OUTPUT_DIR = 'consumption_data'
    BATCH_SIZE = 10000
    
    # Initialize generator
    generator = WaterConsumptionGenerator(
        start_date=START_DATE,
        end_date=END_DATE,
        num_users=NUM_USERS
    )
    
    # Generate dataset
    try:
        generator.generate_dataset(output_dir=OUTPUT_DIR, batch_size=BATCH_SIZE)
        
        print("\n✅ Dataset generation completed successfully!")
        print(f"📁 Output directory: {OUTPUT_DIR}")
        print(f"📊 Total users: {NUM_USERS:,}")
        print(f"📅 Date range: {START_DATE} to {END_DATE}")
        print(f"💾 Expected total records: {NUM_USERS * len(generator.dates):,}")
        
    except Exception as e:
        logger.error(f"Error during dataset generation: {e}")
        raise


if __name__ == "__main__":
    main() 