import re
import matplotlib.dates as mdates
import matplotlib
import numpy as np

matplotlib.use('Agg')
import seaborn as sns
import matplotlib.pyplot as plt

from datetime import datetime

import requests
from pprint import pprint
import plotly.express as px
import pandas as pd

import plotly.graph_objs as go


pd.set_option('display.min_rows', 100)
pd.set_option('display.max_rows', 150)
pd.set_option('display.max_columns', 13)
pd.set_option('display.width', 2000)


def fetch_artworks():
    url = "https://collectionapi.metmuseum.org/public/collection/v1/objects"
    params = {"departmentIds": [17]}  # ID for the Medieval Art department
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["objectIDs"]
    else:
        return None


def fetch_artwork_details(object_id):
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "objectID": object_id,
            "title": data.get("title"),
            "artist": data.get("artistDisplayName"),
            "year": data.get("objectDate"),
            "region": data.get("artistDisplayBio"),
        }
    else:
        return None


def visualize_data(artworks):
    fig = px.scatter(artworks, x="year", y="region", hover_data=["title", "artist"])
    fig.update_layout(title="Medieval Artworks at The Met by Year and Region")
    fig.show()


def extract_year(date_str):
    if pd.isna(date_str):
        return None
    # Handling 'mid-', 'early ', or 'late ' prefixes
    if 'mid-' in date_str:
        century = int(re.search(r'\d+', date_str).group())
        return (century - 1) * 100 + 50  # Approximating 'mid-' as the middle of the century
    elif 'early ' in date_str:
        century = int(re.search(r'\d+', date_str).group())
        return (century - 1) * 100  # Approximating 'early' as the start of the century
    elif 'late ' in date_str:
        century = int(re.search(r'\d+', date_str).group())
        return (century - 1) * 100 + 75  # Approximating 'late' as the last quarter of the century

    elif 'century' in date_str:
        if "first" in date_str:
            century = int(re.search(r'\d+', date_str).group())
            return (century - 1) * 100  # First half of the century
        elif "second" in date_str:
            century = int(re.search(r'\d+', date_str).group())
            return (century - 1) * 100 + 50  # Second half of the century
        else:
            century = int(re.search(r'\d+', date_str).group())
            return (century - 1) * 100

    # Handling date ranges
    elif '�' in date_str or '-' in date_str:
        return int(re.search(r'\d{4}', date_str).group())

    # Handling direct year values
    else:
        try:
            return int(re.search(r'\d{4}', date_str).group())
        except:
            return None


# medieval_art['year'] = medieval_art['Object Date'].apply(extract_year)

# import plotly.express as px
#
# # Assuming df has 'start_year' and 'end_year' columns
# fig = px.timeline(df, x_start="start_year", x_end="end_year", y="Culture", color="Culture")
# fig.update_layout(title="Date Ranges of Medieval Artworks at The Met by Culture")
# fig.show()


# art_df['Object Date'] = art_df['Object Date'].str.replace('�', '-')

# filtered_art = art_df[art_df["year"] < 2000]
# grouped_data = filtered_art.groupby(['year', 'Culture']).size().reset_index(name='counts')
# # Creating the scatter plot
# fig = px.scatter(grouped_data, x='year', y='counts', color='Culture',
#                  title='Medieval Artworks at The Met by Year and Culture')
# fig.show()

def contains_integer(input_string):
    integer_pattern = r'\d+'
    match = re.search(integer_pattern, input_string)
    return match is not None


columns_to_keep = ['Object Number', 'Title', 'Object Date',
                   'Culture', 'Medium']

met_data = pd.read_csv("openaccess/met.csv")

medieval_art = met_data[met_data['Department'] == 'Medieval Art'].copy()
medieval_art['Object Begin Date'] = pd.to_numeric(medieval_art['Object Begin Date'], errors='coerce')
medieval_art = medieval_art[columns_to_keep]
art_df = medieval_art.copy()

print(art_df)
print(art_df["Object Date"])
# print(art_df["Object Date"].to_string(index=False))


# Function to convert century text to year
def century_to_year(century_str, part_of_century='', is_bce=False):
    try:
        century = int(''.join(filter(str.isdigit, century_str)))
    except ValueError:
        raise ValueError(f"Cannot extract century from '{century_str}'")

    year_start = (century - 1) * 100
    year_end = century * 100

    if is_bce:
        year_start, year_end = -year_end, -year_start

    # Adjust for early, mid, and late
    if part_of_century == 'early':
        return year_start, year_start + 33
    elif part_of_century == 'mid':
        return year_start + 34, year_start + 66
    elif part_of_century == 'late':
        return year_start + 67, year_end
    else:
        return year_start, year_end


# Function to parse a date range string
def parse_date_range(date_range):
    # Normalize the string (remove 'ca.', 'or later', 'or modern', etc.)
    normalized_range = date_range.lower().split(' or ')[0]
    if not contains_integer(normalized_range):
        normalized_range = date_range.lower().split(' or ')[1]

    parts = normalized_range.replace('ca. ', '').replace('s', '').split('–')
    start_part, end_part = (parts + parts)[:2]  # Handles single entry cases

    is_bce = 'bce' in start_part or 'bce' in end_part
    part_of_century_start = 'early' if 'early' in start_part else 'mid' if 'mid' in start_part else 'late' if 'late' in start_part else ''
    part_of_century_end = 'early' if 'early' in end_part else 'mid' if 'mid' in end_part else 'late' if 'late' in end_part else ''

    # Logic for 'mid' or 'third quarter'
    def interpret_complex_phrase(part):
        if 'mid' in part:
            return 'mid'
        if 'third quarter' in part:
            return 'third quarter'
        return ''

    complex_phrase_start = interpret_complex_phrase(start_part)
    complex_phrase_end = interpret_complex_phrase(end_part)

    # Extract numeric part from century strings, if available
    start_century = ''.join(filter(str.isdigit, start_part))
    end_century = ''.join(filter(str.isdigit, end_part))

    try:
        if complex_phrase_start or complex_phrase_end:
            # Handle complex phrases
            century = int(start_century or end_century)
            if complex_phrase_start == 'mid':
                start = (century - 1) * 100 + 34
            elif complex_phrase_start == 'third quarter':
                start = (century - 1) * 100 + 50
            else:
                start = (century - 1) * 100

            if complex_phrase_end == 'mid':
                end = (century - 1) * 100 + 66
            elif complex_phrase_end == 'third quarter':
                end = (century - 1) * 100 + 75
            else:
                end = century * 100
        else:
            # Handle normal cases
            start = century_to_year(start_century, part_of_century_start, is_bce)
            end = century_to_year(end_century, part_of_century_end, is_bce)
    except ValueError as e:
        raise ValueError(f"{e}, \ndate_range: {date_range}, start_century: {start_century}, end_century: {end_century}")

    try:
        return start, end
    except:
        pass


date_ranges_example = ["580–640", "11th–12th century or modern", "4th–7th century", "1534–49"]

art_df = art_df[art_df["Object Date"].notna()]
parsed_ranges = [parse_date_range(dr) for dr in art_df["Object Date"].astype(str)]

starts, ends = zip(*parsed_ranges)
events = ["Event {}".format(i+1) for i in range(len(parsed_ranges))]

art_df['Start Year'], art_df['End Year'] = zip(*parsed_ranges)

# plt.figure(figsize=(10, 8))
# for i, (start, end) in enumerate(parsed_ranges):
#     plt.plot([start, end], [i, i], color='tab:blue', marker='|', markersize=10)
#
# # Improve the formatting
# plt.yticks(range(len(events)), events)
# plt.xlabel("Year")
# plt.title("Timeline of Date Ranges")
# plt.grid(True)
#
# # Show the plot
# plt.show()


# parsed_ranges = [
#     (1820, 1840),
#     (1830, 1900),
#     (2018, 2023)
# ]
#
# events = [
#     "Event A",
#     "Event B",
#     "Event C"
# ]


# # Create a figure using Plotly Express
# fig = go.Figure()
#
# for i, (start, end) in enumerate(parsed_ranges):
#     fig.add_trace(go.Scatter(
#         x=[start, end],
#         y=[i, i],
#         mode='lines+markers',
#         name=f'Event {i+1}',
#         marker=dict(color='blue', size=10),
#         line=dict(width=4)
#     ))
#
# # Update layout
# fig.update_layout(
#     title='Timeline of Date Ranges',
#     xaxis_title='Year',
#     yaxis_title='Events',
#     yaxis=dict(
#         tickmode='array',
#         tickvals=list(range(len(events))),
#         ticktext=events
#     ),
#     showlegend=False
# )
#
# # Show the figure
# fig.show()


def normalize_year(year):
    if isinstance(year, tuple):
        return year[0]  # Assuming the first element of the tuple is the start year
    return year


# Normalize years
art_df['Start Year'] = art_df['Start Year'].apply(normalize_year)
art_df['End Year'] = art_df['End Year'].apply(normalize_year)

# Prepare heatmap data
year_min, year_max = art_df['Start Year'].min(), art_df['End Year'].max()
heatmap_data = np.zeros(year_max - year_min + 1)


new_df = art_df.head(50)

filtered_df = art_df[(art_df['Start Year'] >= 200) & (art_df['Start Year'] <= 2000)]
filtered_df = filtered_df[(filtered_df['End Year'] >= 200) & (filtered_df['End Year'] <= 2000)]


for _, row in new_df.iterrows():
    start, end = int(row['Start Year']), int(row['End Year'])
    for year in range(start, end + 1):
        heatmap_data[year - year_min] += 1

# Create heatmap
fig = go.Figure(data=go.Heatmap(
    z=[heatmap_data],
    x=list(range(year_min, year_max + 1)),
    y=['Art Objects'],
    colorscale='Viridis'
))

# Update layout
fig.update_layout(
    title='Density of Art Objects Over Time',
    xaxis_title='Year',
    yaxis_title='Object Count',
)

fig.show()


