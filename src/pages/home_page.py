import dash
import layouts.home_layout

dash.register_page(__name__, path="/")

layout = layouts.home_layout.create_layout(dash.get_app(), dash.get_app().server)