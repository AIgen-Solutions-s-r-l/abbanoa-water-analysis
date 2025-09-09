'use client';

import React from 'react';

interface DialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
}

interface DialogContentProps {
  className?: string;
  children: React.ReactNode;
}

interface DialogHeaderProps {
  children: React.ReactNode;
}

interface DialogTitleProps {
  className?: string;
  children: React.ReactNode;
}

interface DialogDescriptionProps {
  children: React.ReactNode;
}

export function Dialog({ open, onOpenChange, children }: DialogProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={() => onOpenChange(false)}
      />
      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}

export function DialogContent({ className = '', children }: DialogContentProps) {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto ${className}`}>
      {children}
    </div>
  );
}

export function DialogHeader({ children }: DialogHeaderProps) {
  return (
    <div className="mb-4">
      {children}
    </div>
  );
}

export function DialogTitle({ className = '', children }: DialogTitleProps) {
  return (
    <h2 className={`text-xl font-bold text-gray-900 dark:text-white ${className}`}>
      {children}
    </h2>
  );
}

export function DialogDescription({ children }: DialogDescriptionProps) {
  return (
    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
      {children}
    </p>
  );
}