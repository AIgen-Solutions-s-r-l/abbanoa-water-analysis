'use client';

import React, { useState, useEffect } from 'react';

interface DateRange {
  startDate: Date;
  endDate: Date;
  label: string;
}

interface DateRangeSelectorProps {
  onDateRangeChange: (dateRange: DateRange & { selectedValue?: string }) => void;
  selectedValue?: string;
  className?: string;
}

// Simple SVG icons
const CalendarIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
  </svg>
);

const ClockIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const DateRangeSelector: React.FC<DateRangeSelectorProps> = ({
  onDateRangeChange,
  selectedValue,
  className = ''
}) => {
  const [selectedRange, setSelectedRange] = useState<string>(selectedValue || 'march_2025');  // Initialize with March 2025 (most recent data)
  const [isCustomRange, setIsCustomRange] = useState(false);
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');

  // Sync with parent selectedValue prop
  useEffect(() => {
    if (selectedValue && selectedValue !== selectedRange) {
      setSelectedRange(selectedValue);
    }
  }, [selectedValue, selectedRange]);

  // Predefined time ranges
  const presets = [
    { 
      label: 'Last Week (March 2025)', 
      value: 'last_week_march',
      startDate: new Date('2025-03-25T00:00:00Z'),
      endDate: new Date('2025-04-01T23:59:59Z')
    },
    { 
      label: 'Last Month (March 2025)', 
      value: 'march_2025',
      startDate: new Date('2025-03-01T00:00:00Z'),
      endDate: new Date('2025-03-31T23:59:59Z')
    },
    { 
      label: 'February 2025', 
      value: 'feb_2025',
      startDate: new Date('2025-02-01T00:00:00Z'),
      endDate: new Date('2025-02-28T23:59:59Z')
    },
    { 
      label: 'January 2025', 
      value: 'jan_2025',
      startDate: new Date('2025-01-01T00:00:00Z'),
      endDate: new Date('2025-01-31T23:59:59Z')
    },
    { 
      label: 'December 2024', 
      value: 'dec_2024',
      startDate: new Date('2024-12-01T00:00:00Z'),
      endDate: new Date('2024-12-31T23:59:59Z')
    },
    { 
      label: 'November 2024', 
      value: 'nov_2024',
      startDate: new Date('2024-11-01T00:00:00Z'),
      endDate: new Date('2024-11-30T23:59:59Z')
    },
    { 
      label: 'All Data (Nov 2024 - Mar 2025)', 
      value: 'all_data',
      startDate: new Date('2024-11-01T00:00:00Z'),
      endDate: new Date('2025-04-01T23:59:59Z')
    },
    { 
      label: 'Custom Range', 
      value: 'custom',
      startDate: new Date(),
      endDate: new Date()
    }
  ];

  const handlePresetChange = (rangeKey: string) => {
    setSelectedRange(rangeKey);
    setIsCustomRange(rangeKey === 'custom');
    
    const range = presets.find(r => r.value === rangeKey);
    if (range && rangeKey !== 'custom') {
      onDateRangeChange({
        startDate: range.startDate,
        endDate: range.endDate,
        label: range.label,
        selectedValue: rangeKey
      });
    }
  };

  const handleCustomDateChange = () => {
    if (customStartDate && customEndDate) {
      const startDate = new Date(customStartDate);
      const endDate = new Date(customEndDate);
      
      if (startDate <= endDate) {
        onDateRangeChange({
          startDate,
          endDate,
          label: `${startDate.toLocaleDateString()} - ${endDate.toLocaleDateString()}`
        });
      }
    }
  };

  // Initialize with default range (24h) - removed automatic initialization
  // Parent component will handle initial setup to avoid duplicate loads

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 ${className}`}>
      <div className="flex items-center gap-2 mb-3">
        <CalendarIcon />
        <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">Time Range</h3>
      </div>
      
      {/* Preset Range Buttons */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 mb-4">
        {presets.map((range) => (
          <button
            key={range.value}
            onClick={() => handlePresetChange(range.value)}
            className={`
              px-3 py-2 text-xs font-medium rounded-md transition-colors
              ${selectedRange === range.value
                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800'
                : 'bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600'
              }
            `}
          >
            {range.label}
          </button>
        ))}
      </div>

      {/* Custom Date Range Inputs */}
      {isCustomRange && (
        <div className="border-t border-gray-200 dark:border-gray-600 pt-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Start Date
              </label>
              <input
                type="datetime-local"
                value={customStartDate}
                onChange={(e) => setCustomStartDate(e.target.value)}
                onBlur={handleCustomDateChange}
                className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                End Date
              </label>
              <input
                type="datetime-local"
                value={customEndDate}
                onChange={(e) => setCustomEndDate(e.target.value)}
                onBlur={handleCustomDateChange}
                className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          
          {customStartDate && customEndDate && (
            <button
              onClick={handleCustomDateChange}
              className="mt-3 w-full px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
            >
              Apply Custom Range
            </button>
          )}
        </div>
      )}
      
      {/* Current Selection Display */}
      <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-600">
        <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
          <ClockIcon />
          <span>
            Selected: {presets.find(r => r.value === selectedRange)?.label || 'Custom Range'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default DateRangeSelector; 