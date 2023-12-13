import re

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import requests
import pandas as pd

from functions import parse_date_range, normalize_year

matplotlib.use('Agg')

pd.set_option('display.min_rows', 100)
pd.set_option('display.max_rows', 150)
pd.set_option('display.max_columns', 13)
pd.set_option('display.width', 2000)


columns_to_keep = ['Object Number', 'Title', 'Object Date',
                   'Culture', 'Medium']

met_data = pd.read_csv("meta_data/met.csv")

medieval_art = met_data[met_data['Department'] == 'Medieval Art'].copy()
medieval_art['Object Begin Date'] = pd.to_numeric(medieval_art['Object Begin Date'], errors='coerce')
medieval_art = medieval_art[columns_to_keep]
art_df = medieval_art.copy()

print(art_df)
print(art_df["Object Date"])

art_df = art_df[art_df["Object Date"].notna()]

# Parse dates
parsed_ranges = [parse_date_range(dr) for dr in art_df["Object Date"].astype(str)]
starts, ends = zip(*parsed_ranges)

art_df['Start Year'], art_df['End Year'] = zip(*parsed_ranges)

# Normalize years
art_df['Start Year'] = art_df['Start Year'].apply(normalize_year)
art_df['End Year'] = art_df['End Year'].apply(normalize_year)


# ----------------------------------------- Filtering -----------------------------------------
df = art_df[(art_df['Start Year'] >= 350) & (art_df['Start Year'] <= 2000)]
df = df[(df['End Year'] >= 200) & (df['End Year'] <= 2000)]

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
plt.savefig('graphs/year_medium_culture_visualization_200CE.png')

