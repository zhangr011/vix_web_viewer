#encoding: UTF-8

from typing import List, Sequence, Union
from functools import lru_cache
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid, Tab
from pyecharts.globals import ThemeType
from flask import render_template


from options_monitor.data_manager import SIVManager
from options_monitor.data_ref import \
    PRODUCT_GROUP_NAME, FUTURE_HV_NAMES_REVERSE, \
    IV_NAME, IV_PER, OPEN_INTEREST_NAME, HV_20_NAME, HV_250_NAME, \
    CLOSE_PRICE_NAME, VOLUME_NAME


import pandas as pd

THEME_ME = ThemeType.WHITE


#----------------------------------------------------------------------
@lru_cache
def get_siv_info(now_date_str: str):
    """analyze"""
    siv_mgr = SIVManager()
    all_dfs = siv_mgr.prepare(None, now_date_str)
    return all_dfs


#----------------------------------------------------------------------
def get_iv_data(product: str, date_str: str):
    """get the iv data by contract and date"""
    analyze_dfs = get_siv_info(date_str)
    product_rev = FUTURE_HV_NAMES_REVERSE.get(product)
    for df in analyze_dfs:
        if df[PRODUCT_GROUP_NAME][0] == product_rev:
            return df[df.index <= date_str]


#----------------------------------------------------------------------
def kline_chart(data: pd.DataFrame, product: str):
    # 最后的 Grid
    grid_chart = Grid(init_opts = opts.InitOpts(theme = THEME_ME))
    dates = data.index.to_list()

    kline = (
        Kline(init_opts = opts.InitOpts())
        .add_xaxis(xaxis_data = dates)
        .add_yaxis(
            series_name = "kline",
            y_axis = list(zip(data[CLOSE_PRICE_NAME], data[CLOSE_PRICE_NAME],
                              data[CLOSE_PRICE_NAME] * 0.995, data[CLOSE_PRICE_NAME] * 1.005)),
            itemstyle_opts=opts.ItemStyleOpts(
                color="#ef232a",
                color0="#14b143",
                border_color="#ef232a",
                border_color0="#14b143",
            ),
        )
        .extend_axis(
            yaxis = opts.AxisOpts(
                name = 'vix',
                is_scale = True,
                axislabel_opts = opts.LabelOpts(formatter = "{value} %"), interval = 5
            )
        )
        .extend_axis(
            yaxis = opts.AxisOpts(
                is_show = False,
                is_scale = False,
                min_ = 0,
                max_ = 500,
            ),
        )
        .set_series_opts(
            label_opts = opts.LabelOpts(is_show=False),
            # 'circle', 'rect', 'roundRect', 'triangle', 'diamond', 'pin', 'arrow', 'none'
            markline_opts = opts.MarkLineOpts(
                data = [
                    opts.MarkLineItem(type_ = "min", name = "最低价", symbol = 'none'),
                    opts.MarkLineItem(type_ = "max", name = "最高价", symbol = 'none'),
                ]
            ),
        )
        .set_global_opts(
            title_opts = opts.TitleOpts(title = f"{product} siv", pos_left="0"),
            xaxis_opts = opts.AxisOpts(
                type_="category",
                is_scale=True,
                boundary_gap=False,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
                split_number=20,
                min_="dataMin",
                max_="dataMax",
            ),
            yaxis_opts = opts.AxisOpts(
                name = "指数价格",
                position = "left",
                is_scale = True,
                splitline_opts = opts.SplitLineOpts(is_show = True),
            ),
            tooltip_opts = opts.TooltipOpts(trigger = "axis", axis_pointer_type = "line"),
            legend_opts = opts.LegendOpts(is_show = True),
            datazoom_opts = opts.DataZoomOpts(type_ = "slider", range_start = 0, range_end = 100),
        )
    )

    # two lines to show ivp, normal ivp with cyan, warn vip for red.
    ivp = data[IV_PER]
    ivp_shift_left = ivp.shift(-1)
    data['ivp_warn'] = data[IV_PER][(ivp >= 91) | (ivp <= 15) |
                                    (ivp_shift_left >= 91) | (ivp_shift_left <= 15)]

    hv_show = True
    if not data[IV_NAME].isnull().all():
        hv_show = False

    siv_line = (
        Line(init_opts = opts.InitOpts())
        .add_xaxis(xaxis_data = dates)
        .add_yaxis(
            series_name = "siv",
            y_axis = data[IV_NAME] * 100,
            yaxis_index = 1,
            is_symbol_show = False,
            # is_smooth=True,
            markline_opts = opts.MarkLineOpts(
                data = [
                    opts.MarkLineItem(type_ = "min", name = "ivl"),
                    opts.MarkLineItem(type_ = "max", name = "ivh"),
                ]
            ),
            linestyle_opts = opts.LineStyleOpts(opacity = 1, width = 1.5),
            label_opts = opts.LabelOpts(is_show = False),
        )
        .add_yaxis(
            series_name = "siv5",
            y_axis = data[IV_NAME].rolling(5).mean() * 100,
            yaxis_index = 1,
            is_symbol_show = False,
            # is_smooth=True,
            linestyle_opts = opts.LineStyleOpts(opacity = 0.9, width = 1.2, color = 'gold'),
            label_opts = opts.LabelOpts(is_show = False),
        )
        .add_yaxis(
            series_name = "siv10",
            y_axis = data[IV_NAME].rolling(10).mean() * 100,
            yaxis_index = 1,
            is_symbol_show = False,
            # is_smooth=True,
            linestyle_opts = opts.LineStyleOpts(opacity = 0.9, width = 1.2, color = 'cyan'),
            label_opts = opts.LabelOpts(is_show = False),
        )
        .add_yaxis(
            series_name = "hv20",
            y_axis = data[HV_20_NAME] * 100,
            yaxis_index = 1,
            is_symbol_show = False,
            is_selected = hv_show,
            # is_smooth=True,
            linestyle_opts = opts.LineStyleOpts(opacity = 0.9, width = 1.2, color = 'black'),
            label_opts = opts.LabelOpts(is_show = False),
        )
        .add_yaxis(
            series_name = "hv250",
            y_axis = data[HV_250_NAME] * 100,
            yaxis_index = 1,
            is_symbol_show = False,
            is_selected = hv_show,
            # is_smooth=True,
            linestyle_opts = opts.LineStyleOpts(opacity = 0.8, width = 1),
            label_opts = opts.LabelOpts(is_show = False),
        )
        .add_yaxis(
            series_name = "ivp",
            y_axis = ivp,
            yaxis_index = 2,
            is_symbol_show = False,
            # is_smooth=True,
            linestyle_opts = opts.LineStyleOpts(
                opacity = 1,
                width = 1.2,
                color = 'cyan'),
            label_opts = opts.LabelOpts(is_show = False),
        )
        .add_yaxis(
            series_name = "ivp_warn",
            y_axis = data['ivp_warn'],
            yaxis_index = 2,
            is_symbol_show = False,
            linestyle_opts = opts.LineStyleOpts(
                opacity = 1,
                width = 1.2,
                color = 'red'),
            # is_smooth=True,
            label_opts = opts.LabelOpts(is_show = False),
        )
    )

    # K线图和 siv 图
    kline.overlap(siv_line)
    return kline


#----------------------------------------------------------------------
def get_template(product: str, date_str: str):
    kwargs = {"product" : product,
              "date" : date_str,
              "tabs": FUTURE_HV_NAMES_REVERSE.keys()}
    return render_template('options.html', **kwargs)


#----------------------------------------------------------------------
def get_data(product: str, date_str: str):
    data = get_iv_data(product, date_str)
    kline = kline_chart(data, product)
    return kline.dump_options_with_quotes()
