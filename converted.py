import pandas as pd

# Load CSV file into a DataFrame
df = pd.read_csv('applied.csv')

# Save DataFrame to an Excel file
df.to_excel('applied.xlsx', index=False)