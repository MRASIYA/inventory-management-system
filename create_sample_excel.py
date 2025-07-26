import pandas as pd
from datetime import datetime

# Create sample data for ISSUES.xlsx
data = {
    'Material Name': ['Steel Bars', 'Cement Bags', 'Paint Cans', 'Wire Rolls'],
    'Date': [datetime.now().strftime('%Y-%m-%d')] * 4,
    'Issued': [50, 20, 15, 10],
    'Received': [100, 50, 30, 25],
    'Return': [5, 2, 1, 0],
    'Balance': [55, 32, 16, 15]  # Received + Return - Issued
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel file
df.to_excel('ISSUES.xlsx', sheet_name='Sheet1', index=False)

print("ISSUES.xlsx created successfully!")
print("\nFile structure:")
print(df.to_string(index=False))
