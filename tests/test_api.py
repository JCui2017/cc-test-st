#!/usr/bin/env python3
"""
Quick test script to verify Census API integration
"""

import requests
import json

def test_census_api():
    """Test Census API connectivity and data retrieval"""
    print("Testing Census API integration...")
    
    # Test URL and parameters (updated to match app configuration)
    url = "https://api.census.gov/data/2022/acs/acs1/profile"
    params = {
        "get": "DP03_0062E,NAME",  # Median household income from profile
        "for": "state:*"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ API connection successful!")
        print(f"✅ Retrieved data for {len(data)-1} states/territories")
        print(f"✅ Sample data: {data[1][:2]} (first state's name and income)")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_census_api()
    if success:
        print("\n🎉 Census API integration is working correctly!")
    else:
        print("\n⚠️ Census API integration needs attention.")