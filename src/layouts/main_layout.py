import dash
import components



def create_layout(App: dash.Dash) -> dash.html.Div:
    

    
    layout = dash.html.Div(
        [
            dash.dcc.Location(id="url", refresh=True),
            components.nav_bar.render(App),
            dash.html.Div(id="page-content", children=[]),
            dash.page_container,
        ]
    )


    return layout