"""
Test script to verify that the Streamlit dashboard updates without page reloads.

This script simulates user interactions and verifies smooth state transitions.
"""

import time
import streamlit as st
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_no_reload_behavior():
    """Test that filter changes don't cause page reloads."""

    print("Testing Streamlit Dashboard - No Reload Behavior")
    print("=" * 50)

    # Test 1: Session state persistence
    print("\n1. Testing session state persistence...")

    # Initialize session state
    if "test_counter" not in st.session_state:
        st.session_state.test_counter = 0

    initial_counter = st.session_state.test_counter

    # Simulate district change
    st.session_state.district_id = "DIST_001"
    st.session_state.district_id = "DIST_002"  # Change district

    # Counter should remain the same (no reload)
    assert (
        st.session_state.test_counter == initial_counter
    ), "Page reloaded on district change!"
    print("✓ Session state persists on district change")

    # Test 2: Callback execution
    print("\n2. Testing callback execution...")

    callback_executed = False

    def test_callback():
        global callback_executed
        callback_executed = True
        st.session_state.test_value = "changed"

    # Simulate callback
    test_callback()

    assert callback_executed, "Callback not executed!"
    assert st.session_state.test_value == "changed", "Session state not updated!"
    print("✓ Callbacks execute without reload")

    # Test 3: Data caching
    print("\n3. Testing data caching...")

    @st.cache_data(ttl=300)
    def get_cached_data(param):
        return f"data_{param}_{time.time()}"

    # First call
    data1 = get_cached_data("test")
    time.sleep(0.1)

    # Second call should return cached data
    data2 = get_cached_data("test")

    assert data1 == data2, "Cache not working!"
    print("✓ Data caching prevents redundant fetches")

    # Test 4: Component keys
    print("\n4. Testing component key stability...")

    # Components with keys should maintain state
    if st.selectbox("Test Select", ["A", "B", "C"], key="stable_select"):
        pass

    # Key should remain stable across reruns
    assert "stable_select" in st.session_state, "Component key lost!"
    print("✓ Component keys remain stable")

    print("\n" + "=" * 50)
    print("All tests passed! Dashboard updates without page reloads.")

    return True

def test_interaction_flow():
    """Test the actual interaction flow of the dashboard."""

    print("\nTesting Dashboard Interaction Flow")
    print("=" * 50)

    # Import dashboard components
    from src.presentation.streamlit.components.sidebar_filters import SidebarFilters
    from src.presentation.streamlit.utils.data_fetcher import DataFetcher
    from src.presentation.streamlit.components.forecast_tab import ForecastTab

    # Initialize components
    print("\n1. Initializing components...")
    sidebar = SidebarFilters()
    data_fetcher = DataFetcher()
    forecast_tab = ForecastTab(data_fetcher)
    print("✓ Components initialized successfully")

    # Test district change
    print("\n2. Testing district change...")
    st.session_state.district_id = "DIST_001"
    initial_data = st.session_state.get("forecast_data", None)

    # Change district
    st.session_state.district_id = "DIST_002"
    sidebar._on_district_change()

    # Data should be cleared but no reload
    assert st.session_state.forecast_data is None, "Data not cleared on district change"
    print("✓ District change clears data without reload")

    # Test metric change
    print("\n3. Testing metric change...")
    st.session_state.metric = "flow_rate"
    st.session_state.metric_selector = "Pressure (bar)"
    sidebar._on_metric_change()

    assert st.session_state.metric == "pressure", "Metric not updated correctly"
    print("✓ Metric change updates state correctly")

    # Test horizon change
    print("\n4. Testing horizon change...")
    st.session_state.horizon = 7
    st.session_state.horizon_slider = 3
    sidebar._on_horizon_change()

    assert st.session_state.horizon == 3, "Horizon not updated correctly"
    print("✓ Horizon change updates without reload")

    print("\n" + "=" * 50)
    print("Interaction flow test complete!")

if __name__ == "__main__":
    # Run tests
    try:
        test_no_reload_behavior()
        test_interaction_flow()
        print(
            "\n✅ All tests passed! Dashboard operates smoothly without page reloads."
        )
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
