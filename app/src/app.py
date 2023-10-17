import requests
import json
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import matplotlib.pyplot as plt
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

custom_tiffany_scale = ['#E0F2F1', '#B2DFDB', '#80CBC4', '#4DB6AC', '#26A69A', '#009688', '#00897B', '#00796B', '#00695C', '#004D40']
custom_red_scale = ['lightcoral', 'darkred']

tiffany_cmap = LinearSegmentedColormap.from_list('custom_tiffany_scale', custom_tiffany_scale)
red_cmap = LinearSegmentedColormap.from_list('custom_red_scale', custom_red_scale)

a = np.array([[0,1]])

plt.figure(figsize=(9, 1))
img = plt.imshow(a, cmap=tiffany_cmap)
plt.gca().set_visible(False)
cax = plt.axes([0.1, 0.2, 0.8, 0.6])
plt.colorbar(orientation="horizontal", cax=cax)
plt.figure(figsize=(9, 1))
img = plt.imshow(a, cmap=red_cmap)
plt.gca().set_visible(False)
cax = plt.axes([0.1, 0.2, 0.8, 0.6])
plt.colorbar(orientation="horizontal", cax=cax)
plt.show()

columns = [
    'state', 'incidentType'
]
df_summary = pd.DataFrame(columns=columns)

base_url = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"

skip = 0
top = 1000
while True:
    url = f"{base_url}?$skip={skip}&$top={top}"
    response = requests.get(url)
    data = json.loads(response.text)

    if not data['DisasterDeclarationsSummaries']:
        break

    temp_df = pd.DataFrame(data['DisasterDeclarationsSummaries'])
    temp_df = temp_df[columns]
    df_summary = pd.concat([df_summary, temp_df], ignore_index=True)

    skip += top

df_summary.head(5)

df_summary.incidentType.sample

columns = [
    'id', 'reportingPeriod', 'state', 'legalAgencyName', 'projectType',
    'projectStartDate', 'projectEndDate', 'nameOfProgram', 'fundingAmount'
]
df = pd.DataFrame(columns=columns)

base_url = "https://www.fema.gov/api/open/v2/EmergencyManagementPerformanceGrants"

skip = 0
top = 1000
while True:
    url = f"{base_url}?$skip={skip}&$top={top}"
    response = requests.get(url)
    data = json.loads(response.text)

    if not data['EmergencyManagementPerformanceGrants']:
        break

    temp_df = pd.DataFrame(data['EmergencyManagementPerformanceGrants'])
    df = pd.concat([df, temp_df], ignore_index=True)

    skip += top

df.head()
incident_counts = df_summary['incidentType'].value_counts()

fig = px.pie(
    names=incident_counts.index,
    values=incident_counts.values,
    title='Distribution of Disaster Types in the USA',
    color_discrete_sequence=px.colors.sequential.Plasma,
    hole=0.3,
    template='plotly_white'
)

fig.update_layout(
    width=1000,
    height=800,
    title=dict(
        text='Distribution of Disaster Types in the USA',
        x=0.5,
        y=0.95,
        font=dict(color='#333333', size=20)
    ),
    font=dict(family='monospace'),
    legend=dict(
        x=1,
        y=0.96,
        bordercolor='#444444',
        borderwidth=0,
        tracegroupgap=5
    )
)

fig.show()

grouped_df = df.groupby('state').agg(
    total_funding=pd.NamedAgg(column='fundingAmount', aggfunc='sum'),
    total_programs=pd.NamedAgg(column='nameOfProgram', aggfunc='count')
).reset_index()

grouped_df['total_funding'] = pd.to_numeric(grouped_df['total_funding'], errors='coerce')
grouped_df.head()
grouped_df.dtypes
grouped_df.isnull().sum()

state_abbrev_dict = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands': 'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

grouped_df['state_abbrev'] = grouped_df['state'].map(state_abbrev_dict)

df_summary.rename(columns={'state': 'state_abbrev'}, inplace=True)
disaster_count = df_summary.groupby('state_abbrev')['incidentType'].count().reset_index()
disaster_count.columns = ['state_abbrev', 'total_disasters']
grouped_df = pd.merge(grouped_df, disaster_count, on='state_abbrev', how='left')


disaster_color_map = {
    'Fire': 'red',
    'Flood': 'blue',
    'Hurricane': 'purple',
    'Tropical Storm': 'cyan',
    'Severe Storm': 'grey',
    'Winter Storm': 'white',
    'Tornado': 'green',
    'Snowstorm': 'lightblue',
    'Earthquake': 'brown',
    'Biological': 'pink',
    'Mud/Landslide': 'darkgreen',
    'Coastal Storm': 'darkblue',
    'Other': 'black',
    'Severe Ice Storm': 'lightgrey',
    'Dam/Levee Break': 'orange',
    'Typhoon': 'darkcyan',
    'Volcanic Eruption': 'darkred',
    'Freezing': 'lightcyan',
    'Toxic Substances': 'yellow',
    'Chemical': 'lightgreen',
    'Terrorist': 'magenta',
    'Drought': 'beige',
    'Human Cause': 'tan',
    'Fishing Losses': 'navy',
    'Tsunami': 'teal'
}

app = dash.Dash(__name__, title = "Disaster-Funding Dash App")

# Declare server for Heroku deployment. Needed for Procfile.
server = app.server

app.layout = html.Div([
    dcc.Dropdown(
        id='indicator-dropdown',
        options=[
            {'label': 'Total Funding', 'value': 'total_funding'},
            {'label': 'Total Disasters', 'value': 'total_disasters'}
        ],
        value='total_disasters'
    ),
    dcc.Graph(id='choropleth-map'),
    dcc.Graph(id='pie-chart', style={'display': 'none'})
])


@app.callback(
    [Output('choropleth-map', 'figure'),
     Output('pie-chart', 'figure'),
     Output('pie-chart', 'style')],
    [Input('choropleth-map', 'clickData'),
     Input('indicator-dropdown', 'value')]
)

def update_graph(clickData, selected_indicator):
    color_scale = custom_tiffany_scale if selected_indicator == 'total_funding' else custom_red_scale

    fig_map = px.choropleth(
        grouped_df,
        locations='state_abbrev',
        color=selected_indicator,
        locationmode='USA-states',
        scope='usa',
        color_continuous_scale=color_scale
    )

    fig_pie = px.pie()
    pie_style = {'display': 'none'}

    if clickData and 'points' in clickData and len(clickData['points']) > 0:
        state_abbrev = clickData['points'][0].get('location', None)
        if state_abbrev:
            state_name = state_abbrev
            
            if selected_indicator == 'total_disasters':
                pie_data = df_summary[df_summary['state_abbrev'] == state_name]['incidentType'].value_counts()
                fig_pie = px.pie(pie_data, names=pie_data.index, values=pie_data.values, 
                                 color=pie_data.index, color_discrete_map=disaster_color_map)  
                pie_style = {'display': 'block'}

            total_value = grouped_df[grouped_df['state_abbrev'] == state_abbrev][selected_indicator].values[0]
            fig_map.update_layout(
                title=f"{selected_indicator} by State (Selected: {state_name}, {selected_indicator}: {total_value})"
            )

    return fig_map, fig_pie, pie_style



if __name__ == '__main__':
    app.run_server(debug=True)














