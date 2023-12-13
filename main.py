import re

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import requests
import pandas as pd

from functions import parse_date_range, normalize_year

matplotlib.use('Agg')

pd.set_option('display.min_rows', 600)
pd.set_option('display.max_rows', 900)
pd.set_option('display.max_columns', 13)
pd.set_option('display.width', 2000)


columns_to_keep = ['Object Number', 'Title', 'Object Date',
                   'Culture', 'Medium']

met_data = pd.read_csv("meta_data/met.csv")

medieval_art = met_data[met_data['Department'] == 'Medieval Art'].copy()
medieval_art['Object Begin Date'] = pd.to_numeric(medieval_art['Object Begin Date'], errors='coerce')
medieval_art = medieval_art[columns_to_keep]
art_data = medieval_art.copy()

print(art_data)

art_data = art_data[art_data["Object Date"].notna()]

# Parse dates
parsed_ranges = [parse_date_range(dr) for dr in art_data["Object Date"].astype(str)]
starts, ends = zip(*parsed_ranges)

art_data['Start Year'], art_data['End Year'] = zip(*parsed_ranges)

# Normalize years
art_data['Start Year'] = art_data['Start Year'].apply(lambda x: normalize_year(x, index=0))
art_data['End Year'] = art_data['End Year'].apply(lambda x: normalize_year(x, index=1))


# ----------------------------------------- Filtering -----------------------------------------
# df = art_data

df = art_data[(art_data['Start Year'] >= 300) & (art_data['Start Year'] <= 1700)]
df = df[(df['End Year'] >= 300) & (df['End Year'] <= 1700)]


start_years = df['Start Year']
end_years = df['End Year']
mediums = df['Medium']
cultures = df['Culture']


# ----------------------------------------- Graphing -----------------------------------------
# Canvas with four subplots
fig, ((ax3, ax4), (ax1, ax2)) = plt.subplots(2, 2, figsize=(12, 15))

# Plot the Start Year histogram
ax1.hist(start_years, bins=20, edgecolor='k')
ax1.set_title('Distribution of Start Years')
ax1.set_xlabel('Start Year')
ax1.set_ylabel('Frequency')
ax1.grid(axis='y', alpha=0.75)

# Plot the End Year histogram
ax2.hist(end_years, bins=20, edgecolor='k', color='orange')  # Adjust the number of bins as needed
ax2.set_title('Distribution of End Years')
ax2.set_xlabel('End Year')
ax2.set_ylabel('Frequency')
ax2.grid(axis='y', alpha=0.75)

# Plot the Medium bar chart
medium_counts = mediums.value_counts().head(10)  # Adjust the number of categories to display
medium_counts.plot(kind='bar', ax=ax3)
ax3.set_title('Top 10 Mediums')
ax3.set_xlabel('Medium')
ax3.set_ylabel('Count')
ax3.grid(axis='y', alpha=0.75)

# Plot the Culture bar chart
culture_counts = cultures.value_counts().head(10)  # Adjust the number of categories to display
culture_counts.plot(kind='bar', ax=ax4)
ax4.set_title('Top 10 Cultures')
ax4.set_xlabel('Culture')
ax4.set_ylabel('Count')
ax4.grid(axis='y', alpha=0.75)

plt.subplots_adjust(hspace=0.9)

# Save the plot to a file
plt.savefig('graphs/years_medium_culture_visualization_300_1700.png')


# ----------------------------------------- Analysis -----------------------------------------
# print(art_data[["Object Date", "Start Year", "End Year"]])
print(art_data.head(5))

# Print the first 5 rows
print("First 5 rows of art_data:")
print(art_data.head(5))

# Print the columns "Object Date", "Start Year", and "End Year"
print("Columns 'Object Date', 'Start Year', 'End Year' of art_data:")
print(art_data[["Object Date", "Start Year", "End Year"]])

# Print the unique values in the "Medium" column
print("Unique values in the 'Medium' column:")
print(art_data["Medium"].unique())

# Print the unique values in the "Culture" column
print("Unique values in the 'Culture' column:")
unique_culture_values = art_data["Culture"].unique()
print(unique_culture_values)
print(f"\n{len(unique_culture_values)} different cultures with medieval art at the Met.\n\n")

# Top 10 most frequent cultures
culture_counts = art_data['Culture'].value_counts().head(10)
print("Top 10 most frequent cultures:")
print(culture_counts)

# Top 10 most frequent mediums
medium_counts = art_data['Medium'].value_counts().head(10)
print("\nTop 10 most frequent mediums:")
print(medium_counts)
