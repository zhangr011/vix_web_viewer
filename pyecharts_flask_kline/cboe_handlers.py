# encoding: UTF-8

from flask import render_template
from functools import lru_cache

from pyecharts import options as opts
from pyecharts.charts import Line, Bar, Grid
from flask import render_template

from cboe_monitor.data_manager import VIXDataManager, GVZDataManager, OVXDataManager
from cboe_monitor.utilities import run_over_time_frame, CLOSE_PRICE_NAME, get_last_day


#----------------------------------------------------------------------
@lru_cache
def get_vix_info(last_date):
    # query data from the data manager
    # param last_date is for lru_cache only
    delivery_dates, schedule_days = run_over_time_frame()
    vdm = VIXDataManager(delivery_dates)
    df = vdm.combine_all(24)
    rets_vix = vdm.analyze()
    gvzm = GVZDataManager([])
    rets_gvzm = gvzm.analyze()
    ovxm = OVXDataManager([])
    rets_ovxm = ovxm.analyze()
    vix_diff = rets_vix['vix_diff'][[1]]
    vix_diff.rename({1 : 'diff'}, axis = 1, inplace = True)
    df_gvz = rets_gvzm['gvz'][[CLOSE_PRICE_NAME]]
    df_gvz.rename({CLOSE_PRICE_NAME : 'gvz'}, axis = 1, inplace = True)
    df_ovx = rets_ovxm['ovx'][[CLOSE_PRICE_NAME]]
    df_ovx.rename({CLOSE_PRICE_NAME : 'ovx'}, axis = 1, inplace = True)
    df = df.join(vix_diff)
    df = df.join(df_gvz)
    df = df.join(df_ovx)
    return df, delivery_dates


#----------------------------------------------------------------------
def get_warning_areas(df):
    """get the warning based on vix_diff"""
    warning = False
    areas = []
    start = None
    for date, diff in zip(df.index, df['diff']):
        if warning is False and diff < -0.005:
            warning = True
            start = date
        elif warning is True and diff >= 0.02:
            warning = False
            areas.append((start, date))
            start = None
    # close the last area
    if start is not None:
        last_date = df.index[-1]
        if start == last_date:
            # move the last date to the previous
            start = df.index[-2]
        areas.append((start, last_date))
    return areas

#----------------------------------------------------------------------
def line(delivery_dates, df):
    # line the vix
    FLINE_OPT = opts.LineStyleOpts(opacity = 1, width = 1.5)
    OLINE_OPT = opts.LineStyleOpts(opacity = 0.9, width = 1.2, type_ = 'dashed')
    df['delivery'] = [10 + 5 * (idx in delivery_dates) for idx in df.index]
    warning_areas = get_warning_areas(df)
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
                label_opts = opts.LabelOpts(is_show = False),
                markarea_opts = opts.MarkAreaOpts(
                    is_silent = True,
                    data = [opts.MarkAreaItem(name = "warn", x=(xs, xe)) for xs, xe in warning_areas],
                    itemstyle_opts = opts.ItemStyleOpts(color = '#FFA54F10')
                ))
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
    last_day = get_last_day()
    df, delivery_dates = get_vix_info(last_day)
    chart = line(delivery_dates, df)
    return chart.dump_options_with_quotes()
