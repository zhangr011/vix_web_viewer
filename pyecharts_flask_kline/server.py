# encoding: UTF-8

from flask import Flask

import configparser
ini_config = configparser.ConfigParser()
DATA_CONFIG_PATH = './data/data.ini'
DATA_SECTION = 'data'
ini_config.read(DATA_CONFIG_PATH)

# data path
OPTIONS_DATA_PATH = ini_config.get(DATA_SECTION, 'options_monitor')
CBOE_DATA_PATH = ini_config.get(DATA_SECTION, 'cboe_vix_gvz_ovx_monitor')

# set the data path
from options_monitor.data_ref import set_data_root as options_set_data_root
options_set_data_root(OPTIONS_DATA_PATH)

from cboe_monitor.utilities import set_data_root as cboe_set_data_root
cboe_set_data_root(CBOE_DATA_PATH)

# handlers
import options_handlers
import cboe_handlers

app = Flask(__name__, static_folder="templates")


@app.route("/<product>/<date_str>")
def options(product: str, date_str: str):
    return options_handlers.get_template(product, date_str)

@app.route("/siv/<product>/<date_str>")
def options_data(product: str, date_str: str):
    """kline data"""
    return options_handlers.get_data(product, date_str)

@app.route("/vix")
def vix():
    return cboe_handlers.get_template()

@app.route("/vix/data")
def vix_data():
    return cboe_handlers.get_data()


if __name__ == "__main__":
    app.run(host='0.0.0.0')
