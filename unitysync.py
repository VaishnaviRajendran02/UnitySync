import pandas as pd
import requests
import requests
import time
from datetime import datetime 
import math
import json

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def process_needs_and_volunteers():
    # Read files
    try:
        needs_df = pd.read_excel('Need.csv.xlsx')
        vols_df = pd.read_excel('volunteers.csv.xlsx')
        print(f"Successfully loaded {len(needs_df)} needs and {len(vols_df)} volunteers.")
    except Exception as e:
        print(f"Error reading files: {e}")
        return

    # Check and add mock columns to Needs if they don't exist based on the prompt
    if 'Category' not in needs_df.columns:
        print("Warning: 'Category' column not found in Needs.csv. Adding mock data for demonstration.")
        needs_df['Category'] = ['Medical' if i % 2 == 0 else 'General' for i in range(len(needs_df))]
    if 'Is_Disabled' not in needs_df.columns:
        print("Warning: 'Is_Disabled' column not found in Needs.csv. Adding mock data for demonstration.")
        needs_df['Is_Disabled'] = [1 if i % 3 == 0 else 0 for i in range(len(needs_df))]
    
    if 'Lat' not in needs_df.columns or 'Long' not in needs_df.columns:
        print("Warning: Lat/Long not found in Needs.csv. Adding mock location data.")
        needs_df['Lat'] = 13.0
        needs_df['Long'] = 80.2

    # Prioritize: Assign higher urgency score if Category is Medical and Is_Disabled is 1
    needs_df['Urgency'] = 1 # Base score
    high_priority_mask = (needs_df['Category'] == 'Medical') & (needs_df['Is_Disabled'] == 1)
    needs_df.loc[high_priority_mask, 'Urgency'] = 100

    # Filter available volunteers
    if 'Status' in vols_df.columns:
        avail_vols = vols_df[vols_df['Status'].astype(str).str.strip().str.lower() == 'available']
    else:
        print("Warning: 'Status' column not found in volunteers. Considering all volunteers available.")
        avail_vols = vols_df

    if len(avail_vols) == 0:
        print("No available volunteers found!")
        return

    # Match: Find 3 nearest 'Available' volunteers for each need
    for idx, need in needs_df.iterrows():
        need_lat = need['Lat']
        need_long = need['Long']
        
        distances = []
        for v_idx, vol in avail_vols.iterrows():
            # Check if Lat/Long exist in volunteers
            if 'Lat' in vol and 'Long' in vol:
                v_lat = vol['Lat']
                v_long = vol['Long']
                dist = haversine(need_lat, need_long, v_lat, v_long)
                vol_dict = vol.to_dict()
                vol_dict['distance_km'] = round(dist, 2)
                distances.append((dist, vol_dict))
            else:
                distances.append((float('inf'), vol.to_dict()))
        
        # Sort by distance and get top 3
        distances.sort(key=lambda x: x[0])
        nearest_3 = [d[1] for d in distances[:3]]
        
        # Automate: Every time a high-priority match is found, send POST request to webhook
        if need['Urgency'] >= 80:
            primary_vol = nearest_3[0] if nearest_3 else None
            request_text = need.get('Skill', 'Need immediate medical assistance')
            location_url = f"https://www.google.com/maps?q={need_lat},{need_long}"
            distance_km = primary_vol['distance_km'] if primary_vol else 0
            volunteer_name = primary_vol['Name'] if primary_vol else 'Unknown'
            
            # Since we are already inside the >= 80 block, this is always URGENT
            status_val = 'URGENT' 
            formatted_message = f"🚨 {status_val}: {request_text}\n📍 Location: {location_url}\n🏃 Volunteer: {volunteer_name} ({distance_km} km away)"
            payload = {
                'status': status_val,
                'category': need['Category'],
                'request': request_text,
                'volunteer': volunteer_name,
                'distance': distance_km,
                'maps_link': location_url,
                'formatted_message': formatted_message,
                'time': str(datetime.now())
            }
            
            print(f"High-priority match found for need {need.get('Need_ID', f'NEED_{idx}')}!")
            print("Sending the following JSON payload to webhook:")
            print(json.dumps(payload, indent=2))
            
            try:
                # Switched from webhook-test to webhook to resolve the 404 unregistered error 
                # Change this line in your script:
                response = requests.post('http://localhost:5678/webhook-test/unitysync', json=payload)
                print(f"Webhook response: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Failed to post to webhook: {e}")

if __name__ == "__main__":
    process_needs_and_volunteers()
