# encoding: UTF-8

from flask import render_template
from functools import lru_cache

from pyecharts import options as opts
from pyecharts.charts import Line, Bar, Grid
from flask import render_template

from cboe_monitor.data_manager import VIXDataManager, GVZDataManager, OVXDataManager
from cboe_monitor.utilities import run_over_time_frame, CLOSE_PRICE_NAME


#----------------------------------------------------------------------
@lru_cache
def get_vix_info():
    # query data from the data manager
    # param date is for lru_cache only
    delivery_dates, schedule_days = run_over_time_frame()
    vdm = VIXDataManager(delivery_dates)
    df = vdm.combine_all(24)
    rets_vix = vdm.analyze()
    gvzm = GVZDataManager([])
    rets_gvzm = gvzm.analyze()
    ovxm = OVXDataManager([])
    rets_ovxm = ovxm.analyze()
    df_gvz = rets_gvzm['gvz'][[CLOSE_PRICE_NAME]]
    df_gvz.rename({CLOSE_PRICE_NAME : 'gvz'}, axis = 1, inplace = True)
    df_ovx = rets_ovxm['ovx'][[CLOSE_PRICE_NAME]]
    df_ovx.rename({CLOSE_PRICE_NAME : 'ovx'}, axis = 1, inplace = True)
    df = df.join(df_gvz)
    df = df.join(df_ovx)
    return df


#----------------------------------------------------------------------
def line(delivery_dates, df):
    # line the vix
    FLINE_OPT = opts.LineStyleOpts(opacity = 1, width = 1.5)
    OLINE_OPT = opts.LineStyleOpts(opacity = 0.9, width = 1.2, type_ = 'dashed')
    df['delivery'] = [10 + 5 * (idx in delivery_dates) for idx in df.index]
    line = (Line()
            .add_xaxis(xaxis_data = df.index)
            .add_yaxis("vix", df[0], is_symbol_show = False,
                       areastyle_opts = opts.AreaStyleOpts(opacity = 0.2),
                       linestyle_opts = FLINE_OPT,
                       markline_opts = opts.MarkLineOpts(
                           data = [
                               opts.MarkLineItem(type_ = "min", name = "ivl"),
                               opts.MarkLineItem(type_ = "max", name = "ivh"),
                           ]))
            .add_yaxis('gvz', df['gvz'],
                       is_symbol_show = False, linestyle_opts = FLINE_OPT,
                       markline_opts = opts.MarkLineOpts(
                           data = [
                               opts.MarkLineItem(type_ = "min", name = "ivl"),
                               opts.MarkLineItem(type_ = "max", name = "ivh"),
                           ]
                       ))
            .add_yaxis('ovx', df['ovx'],
                       is_symbol_show = False, linestyle_opts = FLINE_OPT,
                       is_selected = False,
                       markline_opts = opts.MarkLineOpts(
                           data = [
                               opts.MarkLineItem(type_ = "min", name = "ivl"),
                               opts.MarkLineItem(type_ = "max", name = "ivh"),
                           ]))
            .add_yaxis("1", df[1], is_symbol_show = False,
                       linestyle_opts = OLINE_OPT)
            .add_yaxis("2", df[2], is_symbol_show = False,
                       linestyle_opts = OLINE_OPT, is_selected = False)
            .add_yaxis("3", df[3], is_symbol_show = False,
                       linestyle_opts = OLINE_OPT)
            .add_yaxis("4", df[4], is_symbol_show = False,
                       linestyle_opts = OLINE_OPT, is_selected = False)
            .add_yaxis("5", df[5], is_symbol_show = False,
                       linestyle_opts = OLINE_OPT)
            # add delivery date mark, not a good idea, but worked.
            .add_yaxis("delivery", df['delivery'], is_symbol_show = False, is_step = True)
            .set_series_opts(
                label_opts = opts.LabelOpts(is_show = False))
            .set_global_opts(
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
                tooltip_opts = opts.TooltipOpts(trigger = "axis", axis_pointer_type = "line"),
                datazoom_opts = opts.DataZoomOpts(type_ = "slider", range_start = 50, range_end = 100),
            ))
    return line


#----------------------------------------------------------------------
def get_template():
    return render_template('vix.html')


#----------------------------------------------------------------------
def get_data():
    delivery_dates, schedule_days = run_over_time_frame()
    df = get_vix_info()
    chart = line(delivery_dates, df)
    return chart.dump_options_with_quotes()
