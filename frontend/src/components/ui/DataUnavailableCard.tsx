import React from 'react';
import { Card } from './Card';
import { Button } from './Button';
import { 
  Database, 
  RefreshCw, 
  AlertCircle, 
  WifiOff,
  ServerOff,
  Clock
} from 'lucide-react';

interface DataUnavailableCardProps {
  title: string;
  message: string;
  onRetry?: () => void;
  icon?: React.ReactNode;
  variant?: 'info' | 'warning' | 'error';
  showAdminContact?: boolean;
}

const iconMap = {
  info: Database,
  warning: AlertCircle,
  error: WifiOff
};

const colorMap = {
  info: {
    bg: 'bg-blue-100 dark:bg-blue-900/20',
    icon: 'text-blue-600 dark:text-blue-400'
  },
  warning: {
    bg: 'bg-amber-100 dark:bg-amber-900/20',
    icon: 'text-amber-600 dark:text-amber-400'
  },
  error: {
    bg: 'bg-red-100 dark:bg-red-900/20',
    icon: 'text-red-600 dark:text-red-400'
  }
};

export const DataUnavailableCard: React.FC<DataUnavailableCardProps> = ({
  title,
  message,
  onRetry,
  icon,
  variant = 'info',
  showAdminContact = true
}) => {
  const IconComponent = iconMap[variant];
  const colors = colorMap[variant];

  return (
    <Card className="p-8">
      <div className="flex flex-col items-center justify-center text-center space-y-4">
        <div className={`rounded-full ${colors.bg} p-6`}>
          {icon || <IconComponent className={`w-12 h-12 ${colors.icon}`} />}
        </div>
        <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
          {title}
        </h2>
        <p className="text-gray-600 dark:text-gray-400 max-w-md">
          {message}
        </p>
        {onRetry && (
          <div className="pt-4">
            <Button 
              variant="primary" 
              onClick={onRetry}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </div>
        )}
        {showAdminContact && (
          <div className="text-sm text-gray-500 dark:text-gray-500 mt-4">
            Please contact your system administrator if this issue persists.
          </div>
        )}
      </div>
    </Card>
  );
};

// Preset configurations for common scenarios
export const EmptyDataCard: React.FC<{ 
  dataType: string;
  onRetry?: () => void;
}> = ({ dataType, onRetry }) => (
  <DataUnavailableCard
    title={`${dataType} Data Not Available`}
    message={`The ${dataType.toLowerCase()} data is currently not available in the database. This could be because the data hasn't been loaded yet or the system is being set up.`}
    onRetry={onRetry}
    variant="info"
  />
);

export const NetworkErrorCard: React.FC<{ 
  onRetry?: () => void;
}> = ({ onRetry }) => (
  <DataUnavailableCard
    title="Network Connection Error"
    message="Unable to connect to the server. Please check your internet connection and try again."
    onRetry={onRetry}
    variant="error"
    icon={<WifiOff className="w-12 h-12 text-red-600 dark:text-red-400" />}
  />
);

export const ServerErrorCard: React.FC<{ 
  errorMessage?: string;
  onRetry?: () => void;
}> = ({ errorMessage, onRetry }) => (
  <DataUnavailableCard
    title="Server Error"
    message={errorMessage || "An unexpected error occurred while fetching data. Please try again later."}
    onRetry={onRetry}
    variant="error"
    icon={<ServerOff className="w-12 h-12 text-red-600 dark:text-red-400" />}
  />
);

export const MaintenanceCard: React.FC<{}> = () => (
  <DataUnavailableCard
    title="System Maintenance"
    message="The system is currently undergoing maintenance. Please check back later."
    variant="warning"
    icon={<Clock className="w-12 h-12 text-amber-600 dark:text-amber-400" />}
    showAdminContact={false}
  />
);



