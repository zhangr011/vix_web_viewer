# vix_web_viewer
vix and siv web viewer based on cboe_vix_gvz_ovx_monitor and options_monitor.

this is only for data viewing, the data collecting is by https://github.com/zhangr011/cboe_vix_gvz_ovx_monitor.git and https://github.com/zhangr011/options_monitor.git

```
# copy the data.ini and modify the data path
cp ./data/data.back.ini ./data/data.ini
# then start the flask web
bash ./start_flask.sh restart
```
