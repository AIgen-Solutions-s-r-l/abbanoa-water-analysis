'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import NodeDetailModal from '@/components/water/NodeDetailModal';
import {
  MapPinIcon,
  ActivityIcon,
  AlertCircleIcon,
  InfoIcon,
  LayersIcon,
  RefreshCwIcon
} from 'lucide-react';

// Import Leaflet CSS
import 'leaflet/dist/leaflet.css';

// Fix for Leaflet icons in Next.js
if (typeof window !== 'undefined') {
  require('./leaflet-config');
}

// Dynamic import for Leaflet components to avoid SSR issues
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false });
const Marker = dynamic(() => import('react-leaflet').then(mod => mod.Marker), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false });
const Polyline = dynamic(() => import('react-leaflet').then(mod => mod.Polyline), { ssr: false });
const CircleMarker = dynamic(() => import('react-leaflet').then(mod => mod.CircleMarker), { ssr: false });

interface Node {
  node_id: string;
  node_name: string;
  latitude: number;
  longitude: number;
  location_name: string;
  current_flow: number;
  current_pressure: number;
  status: 'optimal' | 'warning' | 'critical';
}

interface Pipe {
  pipe_id: string;
  from_node_id: string;
  to_node_id: string;
  from_lat: number;
  from_lon: number;
  to_lat: number;
  to_lon: number;
  diameter_mm: number;
  material: string;
  flow_rate: number;
}

const InfrastructureMapPage = () => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [pipes, setPipes] = useState<Pipe[]>([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [loading, setLoading] = useState(true);
  const [showLabels, setShowLabels] = useState(true);
  const [showFlow, setShowFlow] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mapReady, setMapReady] = useState(false);
  const [showNodeModal, setShowNodeModal] = useState(false);

  // Center of Selargius
  const mapCenter: [number, number] = [39.256656, 9.162556];

  useEffect(() => {
    fetchInfrastructureData();
    const interval = setInterval(fetchInfrastructureData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Set map ready after component mounts
  useEffect(() => {
    setMapReady(true);
  }, []);

  const fetchInfrastructureData = async () => {
    try {
      // Fetch nodes
      const nodesResponse = await fetch('/api/proxy/v1/nodes');
      if (!nodesResponse.ok) throw new Error('Failed to fetch nodes');
      const nodesData = await nodesResponse.json();

      // Fetch readings for each node
      const nodesWithReadings = await Promise.all(
        nodesData
          .filter((node: any) => node.location?.coordinates?.latitude && node.location?.coordinates?.longitude)
          .map(async (node: any) => {
            try {
              const readingsResponse = await fetch(`/api/proxy/v1/nodes/${node.id}/readings?limit=1`);
              const readings = readingsResponse.ok ? await readingsResponse.json() : [];
              return { ...node, readings };
            } catch {
              return { ...node, readings: [] };
            }
          })
      );

      // Transform nodes data
      const transformedNodes: Node[] = nodesWithReadings.map((node: any) => ({
        node_id: node.id,
        node_name: node.name || `Node ${node.id}`,
        latitude: parseFloat(node.location.coordinates.latitude),
        longitude: parseFloat(node.location.coordinates.longitude),
        location_name: node.location?.site_name || 'Unknown',
        current_flow: node.readings?.[0]?.flow_rate || 0,
        current_pressure: node.readings?.[0]?.pressure || 0,
        status: determineNodeStatus(node.readings?.[0])
      }));

      console.log('Transformed nodes:', transformedNodes);
      setNodes(transformedNodes);

      // Generate pipes
      const generatedPipes: Pipe[] = [];
      for (let i = 0; i < transformedNodes.length; i++) {
        for (let j = i + 1; j < transformedNodes.length; j++) {
          const node1 = transformedNodes[i];
          const node2 = transformedNodes[j];
          const distance = calculateDistance(
            node1.latitude, node1.longitude,
            node2.latitude, node2.longitude
          );

          // Connect nodes within ~1km
          if (distance < 1000) {
            generatedPipes.push({
              pipe_id: `PIPE_${node1.node_id}_${node2.node_id}`,
              from_node_id: node1.node_id,
              to_node_id: node2.node_id,
              from_lat: node1.latitude,
              from_lon: node1.longitude,
              to_lat: node2.latitude,
              to_lon: node2.longitude,
              diameter_mm: 200 + Math.floor(Math.random() * 200),
              material: Math.random() > 0.5 ? 'Steel' : 'PVC',
              flow_rate: Math.random() * 50
            });
          }
        }
      }

      setPipes(generatedPipes);
    } catch (error) {
      console.error('Error fetching infrastructure data:', error);
      setError('Failed to load infrastructure data');
    } finally {
      setLoading(false);
    }
  };

  const determineNodeStatus = (reading: any): 'optimal' | 'warning' | 'critical' => {
    if (!reading) return 'warning';
    if (reading.pressure < 2 || reading.pressure > 8) return 'critical';
    if (reading.pressure < 3 || reading.pressure > 6) return 'warning';
    return 'optimal';
  };

  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
    const R = 6371e3; // Earth's radius in meters
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
      Math.cos(φ1) * Math.cos(φ2) *
      Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
  };

  const getNodeColor = (status: string) => {
    switch (status) {
      case 'optimal': return '#10b981';
      case 'warning': return '#f59e0b';
      case 'critical': return '#ef4444';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-96">
          <div className="animate-pulse text-gray-500">Loading infrastructure map...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
          Infrastructure Map
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Real-time view of the water distribution network in Selargius
        </p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Map */}
        <Card className="lg:col-span-3 p-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Network Overview - Selargius</h2>
            <div className="flex gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowLabels(!showLabels)}
                className={showLabels ? 'bg-blue-100 dark:bg-blue-900' : ''}
              >
                <LayersIcon className="h-4 w-4 mr-1" />
                Labels
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowFlow(!showFlow)}
                className={showFlow ? 'bg-blue-100 dark:bg-blue-900' : ''}
              >
                <ActivityIcon className="h-4 w-4 mr-1" />
                Pipes
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={fetchInfrastructureData}
              >
                <RefreshCwIcon className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Leaflet Map */}
          <div className="relative rounded-lg overflow-hidden" style={{ height: '600px' }}>
            {mapReady && (
              <MapContainer
                center={mapCenter}
                zoom={15}
                style={{ height: '100%', width: '100%' }}
              >
                {/* OpenStreetMap Tiles */}
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {/* Pipes - Draw twice for glow effect */}
                {showFlow && pipes.map((pipe) => (
                  <React.Fragment key={pipe.pipe_id}>
                    {/* Glow layer */}
                    <Polyline
                      positions={[[pipe.from_lat, pipe.from_lon], [pipe.to_lat, pipe.to_lon]]}
                      color={pipe.material === 'PVC' ? '#60a5fa' : '#3b82f6'}
                      weight={Math.max(8, Math.sqrt(pipe.diameter_mm / 30))}
                      opacity={0.3}
                    />
                    {/* Main pipe */}
                    <Polyline
                      positions={[[pipe.from_lat, pipe.from_lon], [pipe.to_lat, pipe.to_lon]]}
                      color={pipe.material === 'PVC' ? '#2563eb' : '#1e40af'}
                      weight={Math.max(5, Math.sqrt(pipe.diameter_mm / 40))}
                      opacity={0.9}
                      dashArray={pipe.material === 'PVC' ? '12, 6' : undefined}
                    />
                  </React.Fragment>
                ))}

                {/* Nodes */}
                {nodes.map((node) => (
                  <CircleMarker
                    key={node.node_id}
                    center={[node.latitude, node.longitude]}
                    radius={selectedNode?.node_id === node.node_id ? 16 : 12}
                    fillColor={getNodeColor(node.status)}
                    color="#fff"
                    weight={3}
                    opacity={1}
                    fillOpacity={0.9}
                    eventHandlers={{
                      click: () => {
                        setSelectedNode(node);
                        setShowNodeModal(true);
                      },
                    }}
                  >
                    <Popup>
                      <div className="p-2">
                        <h3 className="font-semibold">{node.node_name}</h3>
                        <p className="text-sm text-gray-600">Click for details</p>
                      </div>
                    </Popup>
                  </CircleMarker>
                ))}
              </MapContainer>
            )}
          </div>

          {/* Legend */}
          <div className="mt-4 flex items-center justify-between">
            <div className="flex gap-6">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Optimal</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-yellow-500 rounded-full"></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Warning</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Critical</span>
              </div>
            </div>
            <div className="text-sm text-gray-500">
              {nodes.length} nodes • {pipes.length} connections
            </div>
          </div>
        </Card>

        {/* Side Panel */}
        <div className="space-y-4">
          {/* Selected Node Details */}
          {selectedNode && (
            <Card className="p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <MapPinIcon className="h-4 w-4" />
                {selectedNode.node_name}
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">ID:</span>
                  <span className="font-medium">{selectedNode.node_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Location:</span>
                  <span className="font-medium">{selectedNode.location_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Coordinates:</span>
                  <span className="font-mono text-xs">
                    {selectedNode.latitude.toFixed(6)}, {selectedNode.longitude.toFixed(6)}
                  </span>
                </div>
                <hr className="my-2" />
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Flow:</span>
                  <span className="font-medium">{selectedNode.current_flow.toFixed(1)} L/s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Pressure:</span>
                  <span className="font-medium">{selectedNode.current_pressure.toFixed(1)} bar</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Status:</span>
                  <span className={`font-medium capitalize text-${
                    selectedNode.status === 'optimal' ? 'green' : 
                    selectedNode.status === 'warning' ? 'yellow' : 'red'
                  }-600`}>
                    {selectedNode.status}
                  </span>
                </div>
              </div>
            </Card>
          )}

          {/* System Overview */}
          <Card className="p-4">
            <h3 className="font-semibold mb-3">System Overview</h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600 dark:text-gray-400">Network Health</span>
                  <span className="font-medium">
                    {Math.round((nodes.filter(n => n.status === 'optimal').length / nodes.length) * 100)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{
                      width: `${(nodes.filter(n => n.status === 'optimal').length / nodes.length) * 100}%`
                    }}
                  />
                </div>
              </div>

              <div className="pt-2 space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Total Flow</span>
                  <span className="font-medium">
                    {nodes.reduce((sum, n) => sum + n.current_flow, 0).toFixed(1)} L/s
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Avg Pressure</span>
                  <span className="font-medium">
                    {(nodes.reduce((sum, n) => sum + n.current_pressure, 0) / nodes.length).toFixed(1)} bar
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Active Alerts</span>
                  <span className="font-medium text-red-600">
                    {nodes.filter(n => n.status === 'critical').length}
                  </span>
                </div>
              </div>
            </div>
          </Card>

          {/* Quick Actions */}
          <Card className="p-4">
            <h3 className="font-semibold mb-3">Quick Actions</h3>
            <div className="space-y-2">
              <Button variant="secondary" className="w-full justify-start">
                <AlertCircleIcon className="h-4 w-4 mr-2" />
                View Alerts
              </Button>
              <Button variant="secondary" className="w-full justify-start">
                <ActivityIcon className="h-4 w-4 mr-2" />
                Flow Analysis
              </Button>
              <Button variant="secondary" className="w-full justify-start">
                <InfoIcon className="h-4 w-4 mr-2" />
                Network Report
              </Button>
            </div>
          </Card>
        </div>
      </div>

      {/* Node Detail Modal */}
      {showNodeModal && selectedNode && (
        <NodeDetailModal
          node={selectedNode}
          onClose={() => setShowNodeModal(false)}
        />
      )}
    </div>
  );
};

export default InfrastructureMapPage; 