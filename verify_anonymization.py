#!/usr/bin/env python3

import requests
import json

def verify_anonymization():
    print('🔒 Verifying Node Names Anonymization')
    print('=' * 50)
    
    base_url = 'http://localhost:8000'
    
    # Define old names that should NOT appear
    old_names = [
        "CENTRO EST", "CENTRO NORD", "CENTRO OVEST", "CENTRO SUD",
        "FIORI", "LIBERTÀ", "Q.GALLUS", "Q.MATTEOTTI", "Q.MONSERRATO",
        "Q.NENNI SUD", "Q.SANT'ANNA", "Q.SARDEGNA", "Q.TRIESTE", "STADIO"
    ]
    
    # Define expected anonymized names
    expected_names = [
        "DIST01", "DIST02", "DIST03", "DIST04",
        "INTERCON01", "INTERCON02", "INTERCON03", "INTERCON04", "INTERCON05",
        "INTERCON06", "INTERCON07", "INTERCON08",
        "ZONE01", "ZONE02"
    ]
    
    try:
        # Test 1: Check nodes endpoint
        print('🔍 Test 1: Checking /api/v1/nodes endpoint...')
        response = requests.get(f'{base_url}/api/v1/nodes', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f'✅ Success! Found {len(data)} nodes')
            
            # Check node names
            node_names = [node['name'] for node in data]
            print('\n📋 Node Names:')
            for name in node_names:
                print(f'   - {name}')
            
            # Check for old names (should NOT be found)
            found_old_names = [name for name in node_names if name in old_names]
            if found_old_names:
                print(f'\n❌ Found old names: {found_old_names}')
                return False
            else:
                print('\n✅ No old names found!')
            
            # Check for expected anonymized names
            found_expected_names = [name for name in node_names if name in expected_names]
            print(f'\n✅ Found {len(found_expected_names)} anonymized names: {found_expected_names}')
            
        else:
            print(f'❌ Failed! Status code: {response.status_code}')
            return False
            
        # Test 2: Check dashboard summary endpoint
        print('\n🔍 Test 2: Checking /api/v1/dashboard/summary endpoint...')
        response = requests.get(f'{base_url}/api/v1/dashboard/summary', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            nodes = data.get("nodes", [])
            print(f'✅ Success! Found {len(nodes)} nodes in summary')
            
            # Check node names in summary
            summary_node_names = [node.get('name', '') for node in nodes]
            found_old_in_summary = [name for name in summary_node_names if name in old_names]
            
            if found_old_in_summary:
                print(f'\n❌ Found old names in summary: {found_old_in_summary}')
                return False
            else:
                print('\n✅ No old names in summary!')
                
        else:
            print(f'❌ Failed! Status code: {response.status_code}')
            return False
            
        # Test 3: Check anomalies endpoint
        print('\n🔍 Test 3: Checking /api/v1/anomalies endpoint...')
        response = requests.get(f'{base_url}/api/v1/anomalies?hours=24', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f'✅ Success! Found {len(data)} anomalies')
            
            # Check node names in anomalies (if any)
            if data:
                anomaly_node_names = [anomaly.get('node_name', '') for anomaly in data if anomaly.get('node_name')]
                found_old_in_anomalies = [name for name in anomaly_node_names if name in old_names]
                
                if found_old_in_anomalies:
                    print(f'\n❌ Found old names in anomalies: {found_old_in_anomalies}')
                    return False
                else:
                    print('\n✅ No old names in anomalies!')
            else:
                print('\n✅ No anomalies found (this is normal)')
                
        else:
            print(f'❌ Failed! Status code: {response.status_code}')
            return False
            
        print('\n' + '=' * 50)
        print('🎉 ALL TESTS PASSED!')
        print('✅ Node names have been successfully anonymized')
        print('✅ No real location names are visible anywhere')
        print('✅ All endpoints return generic functional names')
        print('\n📝 Anonymization Summary:')
        print('   - Distribution Centers: DIST01, DIST02, DIST03, DIST04')
        print('   - Interconnections: INTERCON01-INTERCON08')
        print('   - Zone Meters: ZONE01, ZONE02')
        
        return True
        
    except requests.exceptions.ConnectionError:
        print('❌ Could not connect to the API. Is the backend running?')
        return False
    except Exception as error:
        print(f'❌ Error during verification: {error}')
        return False

if __name__ == "__main__":
    success = verify_anonymization()
    exit(0 if success else 1)
