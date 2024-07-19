from dash import Dash
import dash_leaflet as dl
from dash import dcc
from dash import html
import plotly.express as px
from dash import dash_table
from dash.dependencies import Input, Output

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient
import base64

from MongoDB_CRUD import AnimalShelter

# SPECIFIED GOOD BOYS/GIRLS
GOOD_GIRLS_OR_BOYS = {
    'water_rescue': {
        'breed': ['Labrador Retriever Mix', 'Chesapeake Bay Retriever', 'Newfoundland'],
        'sex': 'Intact Female',
        'min_age_weeks': 26,
        'max_age_weeks': 156
    },
    'mountain_rescue': {
        'breed': ['German Shepard', 'Alaskan Malamute', 'Old English Sheepdog', 'Siberian Husky', 'Rottweiler'],
        'sex': 'Intact Male',
        'min_age_weeks': 26,
        'max_age_weeks': 156
    },
    'disaster_rescue': {
        'breed': ['Doberman Pinscher', 'German Shepard', 'Golden Retriever', 'Bloodhound', 'Rottweiler'],
        'sex': 'Intact Male',
        'min_age_weeks': 20,
        'max_age_weeks': 300
    }
}

df_dumb = pd.DataFrame(dict(
    my_rage=['coping', 'malding', 'seething'],
    time_spent_waiting=['then', 'now', 'right fucking now']
))
JOKE_CHART = px.line(df_dumb, x='time_spent_waiting', y='my_rage', title='LOADING LOADING LOADING LOADING AAAAAAAAAAAA')

image_filename = 'assets/stupid_logo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
###########################
# Data Manipulation / Model
###########################

username = "aacuser"
password = "password"
shelter = AnimalShelter(username, password)

df = pd.DataFrame.from_records(shelter.read({}))
df.drop(columns=['_id'], inplace=True)

#########################
# Dashboard Layout / View
#########################

# app is primary variable for display on webpage.
app = Dash('SimpleExample')

app.layout = html.Div([
    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), width=1600, height=200),
    html.Center(html.B(html.H1('List of Animals'))),
    html.Hr(),
    dcc.Checklist(
        options=['Dog', 'Cat', 'Bird', 'Other'],
        value=['Dog', 'Cat', 'Bird', 'Other'],
        inline=True,
        id='breed_selection'
    ),
    dcc.RadioItems(
        ['Water', 'Mountain', 'Disaster', 'Reset'],
        '',
        inline=True,
        id='type_rescue'
    ),
    dash_table.DataTable(
        id='datatable-id',
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
        sort_action='native',
        row_selectable='single',
        page_size=10,
        page_current=0,
        hidden_columns=['rec_num', 'date_of_birth', 'datetime', 'monthyear', 'location_lat', 'location_long',
                        'age_upon_outcome_in_weeks'],
        css=[{"selector": ".show-hide", "rule": "display: none"}]  # Gets rid of annoying button

    ),
    html.Br(),
    html.Hr(),
    html.Center(html.B(html.H1('Viewing of Data is Mandatory'))),
    html.Div(className='row',
             style={'display': 'flex'},
             children=[
                 dcc.Graph(
                     id='graph-id',
                     figure=JOKE_CHART
                 ),
                 html.Div(
                     id='map-id',
                     className='col s12 m6',
                 )
             ]),
    html.Br(),
    # html.Header("Image: @dawning_crow"),
    # html.Img(src="https://pbs.twimg.com/media/GH6ECYjaoAAGGem?format=jpg&name=medium", width=300, height=300)

])


#############################################
# Interaction Between Components / Controller
#############################################
# This callback will highlight a row on the data table when the user selects it
@app.callback(
    Output('datatable-id', 'style_data_conditional'),
    [Input('datatable-id', 'selected_rows'),
     Input('datatable-id', 'page_size')]
)
def update_styles(selected_rows, page_size, **kwargs):
    if not selected_rows:
        return []
    return [{
        'if': {'row_index': (i % page_size)},
        'background_color': 'steelblue',  # '#D2F3FF',
        'i': i
    } for i in selected_rows]


@app.callback(
    Output('datatable-id', 'data'),
    [Input('breed_selection', 'value'),
     Input('type_rescue', 'value')]
)
def filter_breed(selections, type_rescue, **kwargs):
    if not type_rescue or type_rescue == 'Reset':
        df_new = df[df['animal_type'].isin(selections)]
        return df_new.to_dict('records')
    # Fun fact: we don't need the animal type for this selection because all of the specified breeds are dogs.
    curr_rescue = ''
    if type_rescue == 'Water':
        curr_rescue = 'water_rescue'
    elif type_rescue == 'Mountain':
        curr_rescue = 'mountain_rescue'
    elif type_rescue == 'Disaster':
        curr_rescue = 'disaster_rescue'
    df_new = df[(df['breed'].isin(GOOD_GIRLS_OR_BOYS[curr_rescue]['breed']))
                & (df['sex_upon_outcome'] == GOOD_GIRLS_OR_BOYS[curr_rescue]['sex'])
                & (df['age_upon_outcome_in_weeks'] >= GOOD_GIRLS_OR_BOYS[curr_rescue]['min_age_weeks'])
                & (df['age_upon_outcome_in_weeks'] <= GOOD_GIRLS_OR_BOYS[curr_rescue]['max_age_weeks'])
                ]
    return df_new.to_dict('records')


# Eventually resets the selected row when page is changed.
@app.callback(
    Output('datatable-id', 'selected_rows'),
    [Input('datatable-id', 'page_current')]
)
def reset_styles(page_curr, **kwargs):
    return []


# THIS IS THE MAP
@app.callback(
    Output('map-id', "children"),
    [Input('datatable-id', "derived_viewport_data"),
     Input('datatable-id', 'selected_rows')])
def update_map(viewData, select, **kwargs):
    if not viewData:
        return []
    dff = pd.DataFrame.from_dict(viewData)
    map_data = [dl.TileLayer(id="base-layer-id")]
    markers_num = []
    if select:
        markers_num.append(select[0] % pageSize)
    else:
        markers_num = range(0, len(viewData))
    for i in markers_num:
        name = (str(dff.iloc[i, 9]) if dff.iloc[i, 9] else "?John")  # I have named the forgotten ones "John"
        map_data.append(
            dl.Marker(position=[dff.iloc[i, 13], dff.iloc[i, 14]], children=[
                dl.Tooltip(name),
                dl.Popup([
                    html.P('Name: ' + name),
                    html.P('Breed: ' + dff.iloc[i, 4]),
                    html.P('Status: ' + dff.iloc[i, 11])
                ])
            ])
        )
    # Austin TX is at [30.75, -97.48]
    return [dl.Map(style={'width': '500px', 'height': '500px'}, center=[30.75, -97.48], zoom=10, children=map_data)
            ]


# THIS IS THE CHART
# THE CHART IS STUPID WHY IS IT EVEN HERE?
@app.callback(
    Output('graph-id', "figure"),
    [Input('datatable-id', "derived_viewport_data")
     ])
def update_chart(viewData, **kwargs):
    if not viewData:
        return JOKE_CHART
    THE_DATA = {}
    dff = pd.DataFrame.from_dict(viewData)
    pageSize = len(viewData)
    for i in range(0, pageSize):
        LOOKHERE = dff.iloc[i, 4]
        if LOOKHERE not in list(THE_DATA.keys()):
            THE_DATA[LOOKHERE] = 1.0 / pageSize
        else:
            THE_DATA[LOOKHERE] = ((THE_DATA[LOOKHERE] * pageSize) + 1.0) / pageSize

    return px.pie(dff, names=list(THE_DATA.keys()), values=list(THE_DATA.values()), hole=0.3)


# print("dash version=", dash.__version__) updated dash version
app.run(debug=True)