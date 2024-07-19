from dash import Dash, dcc
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

from MongoDB_CRUD import db_CRUD

###########################
# Data Manipulation / Model
###########################

# Initialize MongoDB connection.
database = db_CRUD("", "")
df = pd.DataFrame.from_records(database.read({}))

# Drop id column for compatibility.
df.drop(columns=['_id'], inplace=True)
# Rearrange columns in the order I want.
df = df[['name', 'short-desc', 'rarity', 'properties', 'size', 'img', 'long-desc']]

#########################
# Dashboard Layout / View
#########################
# app is primary variable for display on webpage.
app = Dash('SimpleExample')

# HTML of webpage
app.layout = html.Div([
    html.Img(src='/assets/HakitaPieceofHeaven.png', style={
        'height': '100%',
        'width': '20%',
    }),
    html.Center(html.B(html.H1('Cool Cole Fish'))),
    html.Hr(),
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
        hidden_columns=['long-desc', 'img'],
        css=[{"selector": ".show-hide", "rule": "display: none"}],  # Gets rid of annoying button
        style_cell={'textAlign': 'left'}

    ),
    html.Br(),
    html.Hr(),
    html.Div(id='fishDisplay-id', style={'display': 'flex'})
])


#############################################
# Methods for modifying displayed data.
#############################################
# Highlights a row on the data table when the user selects it
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
        'background_color': 'steelblue',
        'i': i
    } for i in selected_rows]


# VERY IMPORTANT - Presents data when new fish is selected
@app.callback(
    Output('fishDisplay-id', 'children'),
    [Input('datatable-id', 'selected_rows'),
     Input('datatable-id', 'derived_viewport_data')]
)
def update_fish(selected_row, pageData, **kwargs):
    fishSelect = 'Test Fish'
    if selected_row:
        fishSelect = pageData[selected_row[0]]['name']
    df_result = df.query('name == @fishSelect')
    # Process new data
    fishDetails = html.Div(style={'float': 'left', 'width': '33%', 'padding-left': '30px'},
                           children=dcc.Markdown('''
                           # %s 
                           ## %s
                           ## Fish Rarity:
                           %s
                           ## Fish Properties
                           %s
                           ''' % ('**%s**' % df_result.iat[0, 0], '_%s_' % df_result.iat[0, 1],
                                  df_result.iat[0, 2], df_result.iat[0, 3])))

    fishImg = html.Img(src='/assets/fish/%s' % df_result.iat[0, 5], width=300, height=300,
                       style={'margin': 'auto', 'width': '33%', 'border': '1px solid #355', 'float': 'center'})

    fishDescription = html.P(df_result.iat[0, 6],
                             style={'float': 'right', 'width': '33%', 'padding': '80px', 'text-align': 'left'})

    return [fishDetails, fishImg, fishDescription]


####################
# Run application.
app.run(debug=True)
