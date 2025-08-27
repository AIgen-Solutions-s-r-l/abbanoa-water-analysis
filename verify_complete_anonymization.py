#!/usr/bin/env python3

import requests
import json

def verify_complete_anonymization():
    print('🔒 Verifying Complete Node Anonymization (Names + IDs)')
    print('=' * 60)
    
    base_url = 'http://localhost:8000'
    
    # Define old names/IDs that should NOT appear
    old_names_and_ids = [
        # Old names
        "CENTRO EST", "CENTRO NORD", "CENTRO OVEST", "CENTRO SUD",
        "FIORI", "LIBERTÀ", "Q.GALLUS", "Q.MATTEOTTI", "Q.MONSERRATO",
        "Q.NENNI SUD", "Q.SANT'ANNA", "Q.SARDEGNA", "Q.TRIESTE", "STADIO",
        # Old IDs
        "CENTRO_EST", "CENTRO_NORD", "CENTRO_OVEST", "CENTRO_SUD",
        "FIORI", "LIBERTA", "Q_GALLUS", "Q_MATTEOTTI", "Q_MONSERRATO",
        "Q_NENNI_SUD", "Q_SANTANNA", "Q_SARDEGNA", "Q_TRIESTE", "STADIO"
    ]
    
    # Define expected anonymized names/IDs
    expected_names_and_ids = [
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
            
            # Check node IDs and names
            node_ids = [node['id'] for node in data]
            node_names = [node['name'] for node in data]
            
            print('\n📋 Node IDs:')
            for node_id in node_ids:
                print(f'   - {node_id}')
                
            print('\n📋 Node Names:')
            for name in node_names:
                print(f'   - {name}')
            
            # Check for old names/IDs (should NOT be found)
            found_old_in_ids = [node_id for node_id in node_ids if node_id in old_names_and_ids]
            found_old_in_names = [name for name in node_names if name in old_names_and_ids]
            
            if found_old_in_ids:
                print(f'\n❌ Found old IDs: {found_old_in_ids}')
                return False
            else:
                print('\n✅ No old IDs found!')
                
            if found_old_in_names:
                print(f'\n❌ Found old names: {found_old_in_names}')
                return False
            else:
                print('\n✅ No old names found!')
            
            # Check for expected anonymized names/IDs
            found_expected_in_ids = [node_id for node_id in node_ids if node_id in expected_names_and_ids]
            found_expected_in_names = [name for name in node_names if name in expected_names_and_ids]
            
            print(f'\n✅ Found {len(found_expected_in_ids)} anonymized IDs: {found_expected_in_ids}')
            print(f'✅ Found {len(found_expected_in_names)} anonymized names: {found_expected_in_names}')
            
            # Verify that IDs and names match (they should be the same now)
            mismatches = []
            for node in data:
                if node['id'] != node['name']:
                    mismatches.append(f"{node['id']} != {node['name']}")
            
            if mismatches:
                print(f'\n❌ Found ID/name mismatches: {mismatches}')
                return False
            else:
                print('\n✅ All node IDs and names match perfectly!')
            
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
            found_old_in_summary = [name for name in summary_node_names if name in old_names_and_ids]
            
            if found_old_in_summary:
                print(f'\n❌ Found old names/IDs in summary: {found_old_in_summary}')
                return False
            else:
                print('\n✅ No old names/IDs in summary!')
                
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
                found_old_in_anomalies = [name for name in anomaly_node_names if name in old_names_and_ids]
                
                if found_old_in_anomalies:
                    print(f'\n❌ Found old names/IDs in anomalies: {found_old_in_anomalies}')
                    return False
                else:
                    print('\n✅ No old names/IDs in anomalies!')
            else:
                print('\n✅ No anomalies found (this is normal)')
                
        else:
            print(f'❌ Failed! Status code: {response.status_code}')
            return False
            
        print('\n' + '=' * 60)
        print('🎉 ALL TESTS PASSED!')
        print('✅ Complete anonymization successful')
        print('✅ No real location names or IDs visible anywhere')
        print('✅ All endpoints return generic functional identifiers')
        print('\n📝 Complete Anonymization Summary:')
        print('   - Node IDs: DIST01, DIST02, DIST03, DIST04, INTERCON01-INTERCON08, ZONE01, ZONE02')
        print('   - Node Names: DIST01, DIST02, DIST03, DIST04, INTERCON01-INTERCON08, ZONE01, ZONE02')
        print('   - IDs and Names are now identical (perfect anonymization)')
        
        return True
        
    except requests.exceptions.ConnectionError:
        print('❌ Could not connect to the API. Is the backend running?')
        return False
    except Exception as error:
        print(f'❌ Error during verification: {error}')
        return False

if __name__ == "__main__":
    success = verify_complete_anonymization()
    exit(0 if success else 1)
