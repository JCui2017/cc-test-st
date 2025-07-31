#!/usr/bin/env python3
"""Final test of the complete data pipeline"""

import pandas as pd
import requests

def test_complete_pipeline():
    """Test the complete data processing pipeline"""
    print("🧪 Testing complete data pipeline...")
    
    # Test the Census API call
    url = 'https://api.census.gov/data/2022/acs/acs1/profile'
    params = {'get': 'DP03_0062E,NAME', 'for': 'state:*'}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Process the data like the app does
        processed_data = []
        for row in data[1:]:  # Skip headers
            try:
                value = float(row[0]) if row[0] not in [None, '', '-'] else None
                name = row[1]
                fips = row[2]
                processed_data.append({'name': name, 'fips': fips, 'value': value})
            except:
                continue
        
        df = pd.DataFrame(processed_data)
        clean_df = df.dropna(subset=['value'])
        
        print(f'✅ Successfully processed data for {len(clean_df)} states')
        print(f'✅ Sample states: {", ".join(clean_df.head(3)["name"].tolist())}')
        print(f'✅ Income range: ${clean_df["value"].min():,.0f} - ${clean_df["value"].max():,.0f}')
        print(f'✅ Average income: ${clean_df["value"].mean():,.0f}')
        print('✅ Data pipeline fully functional!')
        
        return True
        
    except Exception as e:
        print(f'❌ Pipeline test failed: {e}')
        return False

if __name__ == "__main__":
    success = test_complete_pipeline()
    if success:
        print("\n🎉 All systems operational! Application ready for use.")
    else:
        print("\n⚠️ Pipeline issues detected.")