import json
import logging
import requests

from bokeh.plotting import figure, curdoc
from bokeh.embed import file_html, json_item
from bokeh.io import show
from bokeh.models import CustomJS, DateSlider

import pandas as pd

from flask import jsonify, Blueprint

from icenet_app.utils import load_json, get_forecast_data

# hover,crosshair,pan,undo,redo,
TOOLS = "wheel_zoom,zoom_in,zoom_out,box_zoom,reset,box_select,poly_select,lasso_select,examine,help"

plots = Blueprint('plots', __name__, template_folder='templates')


@plots.route("/sie_change")
def plot_sie_change():
    inventory = get_forecast_data()
    return line_plot(load_json("output_sie_growth.json",
                               icenet_data_inventory=inventory),
                     title="Sea ice extent change")


@plots.route("/trend_mean")
def plot_trend_mean():
    inventory = get_forecast_data()
    return line_plot(load_json("output_trend.json",
                               icenet_data_inventory=inventory)['mean'],
                     title="Sea ice mean change")


@plots.route("/trend_stddev")
def plot_trend_stddev():
    inventory = get_forecast_data()
    return line_plot(load_json("output_trend.json",
                               icenet_data_inventory=inventory)['stddev'],
                     title="Ensemble stddev change")


@plots.route("/date_picker")
def date_picker():
    inventory = get_forecast_data()
    date_range_files = sorted([df.split(".")[1] for df in inventory.keys() if df.endswith(".png")])
    if len(date_range_files) < 1:
        logging.warning("No image data available")
        return jsonify([])
    else:
        date_range = pd.date_range(date_range_files[0], date_range_files[-1])

    date_slider = DateSlider(value=date_range[0].date(),
                             start=date_range[0].date(),
                             end=date_range[-1].date())
    date_slider.js_on_change("value", CustomJS(code="""
        let date = new Date(this.value);
        let month = date.getMonth() + 1;
        let monthStr = month < 10 ? "0" + month: month;
        let dayStr = date.getDate() < 10 ? "0" + date.getDate() : date.getDate();
        let dateStr = "".concat(date.getFullYear(), monthStr, dayStr);
        console.log("Showing " + dateStr);
        /*$("img#fc_image_sic_" + fc_image_cur_id).hide();
        $("img#fc_image_stddev_" + fc_image_cur_id).hide();
        $("img#fc_image_sic_" + dateStr).show();
        $("img#fc_image_stddev_" + dateStr).show();
        fc_image_cur_id = dateStr;*/
    """))

    return jsonify(json_item(date_slider))


def line_plot(data, title):
    p = figure(title=title, tools=TOOLS, width=500, height=300)
    p.line(list(data.keys()), list(data.values()))
    return json.dumps(json_item(p))

