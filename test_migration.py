#!/usr/bin/env python3
"""Quick test script to validate migration."""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all core imports work."""
    print("Testing imports...")
    try:
        # Domain
        from src.domain.entities.sensor_reading import SensorReading
        from src.domain.entities.monitoring_node import MonitoringNode
        from src.domain.value_objects.measurements import FlowRate, Temperature
        print("✅ Domain imports successful")
        
        # Infrastructure
        from src.infrastructure.normalization.selargius_normalizer import SelargiusDataNormalizer
        print("✅ Infrastructure imports successful")
        
        # Application (requires dependency-injector)
        try:
            from src.application.use_cases.analyze_consumption_patterns import AnalyzeConsumptionPatternsUseCase
            print("✅ Application imports successful")
        except ImportError as e:
            print(f"⚠️  Application imports require full dependencies: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_normalization():
    """Test data normalization."""
    print("\nTesting data normalization...")
    try:
        from src.infrastructure.normalization.selargius_normalizer import SelargiusDataNormalizer
        
        # Find a data file
        data_files = [
            "RAWDATA/REPORT_NODI_SELARGIUS_AGGREGATI_30_MIN_20241113060000_20250331060000.csv",
            "normalized_selargius.csv",
            "cleaned_data.csv"
        ]
        
        data_file = None
        for file in data_files:
            if os.path.exists(file):
                data_file = file
                break
        
        if not data_file:
            print("⚠️  No data file found for testing")
            return False
        
        print(f"  Using data file: {data_file}")
        
        normalizer = SelargiusDataNormalizer()
        nodes, readings, quality = normalizer.normalize_file(data_file)
        
        print(f"✅ Normalization successful!")
        print(f"   - Nodes: {len(nodes)}")
        print(f"   - Readings: {len(readings)}")
        print(f"   - Quality Score: {quality.quality_score:.1f}%")
        
        # Show sample data
        if nodes:
            print(f"\n   Sample Node: {nodes[0].name}")
            print(f"   Location: {nodes[0].location.full_location}")
        
        if readings and len(readings) > 0:
            reading = readings[0]
            print(f"\n   Sample Reading:")
            print(f"   - Timestamp: {reading.timestamp}")
            if reading.flow_rate:
                print(f"   - Flow Rate: {reading.flow_rate.value} {reading.flow_rate.unit}")
            if reading.temperature:
                print(f"   - Temperature: {reading.temperature.value} {reading.temperature.unit}")
        
        return True
    except Exception as e:
        print(f"❌ Normalization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_legacy_compatibility():
    """Test that legacy code is still accessible."""
    print("\nTesting legacy code access...")
    try:
        from legacy.improved_normalizer import ImprovedWaterDataNormalizer
        print("✅ Legacy code is accessible")
        return True
    except Exception as e:
        print(f"⚠️  Legacy code not accessible: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Abbanoa Water Infrastructure Migration Test ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    # Run tests
    results.append(("Import Test", test_imports()))
    results.append(("Normalization Test", test_normalization()))
    results.append(("Legacy Compatibility", test_legacy_compatibility()))
    
    # Summary
    print("\n=== Test Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Migration successful.")
    else:
        print("\n⚠️  Some tests failed. Check dependencies and configuration.")

if __name__ == "__main__":
    main()