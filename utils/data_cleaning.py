import pandas as pd

def clean_data(entries, field):
    """Extracts and cleans data for the given field from API response."""
    field_data = []
    
    for entry in entries:
        if 'fieldData' in entry:
            for field_entry in entry['fieldData']:
                if field_entry.get('name') == field:
                    field_data.append({
                        'timestamp': entry.get('timestamp'),
                        'value': float(field_entry.get('value', 0))
                    })

    if not field_data:
        raise ValueError("No data found for the field: {}".format(field))

    df = pd.DataFrame(field_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df.fillna(method='ffill', inplace=True)  # Forward-fill missing values

    return df

def clean_data2(entries, field):
    """Extracts and cleans data for the given field from API response."""
    field_data = []
    
    for entry in entries:
        if 'fieldData' in entry:
            for field_entry in entry['fieldData']:
                if field_entry.get('name') == field:
                    field_data.append({
                        'timestamp': entry.get('timestamp', 'N/A'),  # Handle missing timestamp
                        'value': float(field_entry.get('value', 0))
                    })

    if not field_data:
        return None

    df = pd.DataFrame(field_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S').fillna('N/A')
    return df