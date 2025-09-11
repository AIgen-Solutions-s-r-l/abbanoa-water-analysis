import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AnomaliesPage from '../page';

// Mock fetch
global.fetch = jest.fn();

describe('AnomaliesPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should fetch anomalies from the last week (168 hours)', async () => {
    // Arrange
    const mockAnomaliesData = [
      {
        id: 1,
        timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        severity: 'medium',
        anomaly_type: 'pressure_anomaly',
        node_name: 'Test Node',
        description: 'Test anomaly',
        confidence: 0.85,
        expected_value: 3.0,
        actual_value: 2.7,
        deviation_percentage: 10,
        node_id: 'NODE_1',
        measurement_type: 'pressure'
      }
    ];

    const mockNodesData = [
      { node_id: 'NODE_1', node_name: 'Test Node' }
    ];

    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        json: async () => mockAnomaliesData,
        ok: true
      })
      .mockResolvedValueOnce({
        json: async () => mockNodesData,
        ok: true
      });

    // Act
    render(<AnomaliesPage />);

    // Assert
    await waitFor(() => {
      // Check that fetch was called with the hours parameter for 1 week (168 hours)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/anomalies?hours=168')
      );
    });

    // Verify the anomaly is displayed
    await waitFor(() => {
      expect(screen.getByText(/Test anomaly/i)).toBeInTheDocument();
    });
  });

  it('should display anomalies from different days within the week', async () => {
    // Arrange
    const now = Date.now();
    const mockAnomaliesData = [
      {
        id: 1,
        timestamp: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
        severity: 'high',
        anomaly_type: 'pressure_anomaly',
        node_name: 'Node Day 1',
        description: 'Anomaly from 1 day ago',
        confidence: 0.9,
        expected_value: 3.0,
        actual_value: 2.5,
        deviation_percentage: 16.7,
        node_id: 'NODE_1',
        measurement_type: 'pressure'
      },
      {
        id: 2,
        timestamp: new Date(now - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
        severity: 'medium',
        anomaly_type: 'flow_anomaly',
        node_name: 'Node Day 3',
        description: 'Anomaly from 3 days ago',
        confidence: 0.85,
        expected_value: 100,
        actual_value: 120,
        deviation_percentage: 20,
        node_id: 'NODE_2',
        measurement_type: 'flow'
      },
      {
        id: 3,
        timestamp: new Date(now - 6 * 24 * 60 * 60 * 1000).toISOString(), // 6 days ago
        severity: 'low',
        anomaly_type: 'quality_anomaly',
        node_name: 'Node Day 6',
        description: 'Anomaly from 6 days ago',
        confidence: 0.75,
        expected_value: 7.0,
        actual_value: 6.8,
        deviation_percentage: 2.9,
        node_id: 'NODE_3',
        measurement_type: 'quality'
      }
    ];

    const mockNodesData = [
      { node_id: 'NODE_1', node_name: 'Node Day 1' },
      { node_id: 'NODE_2', node_name: 'Node Day 3' },
      { node_id: 'NODE_3', node_name: 'Node Day 6' }
    ];

    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        json: async () => mockAnomaliesData,
        ok: true
      })
      .mockResolvedValueOnce({
        json: async () => mockNodesData,
        ok: true
      });

    // Act
    render(<AnomaliesPage />);

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/Anomaly from 1 day ago/i)).toBeInTheDocument();
      expect(screen.getByText(/Anomaly from 3 days ago/i)).toBeInTheDocument();
      expect(screen.getByText(/Anomaly from 6 days ago/i)).toBeInTheDocument();
    });
  });
});