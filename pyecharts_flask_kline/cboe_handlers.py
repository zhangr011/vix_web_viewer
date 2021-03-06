# encoding: UTF-8

from flask import render_template
from functools import lru_cache

from pyecharts import options as opts
from pyecharts.charts import Line, Bar, Grid
from flask import render_template

from cboe_monitor.data_manager import VIXDataManager, GVZDataManager, OVXDataManager
from cboe_monitor.utilities import run_over_time_frame


#----------------------------------------------------------------------
@lru_cache
def get_vix_info():
    # query data from the data manager
    delivery_dates, schedule_days = run_over_time_frame()
    vdm = VIXDataManager(delivery_dates)
    df = vdm.combine_all()
    rets_vix = vdm.analyze()
    gvzm = GVZDataManager([])
    rets_gvzm = gvzm.analyze()
    ovxm = OVXDataManager([])
    rets_ovxm = ovxm.analyze()
    return df, delivery_dates, rets_vix, rets_gvzm, rets_ovxm


#----------------------------------------------------------------------
def line(df, rets_vix, rets_gvzm, rets_ovxm):
    light_area_opt = opts.AreaStyleOpts(opacity = 0.05)
    line = (Line()
            .add_xaxis(xaxis_data = df.index)
            .add_yaxis("0", df[0], is_symbol_show = False,
                       areastyle_opts = opts.AreaStyleOpts(opacity = 0.2),
                       markline_opts = opts.MarkLineOpts(
                           data = [
                               opts.MarkLineItem(type_ = "min", name = "ivl"),
                               opts.MarkLineItem(type_ = "max", name = "ivh"),
                           ]
                       ),
            ).add_yaxis("1", df[1], is_symbol_show = False)
            .add_yaxis("2", df[2], is_symbol_show = False, is_selected = False)
            .add_yaxis("3", df[3], is_symbol_show = False)
            .add_yaxis("4", df[4], is_symbol_show = False, is_selected = False)
            .add_yaxis("5", df[5], is_symbol_show = False)
            .set_series_opts(
                label_opts = opts.LabelOpts(is_show = False)
            ).set_global_opts(
                title_opts = opts.TitleOpts(title = "vix", pos_left = "0"),
                xaxis_opts = opts.AxisOpts(
                    type_ = "category",
                    is_scale = True,
                    boundary_gap = False,
                    axisline_opts = opts.AxisLineOpts(is_on_zero = False),
                    splitline_opts = opts.SplitLineOpts(is_show = False),
                    split_number = 20,
                    min_ = "dataMin",
                    max_ = "dataMax",
                ),
                yaxis_opts = opts.AxisOpts(
                    is_scale = True, splitline_opts=opts.SplitLineOpts(is_show=True)
                ),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="line"),
            ))
    return line


#----------------------------------------------------------------------
def get_template():
    return render_template('vix.html')


#----------------------------------------------------------------------
def get_data():
    df, delivery_dates, rets_vix, rets_gvzm, rets_ovxm = get_vix_info()
    chart = line(df, rets_vix, rets_gvzm, rets_ovxm)
    return chart.dump_options_with_quotes()
