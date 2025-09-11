import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

interface CardTitleProps {
  children: React.ReactNode;
  className?: string;
}

const Card = ({ children, className = '', padding = 'md' }: CardProps) => {
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm ${paddingClasses[padding]} ${className}`}>
      {children}
    </div>
  );
};

const CardHeader = ({ children, className = '' }: CardHeaderProps) => {
  return (
    <div className={`border-b border-gray-200 dark:border-gray-700 pb-4 mb-4 ${className}`}>
      {children}
    </div>
  );
};

const CardContent = ({ children, className = '' }: CardContentProps) => {
  return (
    <div className={className}>
      {children}
    </div>
  );
};

const CardFooter = ({ children, className = '' }: CardFooterProps) => {
  return (
    <div className={`border-t border-gray-200 dark:border-gray-700 pt-4 mt-4 ${className}`}>
      {children}
    </div>
  );
};

const CardTitle = ({ children, className = '' }: CardTitleProps) => {
  return (
    <h3 className={`text-lg font-semibold text-gray-900 dark:text-gray-100 ${className}`}>
      {children}
    </h3>
  );
};

export { Card, CardHeader, CardContent, CardFooter, CardTitle };
export type { CardProps, CardHeaderProps, CardContentProps, CardFooterProps, CardTitleProps }; 