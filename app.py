import dash
from dash import dcc, html
from constants import BG
from callbacks import register_callbacks

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    # Stores fenêtre principale
    dcc.Store(id='store-mdf-path'),
    dcc.Store(id='store-domaines'),
    dcc.Store(id='store-flags-erreur'),
    dcc.Store(id='store-plage', data=None),
    dcc.Store(id='store-canaux-selectionnes', data=[]),
    dcc.Store(id='store-vue', data='graphes'),
    dcc.Store(id='store-mdf-s2'),
    dcc.Store(id='store-dummy'),
    # Stores fenêtre détachée
    dcc.Store(id='store-mdf-path-det'),
    dcc.Store(id='store-domaines-det'),
    dcc.Store(id='store-flags-erreur-det'),
    dcc.Store(id='store-plage-det', data=None),
    dcc.Store(id='store-canaux-selectionnes-det', data=[]),
    dcc.Store(id='store-vue-det', data='graphes'),
    # Layout
    dcc.Location(id='url', refresh=False),
    html.Div(id='contenu-page'),
], style={'background': BG, 'minHeight': '100vh'})

register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True)