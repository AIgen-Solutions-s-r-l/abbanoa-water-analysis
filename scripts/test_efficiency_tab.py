#!/usr/bin/env python3

"""
Test script for the efficiency tab to ensure it's working with updated node mappings.
This script tests the key efficiency calculations and data fetching methods.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.presentation.streamlit.components.efficiency_tab import EfficiencyTab


def test_efficiency_tab():
    """Test the efficiency tab functionality."""

    print("🧪 Testing Network Efficiency Tab...")
    print("=" * 60)

    try:
        # Initialize efficiency tab with a dummy use case (not needed for our tests)
        efficiency_tab = EfficiencyTab(calculate_efficiency_use_case=None)

        # Test 1: Overall efficiency data
        print("\n1. Testing Overall Efficiency Data...")
        efficiency_data = efficiency_tab._get_efficiency_data("Last 24 Hours")

        print(f"   ✓ Active nodes: {efficiency_data.get('active_nodes', 0)}/8")
        print(f"   ✓ Total readings: {efficiency_data.get('total_readings', 0)}")
        print(
            f"   ✓ Efficiency percentage: {efficiency_data.get('efficiency_percentage', 0):.1f}%"
        )
        print(f"   ✓ Loss percentage: {efficiency_data.get('loss_percentage', 0):.1f}%")
        print(
            f"   ✓ Average pressure: {efficiency_data.get('average_pressure', 0):.2f} bar"
        )
        print(f"   ✓ Average flow: {efficiency_data.get('average_flow', 0):.2f} m³/h")
        print(
            f"   ✓ Energy efficiency: {efficiency_data.get('energy_efficiency', 0):.2f} kWh/m³"
        )

        # Test 2: Node-specific efficiency
        print("\n2. Testing Node-Specific Efficiency...")
        node_efficiency = efficiency_tab._get_node_efficiency_data()

        for node_name, efficiency_value in node_efficiency.items():
            print(f"   ✓ {node_name}: {efficiency_value:.1f}%")

        # Test 3: Pressure analysis
        print("\n3. Testing Pressure Analysis...")
        pressure_data = efficiency_tab._get_pressure_analysis_data()

        for node_name, pressure_value in pressure_data["current_pressure"].items():
            print(f"   ✓ {node_name}: {pressure_value:.2f} bar")

        # Test 4: Loss distribution
        print("\n4. Testing Loss Distribution...")
        loss_data = efficiency_tab._get_loss_distribution_data()

        for loss_type, loss_value in loss_data.items():
            print(f"   ✓ {loss_type}: {loss_value:.1f}%")

        # Test 5: Efficiency trends
        print("\n5. Testing Efficiency Trends...")
        trend_data = efficiency_tab._get_efficiency_trends("Last 24 Hours")

        print(f"   ✓ Trend timestamps: {len(trend_data.get('timestamps', []))} points")
        print(
            f"   ✓ Efficiency trend: {len(trend_data.get('efficiency_trend', []))} points"
        )
        print(f"   ✓ Water loss trend: {len(trend_data.get('water_loss', []))} points")
        print(
            f"   ✓ Energy consumption trend: {len(trend_data.get('energy_consumption', []))} points"
        )

        # Summary
        print("\n" + "=" * 60)
        print("✅ EFFICIENCY TAB TEST RESULTS:")
        print("=" * 60)

        if efficiency_data.get("total_readings", 0) > 0:
            print(
                f"🎯 SUCCESS: Found {efficiency_data.get('total_readings', 0)} readings from {efficiency_data.get('active_nodes', 0)} nodes"
            )
            print(
                f"📊 Overall efficiency: {efficiency_data.get('efficiency_percentage', 0):.1f}%"
            )
            print(f"💧 Water loss: {efficiency_data.get('loss_percentage', 0):.1f}%")
            print(
                f"⚡ Energy efficiency: {efficiency_data.get('energy_efficiency', 0):.2f} kWh/m³"
            )
            print(
                f"🔧 Average pressure: {efficiency_data.get('average_pressure', 0):.2f} bar"
            )
        else:
            print("❌ No data found - efficiency tab may not be working correctly")

        # Test node mappings
        print("\n🔍 NODE MAPPING VERIFICATION:")
        print("-" * 40)

        expected_nodes = [
            "Primary Station",
            "Secondary Station",
            "Distribution A",
            "Distribution B",
            "Junction C",
            "Supply Control",
            "Pressure Station",
            "Remote Point",
        ]

        for node_name in expected_nodes:
            if node_name in node_efficiency:
                efficiency_val = node_efficiency[node_name]
                pressure_val = pressure_data["current_pressure"].get(node_name, 0)
                status = "✅ ACTIVE" if efficiency_val > 0 else "⚠️  NO DATA"
                print(
                    f"   {node_name}: {efficiency_val:.1f}% efficiency, {pressure_val:.2f} bar - {status}"
                )
            else:
                print(f"   {node_name}: ❌ NOT FOUND")

        print("\n" + "=" * 60)
        print("✅ EFFICIENCY TAB TEST COMPLETED!")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_efficiency_tab()
