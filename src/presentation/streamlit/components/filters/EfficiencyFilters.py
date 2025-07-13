"""
EfficiencyFilters component for drill-down filtering functionality.

This component provides multi-select filters for district and node selection
specifically for the efficiency analysis tab.
"""

from typing import Dict, List, Optional, Tuple
import streamlit as st


class EfficiencyFilters:
    """
    Filters component for efficiency analysis drill-down.
    
    Features:
    - Multi-select district filtering
    - Multi-select node filtering
    - Hierarchical filtering (districts -> nodes)
    - Session state management
    - Filter reset functionality
    """
    
    def __init__(self):
        """Initialize the efficiency filters."""
        self.districts = {
            "DIST_001": "Central Business District",
            "DIST_002": "Residential North",
            "DIST_003": "Industrial South",
            "DIST_004": "Suburban East",
            "DIST_005": "Coastal West"
        }
        
        # Node mapping by district
        self.nodes_by_district = {
            "DIST_001": [
                "Primary Station",
                "Secondary Station",
                "Distribution A"
            ],
            "DIST_002": [
                "Distribution B",
                "Junction C",
                "Supply Control"
            ],
            "DIST_003": [
                "Pressure Station",
                "Remote Point"
            ],
            "DIST_004": [
                "Monitor Point A",
                "Monitor Point B"
            ],
            "DIST_005": [
                "Coastal Station",
                "Marine Monitor"
            ]
        }
        
        # Initialize session state
        self._init_session_state()
    
    def _init_session_state(self) -> None:
        """Initialize session state for filter values."""
        if "efficiency_selected_districts" not in st.session_state:
            st.session_state.efficiency_selected_districts = []
        if "efficiency_selected_nodes" not in st.session_state:
            st.session_state.efficiency_selected_nodes = []
        if "efficiency_filter_mode" not in st.session_state:
            st.session_state.efficiency_filter_mode = "district"
    
    def render(self) -> Tuple[List[str], List[str]]:
        """
        Render the efficiency filters and return selected values.
        
        Returns:
            Tuple of (selected_districts, selected_nodes)
        """
        
        st.markdown("### 🔍 Drill-Down Filters")
        
        # Filter mode selection
        filter_mode = st.radio(
            "Filter Mode",
            options=["district", "node", "both"],
            format_func=lambda x: {
                "district": "📍 District Level",
                "node": "🏗️ Node Level", 
                "both": "📊 District + Node"
            }[x],
            index=0,
            key="efficiency_filter_mode",
            horizontal=True,
            help="Choose how to filter the efficiency data"
        )
        
        selected_districts = []
        selected_nodes = []
        
        if filter_mode in ["district", "both"]:
            selected_districts = self._render_district_filter()
        
        if filter_mode in ["node", "both"]:
            selected_nodes = self._render_node_filter(
                available_districts=selected_districts if filter_mode == "both" else None
            )
        
        # Filter actions
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🔄 Reset Filters", use_container_width=True):
                self._reset_filters()
                st.rerun()
        
        with col2:
            if st.button("📊 Apply Filters", use_container_width=True):
                st.success("Filters applied!")
        
        with col3:
            if st.button("🔍 Show All", use_container_width=True):
                self._show_all_data()
                st.rerun()
        
        # Display current filter summary
        self._display_filter_summary(selected_districts, selected_nodes)
        
        return selected_districts, selected_nodes
    
    def _render_district_filter(self) -> List[str]:
        """Render district multi-select filter."""
        
        st.markdown("#### 📍 District Selection")
        
        selected_districts = st.multiselect(
            label="Select Districts",
            options=list(self.districts.keys()),
            format_func=lambda x: f"{x} - {self.districts[x]}",
            default=st.session_state.efficiency_selected_districts,
            key="efficiency_selected_districts",
            help="Select one or more districts to analyze"
        )
        
        if selected_districts:
            # Show district information
            with st.expander("ℹ️ District Information"):
                for district in selected_districts:
                    district_name = self.districts[district]
                    node_count = len(self.nodes_by_district.get(district, []))
                    
                    st.markdown(f"""
                    **{district}** - {district_name}
                    - Nodes: {node_count}
                    - Status: ✅ Active
                    """)
        
        return selected_districts
    
    def _render_node_filter(self, available_districts: Optional[List[str]] = None) -> List[str]:
        """Render node multi-select filter."""
        
        st.markdown("#### 🏗️ Node Selection")
        
        # Get available nodes based on district selection
        if available_districts:
            available_nodes = []
            for district in available_districts:
                available_nodes.extend(self.nodes_by_district.get(district, []))
        else:
            # All nodes available
            available_nodes = []
            for nodes in self.nodes_by_district.values():
                available_nodes.extend(nodes)
        
        if not available_nodes:
            st.warning("No nodes available. Please select districts first.")
            return []
        
        # Add grouping options
        grouping_options = ["All Nodes"] + available_nodes
        
        selected_nodes = st.multiselect(
            label="Select Nodes",
            options=grouping_options,
            default=st.session_state.efficiency_selected_nodes,
            key="efficiency_selected_nodes",
            help="Select specific nodes to analyze"
        )
        
        # Handle "All Nodes" selection
        if "All Nodes" in selected_nodes:
            selected_nodes = available_nodes
        
        if selected_nodes:
            # Show node information
            with st.expander("ℹ️ Node Information"):
                for node in selected_nodes:
                    # Find which district this node belongs to
                    district = None
                    for d, nodes in self.nodes_by_district.items():
                        if node in nodes:
                            district = d
                            break
                    
                    st.markdown(f"""
                    **{node}**
                    - District: {district} - {self.districts.get(district, 'Unknown')}
                    - Status: ✅ Active
                    - Type: Monitoring Node
                    """)
        
        return selected_nodes
    
    def _reset_filters(self) -> None:
        """Reset all filters to default values."""
        st.session_state.efficiency_selected_districts = []
        st.session_state.efficiency_selected_nodes = []
        st.session_state.efficiency_filter_mode = "district"
    
    def _show_all_data(self) -> None:
        """Set filters to show all available data."""
        st.session_state.efficiency_selected_districts = list(self.districts.keys())
        
        # Include all nodes
        all_nodes = []
        for nodes in self.nodes_by_district.values():
            all_nodes.extend(nodes)
        st.session_state.efficiency_selected_nodes = all_nodes
    
    def _display_filter_summary(self, selected_districts: List[str], selected_nodes: List[str]) -> None:
        """Display a summary of current filters."""
        
        st.markdown("---")
        st.markdown("#### 📋 Current Filters")
        
        # Create summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            district_count = len(selected_districts)
            total_districts = len(self.districts)
            st.metric(
                "Districts",
                f"{district_count}/{total_districts}",
                f"{(district_count/total_districts*100):.0f}% coverage"
            )
        
        with col2:
            node_count = len(selected_nodes)
            total_nodes = sum(len(nodes) for nodes in self.nodes_by_district.values())
            st.metric(
                "Nodes",
                f"{node_count}/{total_nodes}",
                f"{(node_count/total_nodes*100):.0f}% coverage" if total_nodes > 0 else "0% coverage"
            )
        
        with col3:
            filter_mode = st.session_state.efficiency_filter_mode
            st.metric(
                "Mode",
                filter_mode.title(),
                "Active filtering"
            )
        
        # Show active filters
        if selected_districts or selected_nodes:
            st.markdown("**Active Filters:**")
            
            if selected_districts:
                district_names = [self.districts[d] for d in selected_districts]
                st.markdown(f"• **Districts**: {', '.join(district_names)}")
            
            if selected_nodes:
                st.markdown(f"• **Nodes**: {', '.join(selected_nodes[:3])}")
                if len(selected_nodes) > 3:
                    st.markdown(f"  ... and {len(selected_nodes) - 3} more")
        else:
            st.info("No filters active - showing all data")
    
    def render_compact(self) -> Tuple[List[str], List[str]]:
        """
        Render a compact version of the filters for inline use.
        
        Returns:
            Tuple of (selected_districts, selected_nodes)
        """
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_districts = st.multiselect(
                "📍 Districts",
                options=list(self.districts.keys()),
                format_func=lambda x: self.districts[x],
                key="efficiency_districts_compact",
                help="Filter by district"
            )
        
        with col2:
            # Get available nodes based on district selection
            if selected_districts:
                available_nodes = []
                for district in selected_districts:
                    available_nodes.extend(self.nodes_by_district.get(district, []))
            else:
                available_nodes = []
                for nodes in self.nodes_by_district.values():
                    available_nodes.extend(nodes)
            
            selected_nodes = st.multiselect(
                "🏗️ Nodes",
                options=available_nodes,
                key="efficiency_nodes_compact",
                help="Filter by node"
            )
        
        return selected_districts, selected_nodes
    
    def get_filtered_data_params(self) -> Dict[str, str]:
        """
        Get parameters for filtered data requests.
        
        Returns:
            Dictionary with filter parameters for API calls
        """
        
        selected_districts = st.session_state.get("efficiency_selected_districts", [])
        selected_nodes = st.session_state.get("efficiency_selected_nodes", [])
        
        params = {}
        
        if selected_districts:
            params["districts"] = ",".join(selected_districts)
        
        if selected_nodes:
            params["nodes"] = ",".join(selected_nodes)
        
        return params
    
    def apply_filters_to_data(self, data, district_column: str = "district", node_column: str = "node"):
        """
        Apply current filters to a dataset.
        
        Args:
            data: DataFrame or data structure to filter
            district_column: Name of the district column
            node_column: Name of the node column
            
        Returns:
            Filtered data
        """
        
        selected_districts = st.session_state.get("efficiency_selected_districts", [])
        selected_nodes = st.session_state.get("efficiency_selected_nodes", [])
        
        # Apply district filter
        if selected_districts and hasattr(data, 'loc'):
            data = data[data[district_column].isin(selected_districts)]
        
        # Apply node filter  
        if selected_nodes and hasattr(data, 'loc'):
            data = data[data[node_column].isin(selected_nodes)]
        
        return data 