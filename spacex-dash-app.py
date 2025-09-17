# Import required libraries
import pandas as pd
import numpy as np
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites = spacex_df['Launch Site'].unique()

site_dropdown_options = [{'label':site,'value':site} for site in launch_sites]

counts = spacex_df.groupby('Launch Site')['class'].value_counts().reset_index()

counts['result'] = np.where(counts['class'] == 0, 'Failed', 'Successful')
counts['hover'] = counts.apply(lambda x: f'{x['Launch Site']}\n {x['count']} {x['result']} Launches',axis=1)

# successful_launches = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
# all_launches = spacex_df.groupby('Launch Site')['class'].sum().reset_index()



# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                                options=([
                                                    {'label': 'All Sites', 'value': 'ALL'},
                                                ]+site_dropdown_options),
                                                value='ALL',
                                                placeholder="place holder here",
                                                searchable=True
                                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site

                                html.Div(dcc.Graph(
                                    id='success-pie-chart',
                                )),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=min_payload,
                                    max=max_payload,
                                    value=[min_payload,max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
)

def update_pie_chart(selected_site):
    print(selected_site)
    if selected_site == 'ALL':
        df = counts[counts['class']==1]

        # hover = 
        fig = px.pie(data_frame=df,names='Launch Site', values='count', title='Successful Launches by Launch Site', hover_name='hover')
        fig.update_layout(title_x=0.5)
        return fig
    else:
        df = counts[counts['Launch Site']==selected_site]

        fig = px.pie(data_frame=df,names='result', values='count',title=f'{selected_site} Total Launches',hover_name='hover')
        fig.update_layout(title_x=0.5)
        return fig
        

    # return px.pie(data_frame=)

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart',component_property='figure'),
    [Input(component_id='site-dropdown',component_property='value'),Input(component_id='payload-slider',component_property='value')]
)

def update_scatter(selected_site, payload_range):
    df = spacex_df.copy()
    # print(df)
    min, max = payload_range
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]
    if min != min_payload or max != max_payload:
        df = df[(df['Payload Mass (kg)'] >=min) & (df['Payload Mass (kg)'] <= max )]
        # df = df[(min <= df['Payload Mass (kg)'] <= max )]
    return px.scatter(data_frame=df, x='Payload Mass (kg)', y='class', color='Booster Version Category', title=f'Correlation between Payload and Success for {'All Sites' if selected_site == 'ALL' else selected_site}')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
