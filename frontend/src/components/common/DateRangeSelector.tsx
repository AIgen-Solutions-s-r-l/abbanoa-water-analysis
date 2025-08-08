import React, { useState, useEffect } from 'react';

interface DateRangeSelectorProps {
  onDateRangeChange: (startDate: Date, endDate: Date, label: string) => void;
  selectedValue?: string;
  className?: string;
}

// Icon components
const CalendarIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
  </svg>
);

const ClockIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const TrendingIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
      d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
  </svg>
);

const DateRangeSelector: React.FC<DateRangeSelectorProps> = ({
  onDateRangeChange,
  selectedValue,
  className = ''
}) => {
  const [selectedRange, setSelectedRange] = useState<string>(selectedValue || 'last_7_days');
  const [isCustomRange, setIsCustomRange] = useState(false);
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);

  // Get current date
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);

  // Helper function to subtract days
  const subtractDays = (date: Date, days: number): Date => {
    const result = new Date(date);
    result.setDate(result.getDate() - days);
    result.setHours(0, 0, 0, 0);
    return result;
  };

  // Helper function to subtract months
  const subtractMonths = (date: Date, months: number): Date => {
    const result = new Date(date);
    result.setMonth(result.getMonth() - months);
    result.setHours(0, 0, 0, 0);
    return result;
  };

  // Predefined time ranges with dynamic dates
  const presets = [
    { 
      category: 'Quick Ranges',
      icon: <ClockIcon />,
      options: [
        { 
          label: 'Today', 
          value: 'today',
          startDate: new Date(today.getFullYear(), today.getMonth(), today.getDate(), 0, 0, 0),
          endDate: today
        },
        { 
          label: 'Yesterday', 
          value: 'yesterday',
          startDate: subtractDays(today, 1),
          endDate: subtractDays(today, 1)
        },
        { 
          label: 'Last 7 Days', 
          value: 'last_7_days',
          startDate: subtractDays(today, 6),
          endDate: today
        },
        { 
          label: 'Last 30 Days', 
          value: 'last_30_days',
          startDate: subtractDays(today, 29),
          endDate: today
        },
      ]
    },
    {
      category: 'Monthly Ranges',
      icon: <CalendarIcon />,
      options: [
        { 
          label: 'This Month', 
          value: 'this_month',
          startDate: new Date(today.getFullYear(), today.getMonth(), 1),
          endDate: today
        },
        { 
          label: 'Last Month', 
          value: 'last_month',
          startDate: new Date(today.getFullYear(), today.getMonth() - 1, 1),
          endDate: new Date(today.getFullYear(), today.getMonth(), 0)
        },
        { 
          label: 'Last 3 Months', 
          value: 'last_3_months',
          startDate: subtractMonths(today, 3),
          endDate: today
        },
        { 
          label: 'Last 6 Months', 
          value: 'last_6_months',
          startDate: subtractMonths(today, 6),
          endDate: today
        },
      ]
    },
    {
      category: 'Historical Data',
      icon: <TrendingIcon />,
      options: [
        { 
          label: 'Year to Date', 
          value: 'ytd',
          startDate: new Date(today.getFullYear(), 0, 1),
          endDate: today
        },
        { 
          label: 'All Available Data', 
          value: 'all_data',
          startDate: new Date('2024-11-13T00:00:00Z'),
          endDate: today
        },
      ]
    }
  ];

  // Find the selected preset
  const findPreset = (value: string) => {
    for (const category of presets) {
      const option = category.options.find(opt => opt.value === value);
      if (option) return option;
    }
    return null;
  };

  // Get display label for selected range
  const getDisplayLabel = () => {
    if (isCustomRange) {
      if (customStartDate && customEndDate) {
        const start = new Date(customStartDate).toLocaleDateString();
        const end = new Date(customEndDate).toLocaleDateString();
        return `${start} - ${end}`;
      }
      return 'Select dates...';
    }
    const preset = findPreset(selectedRange);
    return preset ? preset.label : 'Select range...';
  };

  // Sync with parent selectedValue prop
  useEffect(() => {
    if (selectedValue && selectedValue !== selectedRange) {
      setSelectedRange(selectedValue);
    }
  }, [selectedValue, selectedRange]);

  // Handle preset selection
  const handlePresetSelect = (value: string, startDate: Date, endDate: Date, label: string) => {
    setSelectedRange(value);
    setIsCustomRange(false);
    setShowDropdown(false);
    onDateRangeChange(startDate, endDate, label);
  };

  // Handle custom range
  const applyCustomRange = () => {
    if (customStartDate && customEndDate) {
      const start = new Date(customStartDate);
      const end = new Date(customEndDate);
      end.setHours(23, 59, 59, 999);
      const label = `${start.toLocaleDateString()} - ${end.toLocaleDateString()}`;
      setIsCustomRange(true);
      setShowDropdown(false);
      onDateRangeChange(start, end, label);
    }
  };

  // Initialize with default range
  useEffect(() => {
    const defaultPreset = findPreset(selectedRange);
    if (defaultPreset) {
      onDateRangeChange(defaultPreset.startDate, defaultPreset.endDate, defaultPreset.label);
    }
  }, []); // Only run on mount

  return (
    <div className={`relative ${className}`}>
      {/* Time Range Header */}
      <div className="flex items-center gap-2 mb-4">
        <CalendarIcon />
        <h3 className="text-lg font-semibold text-gray-200">Time Range</h3>
      </div>

      {/* Main Selector Button */}
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="w-full px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg border border-gray-600 
                   transition-all duration-200 flex items-center justify-between group"
      >
        <div className="flex items-center gap-3">
          <div className="text-blue-400">
            <CalendarIcon />
          </div>
          <span className="text-gray-200 font-medium">{getDisplayLabel()}</span>
        </div>
        <svg 
          className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${showDropdown ? 'rotate-180' : ''}`} 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {showDropdown && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-gray-800 border border-gray-700 
                        rounded-lg shadow-xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2">
          <div className="max-h-96 overflow-y-auto">
            {/* Preset Options */}
            {presets.map((category, idx) => (
              <div key={idx} className="border-b border-gray-700 last:border-0">
                <div className="px-4 py-2 bg-gray-900/50 flex items-center gap-2">
                  <div className="text-gray-400">{category.icon}</div>
                  <span className="text-sm font-medium text-gray-300">{category.category}</span>
                </div>
                <div className="p-2">
                  {category.options.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => handlePresetSelect(option.value, option.startDate, option.endDate, option.label)}
                      className={`w-full px-4 py-2 text-left rounded-md transition-all duration-150
                                ${selectedRange === option.value && !isCustomRange
                                  ? 'bg-blue-600 text-white' 
                                  : 'hover:bg-gray-700 text-gray-300'}`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>
            ))}

            {/* Custom Range Section */}
            <div className="border-t border-gray-700 p-4 bg-gray-900/30">
              <div className="flex items-center gap-2 mb-3">
                <CalendarIcon />
                <span className="text-sm font-medium text-gray-300">Custom Range</span>
              </div>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-gray-400 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={customStartDate}
                    max={new Date().toISOString().split('T')[0]}
                    onChange={(e) => setCustomStartDate(e.target.value)}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md 
                             text-gray-200 focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-400 mb-1">End Date</label>
                  <input
                    type="date"
                    value={customEndDate}
                    min={customStartDate}
                    max={new Date().toISOString().split('T')[0]}
                    onChange={(e) => setCustomEndDate(e.target.value)}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md 
                             text-gray-200 focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <button
                  onClick={applyCustomRange}
                  disabled={!customStartDate || !customEndDate}
                  className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 
                           disabled:text-gray-500 text-white rounded-md transition-colors duration-200"
                >
                  Apply Custom Range
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Current Selection Info */}
      <div className="mt-3 flex items-center gap-2 text-sm text-gray-400">
        <ClockIcon />
        <span>Selected: {getDisplayLabel()}</span>
      </div>
    </div>
  );
};

export default DateRangeSelector;