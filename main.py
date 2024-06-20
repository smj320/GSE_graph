# モジュールの取得
import datetime as dt
import math
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import use as use
from matplotlib import dates as mdates
from mysql import connector as con

global config, fig, ax


def main():
    global config, fig, ax
    config = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "pass",
        "database": "df3_gse"
    }

    use("TkAgg")
    plt.ion()

    # コネクション断時の再接続設定
    # connection.ping(reconnect=True)

    fig, ax = plt.subplots()
    fig.set_size_inches(10, 5)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%H:%M'))
    ax.set_ylim(-60, 60)
    ax.grid()

    for i in range(86400):
        update(i)


def update(flame):
    global config, fig, ax
    # 描画パラメータ取得
    t0, start, stop, cmd = get_time_range()
    ax.set_xlim(start, stop)

    # DB接続と解除
    connection = con.connect(**config)
    cur = connection.cursor()
    cur.execute(cmd)
    rows = np.array(cur.fetchall()).transpose()
    cur.close()
    connection.close()

    # データ取り出し
    times = rows[1]
    y1 = rows[6]    #BAT_T
    y2 = rows[7]    #SYS_T
    y3 = rows[8]    #SYS_H
    y4 = rows[12]*0.8047+0.497    #MOT_T
    y5 = rows[13]*0.8046+0.5344    #GEA_T

    line1, = ax.plot(times, y1, ".", label="BAT_T", color='g')
    line2, = ax.plot(times, y2, ".", label="SYS_T", color='r')
    line3, = ax.plot(times, y3, ".", label="SYS_H", color='b')
    line4, = ax.plot(times, y4, ".", label="MOT_T", color='y')
    line5, = ax.plot(times, y5, ".", label="GEA_T", color='m')
    ax.set_title("System Temperature    [%s]" % t0.strftime("%F %H:%M:%S"))
    ax.legend(loc=0)
    plt.pause(1)
    line1.remove()
    line2.remove()
    line3.remove()
    line4.remove()
    line5.remove()


def get_time_range():
    # 現在時刻
    t0 = dt.datetime.now()
    # ティック刻み15分の場合,時間繰り越しがあるので15分足して15分で丸める
    t1 = t0 + dt.timedelta(minutes=15)
    stop = np.datetime64(t1.replace(minute=math.floor(t1.minute / 15) * 15, second=0, microsecond=0))
    start = stop - np.timedelta64(2, 'h')
    str_st = start.astype(np.datetime64)
    cmd = "select * from record where TS > '%s'" % str_st
    return t0, start, stop, cmd


if __name__ == "__main__":
    main()
