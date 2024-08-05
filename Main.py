import gunicorn
from dash import Dash, dcc
import dash_leaflet as dl
from dash import dcc
from dash import html
import plotly.express as px
from dash import dash_table
from dash.dependencies import Input, Output
import pandas as pd

from MongoDB_CRUD import db_CRUD

###########################
# Data Manipulation / Model
###########################
# Page size of displayed table. Necessary for calculations within update_fish method.
PAGE_SIZE = 10
# Initialize MongoDB connection.
database = db_CRUD('cole_admin', 'orcasplashdessert', 'localhost', 27017,
                   'Cole_Fish', 'Feesh')
if database.checkConnection():
    df = pd.DataFrame.from_records(database.read({}))
else:
    df = pd.DataFrame({'_id': 0, 'name': 'ERROR Fish', 'short-desc': 'Failed to load database.', 'rarity': '',
                                    'properties': '', 'size': '', 'img': 'fish_error.png', 'long-desc': 'Please consult MongoDB connection.'}, index=[0])
# Drop id column for compatibility.
df.drop(columns=['_id'], inplace=True)
# Rearrange columns in the order I want.
df = df[['name', 'short-desc', 'rarity', 'properties', 'size', 'img', 'long-desc']]
# Sort by rarity. Non-configurable atm.
df = df.sort_values(by=['rarity'])

#########################
# Dashboard Layout / View
#########################
# app is primary variable for display on webpage.
app = Dash('SimpleExample')
server = app.server

# HTML of webpage
app.layout = html.Div([
    html.Img(src='/assets/banner.png', style={
        'height': '200px',
        'width': '100%',
        'left-padding': '30px',
        'right-padding': '30px',
    }, alt='Cool Cole Fish'),
    html.Hr(),
    dash_table.DataTable(
        id='datatable-id',
        columns=[
            {"name": i, "id": i, "deletable": False} for i in df.columns
        ],
        data=df.to_dict('records'),
        sort_action='none',
        row_selectable='single',
        cell_selectable=False,
        page_size=PAGE_SIZE,
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
    while not pageData:  # Errors thrown when callback tries to run when viewport data hasn't loaded.
        pass
    fishSelect = pageData[0]['name']
    if selected_row:
        fishSelect = pageData[selected_row[0] % PAGE_SIZE]['name']
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
app.run_server(debug=True)
