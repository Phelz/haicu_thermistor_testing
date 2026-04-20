
import dash
from dash_bootstrap_components.themes import LUX as THEME


# UI for displaying the camera feeds
app = dash.Dash(
    __name__,
    title="HAICU Thermistor Testing",
    external_stylesheets=[THEME],
    use_pages=True,
    meta_tags=[
        {"charset": "utf-8"},
        {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"},
    ],
)

import layouts.main_layout
app.layout = layouts.main_layout.create_layout(app)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)

# if __name__ == "__main__":
#     threading.Thread(target=app.run).start()
#     server.run()