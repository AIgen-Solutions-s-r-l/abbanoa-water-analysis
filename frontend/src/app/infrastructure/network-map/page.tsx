'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { 
  Network, 
  Droplets, 
  GitBranch, 
  Activity,
  MapPin,
  AlertCircle,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  Circle
} from 'lucide-react';

interface NetworkNode {
  id: string;
  name: string;
  type: string;
  location: {
    lat: number | null;
    lng: number | null;
    name?: string;
  };
  active?: boolean;
  metrics?: {
    avg_flow: number;
    avg_pressure: number;
    last_reading: string;
  };
  children?: NetworkNode[];
}

interface NetworkConnection {
  source: string;
  target: string;
  type: string;
  direction: string;
  properties?: {
    diameter_mm?: number;
    length_m?: number;
    material?: string;
    status?: string;
  };
}

interface NetworkTopology {
  nodes: {
    [key: string]: NetworkNode[];
  };
  connections: NetworkConnection[];
  summary: {
    total_nodes: number;
    total_connections: number;
    node_types: string[];
    active_nodes: number;
  };
}

const nodeTypeColors: { [key: string]: string } = {
  source: 'bg-blue-500',
  reservoir: 'bg-cyan-500',
  hub: 'bg-purple-500',
  junction: 'bg-yellow-500',
  district: 'bg-green-500',
  main: 'bg-gray-500',
  distribution: 'bg-orange-500',
  secondary: 'bg-pink-500'
};

const nodeTypeIcons: { [key: string]: React.ReactNode } = {
  source: <Droplets className="w-4 h-4" />,
  reservoir: <Circle className="w-4 h-4" />,
  hub: <Network className="w-4 h-4" />,
  junction: <GitBranch className="w-4 h-4" />,
  district: <MapPin className="w-4 h-4" />,
};

export default function NetworkMapPage() {
  const [topology, setTopology] = useState<NetworkTopology | null>(null);
  const [hierarchy, setHierarchy] = useState<NetworkNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [selectedNode, setSelectedNode] = useState<NetworkNode | null>(null);
  const [activeTab, setActiveTab] = useState('hierarchy');

  useEffect(() => {
    fetchNetworkData();
  }, []);

  const fetchNetworkData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch topology data
      const topologyRes = await fetch('/api/v1/network/topology?include_metrics=true');
      if (!topologyRes.ok) {
        throw new Error(`Failed to fetch topology: ${topologyRes.statusText}`);
      }
      const topologyData = await topologyRes.json();
      setTopology(topologyData.topology);

      // Fetch hierarchy data
      const hierarchyRes = await fetch('/api/v1/network/topology/hierarchy');
      if (!hierarchyRes.ok) {
        throw new Error(`Failed to fetch hierarchy: ${hierarchyRes.statusText}`);
      }
      const hierarchyData = await hierarchyRes.json();
      setHierarchy(hierarchyData.hierarchy);
      
    } catch (err) {
      console.error('Error fetching network data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load network data');
    } finally {
      setLoading(false);
    }
  };

  const toggleNodeExpansion = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  const renderHierarchyNode = (node: NetworkNode, level: number = 0) => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expandedNodes.has(node.id);
    
    return (
      <div key={node.id} className="mb-2">
        <div 
          className={`flex items-center p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors ${
            selectedNode?.id === node.id ? 'bg-blue-50 border-blue-300 border' : ''
          }`}
          style={{ marginLeft: `${level * 24}px` }}
          onClick={() => {
            setSelectedNode(node);
            if (hasChildren) {
              toggleNodeExpansion(node.id);
            }
          }}
        >
          {hasChildren && (
            <button
              className="mr-2"
              onClick={(e) => {
                e.stopPropagation();
                toggleNodeExpansion(node.id);
              }}
            >
              {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </button>
          )}
          
          <div className={`p-1 rounded ${nodeTypeColors[node.type] || 'bg-gray-400'} text-white mr-3`}>
            {nodeTypeIcons[node.type] || <Circle className="w-4 h-4" />}
          </div>
          
          <div className="flex-1">
            <div className="font-medium">{node.name}</div>
            <div className="text-sm text-gray-500">
              {node.type} • {node.id}
            </div>
          </div>
          
          {node.metrics && (
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <span>Flow: {node.metrics.avg_flow.toFixed(1)} L/s</span>
              <span>Pressure: {node.metrics.avg_pressure.toFixed(1)} bar</span>
            </div>
          )}
        </div>
        
        {hasChildren && isExpanded && (
          <div>
            {node.children!.map(child => renderHierarchyNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  const renderNodesByType = () => {
    if (!topology) return null;
    
    return (
      <div className="space-y-6">
        {Object.entries(topology.nodes).map(([type, nodes]) => (
          <Card key={type}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className={`p-2 rounded ${nodeTypeColors[type] || 'bg-gray-400'} text-white`}>
                  {nodeTypeIcons[type] || <Circle className="w-5 h-5" />}
                </div>
                <span className="capitalize">{type} Nodes</span>
                <span className="text-sm text-gray-500">({nodes.length})</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {nodes.map((node: NetworkNode) => (
                  <div
                    key={node.id}
                    className={`p-3 border rounded-lg hover:shadow-md transition-shadow cursor-pointer ${
                      selectedNode?.id === node.id ? 'border-blue-500 bg-blue-50' : ''
                    }`}
                    onClick={() => setSelectedNode(node)}
                  >
                    <div className="font-medium">{node.name}</div>
                    <div className="text-sm text-gray-500 mt-1">
                      ID: {node.id}
                    </div>
                    {node.location?.name && (
                      <div className="text-sm text-gray-600 mt-1 flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {node.location.name}
                      </div>
                    )}
                    {node.metrics && (
                      <div className="mt-2 text-xs text-gray-600 space-y-1">
                        <div>Flow: {node.metrics.avg_flow.toFixed(1)} L/s</div>
                        <div>Pressure: {node.metrics.avg_pressure.toFixed(1)} bar</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  const renderConnections = () => {
    if (!topology) return null;
    
    return (
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Network Connections</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Source</th>
                    <th className="text-left p-2">Target</th>
                    <th className="text-left p-2">Type</th>
                    <th className="text-left p-2">Direction</th>
                    <th className="text-left p-2">Properties</th>
                  </tr>
                </thead>
                <tbody>
                  {topology.connections.map((conn, idx) => (
                    <tr key={idx} className="border-b hover:bg-gray-50">
                      <td className="p-2">{conn.source}</td>
                      <td className="p-2">{conn.target}</td>
                      <td className="p-2">
                        <span className="px-2 py-1 bg-gray-100 rounded text-xs">
                          {conn.type}
                        </span>
                      </td>
                      <td className="p-2">
                        <span className={`px-2 py-1 rounded text-xs ${
                          conn.direction === 'bidirectional' 
                            ? 'bg-blue-100 text-blue-700' 
                            : 'bg-green-100 text-green-700'
                        }`}>
                          {conn.direction}
                        </span>
                      </td>
                      <td className="p-2 text-xs">
                        {conn.properties?.diameter_mm && (
                          <span className="mr-2">⌀ {conn.properties.diameter_mm}mm</span>
                        )}
                        {conn.properties?.length_m && (
                          <span className="mr-2">L: {conn.properties.length_m}m</span>
                        )}
                        {conn.properties?.material && (
                          <span>{conn.properties.material}</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-2">Loading network data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error}
          </AlertDescription>
        </Alert>
        <Button onClick={fetchNetworkData} className="mt-4">
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Water Infrastructure Network Map</h1>
        <p className="text-gray-600">
          Visualize and explore the water distribution network hierarchy and connections
        </p>
      </div>

      {topology && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-blue-600">
                {topology.summary.total_nodes}
              </div>
              <div className="text-sm text-gray-600">Total Nodes</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-green-600">
                {topology.summary.active_nodes}
              </div>
              <div className="text-sm text-gray-600">Active Nodes</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-purple-600">
                {topology.summary.total_connections}
              </div>
              <div className="text-sm text-gray-600">Connections</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-orange-600">
                {topology.summary.node_types.length}
              </div>
              <div className="text-sm text-gray-600">Node Types</div>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-4">
          <TabsTrigger value="hierarchy">Hierarchy View</TabsTrigger>
          <TabsTrigger value="nodes">Nodes by Type</TabsTrigger>
          <TabsTrigger value="connections">Connections</TabsTrigger>
        </TabsList>

        <TabsContent value="hierarchy">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GitBranch className="w-5 h-5" />
                Network Hierarchy
              </CardTitle>
            </CardHeader>
            <CardContent>
              {hierarchy.length > 0 ? (
                <div>
                  {hierarchy.map(node => renderHierarchyNode(node))}
                </div>
              ) : (
                <div className="text-gray-500 text-center py-8">
                  No hierarchy data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="nodes">
          {renderNodesByType()}
        </TabsContent>

        <TabsContent value="connections">
          {renderConnections()}
        </TabsContent>
      </Tabs>

      {selectedNode && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Selected Node Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="font-semibold">Name:</div>
                <div>{selectedNode.name}</div>
              </div>
              <div>
                <div className="font-semibold">ID:</div>
                <div>{selectedNode.id}</div>
              </div>
              <div>
                <div className="font-semibold">Type:</div>
                <div className="capitalize">{selectedNode.type}</div>
              </div>
              <div>
                <div className="font-semibold">Status:</div>
                <div>{selectedNode.active ? 'Active' : 'Inactive'}</div>
              </div>
              {selectedNode.location && (
                <>
                  <div>
                    <div className="font-semibold">Location:</div>
                    <div>{selectedNode.location.name || 'N/A'}</div>
                  </div>
                  <div>
                    <div className="font-semibold">Coordinates:</div>
                    <div>
                      {selectedNode.location.lat && selectedNode.location.lng
                        ? `${selectedNode.location.lat.toFixed(6)}, ${selectedNode.location.lng.toFixed(6)}`
                        : 'N/A'}
                    </div>
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}