# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Get unique values from the 'launch_site' column
unique_sites = spacex_df['Launch Site'].unique()

# Create a list of dictionaries for each unique site
sites_list = [{'label': 'All Sites', 'value': 'ALL'}]+[{'label': site, 'value': site} for site in unique_sites]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=sites_list,
                                             value='ALL',
                                             placeholder = 'Select a Launch Site here',
                                             searchable = True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    #marks={0: '0Kg', 1000: '1000Kg', 2000: '2000Kg', 3000: '3000Kg', 10000: '10000Kg'},
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # For 'All Sites', aggregate success counts for each site
        aggregated_data = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        aggregated_data.columns = ['Launch Site', 'Success Count']
        fig = px.pie(aggregated_data, values='Success Count', names='Launch Site',
                     title='Total Successes for Each Launch Site')
        return fig
    else:
        # return the outcomes pie chart for a selected site
        selected_site_df = spacex_df[spacex_df['Launch Site'] == entered_site]

        # Calculate success and failure counts for the selected site
        success_counts = selected_site_df[selected_site_df['class'] == 1]['class'].count()
        failure_counts = selected_site_df[selected_site_df['class'] == 0]['class'].count()

        # Create a pie chart for success and failure counts of the selected site
        fig = px.pie(values=[success_counts, failure_counts],
                     names=['Successful Launches', 'Failed Launches'],
                     title=f'Success vs Failed Launches for {entered_site}')
        return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
    Input(component_id="payload-slider", component_property="value")]
)
def update_scatter_chart(entered_site, payload_range):
    if entered_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                         title='Payload vs. Outcome for All Sites')
    else:
        selected_site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        filtered_df = selected_site_df[(selected_site_df['Payload Mass (kg)'] >= payload_range[0]) & 
                                       (selected_site_df['Payload Mass (kg)'] <= payload_range[1])]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                         title=f'Payload vs. Outcome for {entered_site}')
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
