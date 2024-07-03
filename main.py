"""
df3_gseのrecordテーブルから、データをプロットする
"""
# モジュールの取得
# 基本
import math
import datetime as dt
# DB
import pandas as pd
from sqlalchemy import create_engine
# プロット
import matplotlib
from matplotlib import dates
from matplotlib import pyplot as plt
# Curses
import curses


def get_time_range():
    """ 時刻範囲とデータ取得用SQLを生成 """
    # ティック刻み15分の場合
    t0 = dt.datetime.now()
    u_stop = (math.floor(t0.timestamp() / (15 * 60)) + 1) * 15 * 60
    start = dt.datetime.fromtimestamp(u_stop - 2 * 60 * 60)
    stop = dt.datetime.fromtimestamp(u_stop)
    start_str = start.strftime('%Y-%m-%d %H:%M:%S')

    # データ取得用SQL
    cmd = "select * from record where TS > '%s'" % start_str
    return t0, start, stop, cmd


def update(engine, fig, axs):
    """ 描画の更新 """
    # 描画パラメータ取得
    t0, start, stop, query = get_time_range()
    axs[0, 0].set_xlim(start, stop)
    axs[1, 0].set_xlim(start, stop)
    axs[0, 1].set_xlim(start, stop)
    axs[1, 1].set_xlim(start, stop)

    # DB接続と解除
    sqlcmd = "select * from record where TS > '%s'" % start.strftime("%Y-%m-%d %H:%M:%S")
    df = pd.read_sql(sqlcmd, con=engine)
    fig.suptitle("Drill Monitor [%s]" % t0.strftime("%F %H:%M:%S"))

    # プロット1 温度
    lines1 = [axs[0, 0].plot(df.TS, df.BAT_T * 0.6 + 0.8, ".", label="BAT_T", color='g'),
              axs[0, 0].plot(df.TS, df.SYS_T * 1.0 + 0.0, ".", label="SYS_T", color='r'),
              axs[0, 0].plot(df.TS, df.SYS_H * 1.0 + 0.0, ".", label="SYS_H", color='b'),
              axs[0, 0].plot(df.TS, df.MOT_T * 0.6 + 0.8, ".", label="MOT_T", color='y'),
              axs[0, 0].plot(df.TS, df.GEA_T * 0.6 + 0.8, ".", label="GEA_T", color='m'),
              axs[0, 0].plot(df.TS, df.LIQ1_T * 0.6 + 0.8, ".", label="LIQ1_T", color='m'),
              axs[0, 0].plot(df.TS, df.LIQ2_T * 0.6 + 0.8, ".", label="LIQ2_T", color='m')
              ]
    axs[0, 0].legend(loc='lower left')

    # プロット2 電力
    lines2 = [axs[1, 0].plot(df.TS, df.PDU_V * 0.6 + 0.8, ".", label="PDU_V", color='g'),
              axs[1, 0].plot(df.TS, df.BAT_V * 1.0 + 0.0, ".", label="BAT_V", color='r'),
              axs[1, 0].plot(df.TS, df.MOT_V * 1.0 + 0.0, ".", label="MOT_V", color='b')]
    axs[1, 0].legend(loc='lower left')

    # プロット3 掘削ステータス
    lines3 = [axs[0, 1].plot(df.TS, df.MOT_R * 0.6 + 0.8, ".", label="MOT_R", color='g'),
              axs[0, 1].plot(df.TS, df.GND_P * 1.0 + 0.0, ".", label="GND_P", color='r'),
              ]
    axs[0, 1].legend(loc='lower left')

    # プロット4 姿勢
    lines4 = [axs[1, 1].plot(df.TS, df.GRA_X * 0.6 + 0.8, ".", label=".GRA_X", color='g'),
              axs[1, 1].plot(df.TS, df.GRA_Y * 1.0 + 0.0, ".", label="GRA_Y", color='r'),
              axs[1, 1].plot(df.TS, df.GRA_Z * 1.0 + 0.0, ".", label="GRA_Z", color='b')
              ]
    axs[1, 1].legend(loc='lower left')

    # 後始末
    plt.pause(1)
    for ll in lines1:
        ll[0].remove()
    for ll in lines2:
        ll[0].remove()
    for ll in lines3:
        ll[0].remove()
    for ll in lines4:
        ll[0].remove()


def main(stdscr):
    # DB接続と解除
    url = f'mysql+pymysql://root:pass@localhost:3306/df3_gse'
    engine = create_engine(url, echo=False)

    # 画面準備
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)
    stdscr.addstr(1, 1, "GSE Graphic running... [stop ESC]")

    # キャンバスの準備
    matplotlib.use("TkAgg")
    matplotlib.rcParams['font.family'] = ['IPAexGothic']
    fig, axs = plt.subplots(2, 2, figsize=(14, 7))
    plt.subplots_adjust(hspace=0.3)

    # 座標軸の設定
    axs[0, 0].set_title("System Temperature")
    axs[0, 0].xaxis.set_major_formatter(dates.DateFormatter('%m/%d\n%H:%M'))
    axs[0, 0].set_ylim(-60, 60)
    axs[0, 0].grid()
    axs[1, 0].set_title("Power Supply")
    axs[1, 0].xaxis.set_major_formatter(dates.DateFormatter('%m/%d\n%H:%M'))
    axs[1, 0].set_ylim(0, 240)
    axs[1, 0].grid()
    axs[0, 1].set_title("Drill Status")
    axs[0, 1].xaxis.set_major_formatter(dates.DateFormatter('%m/%d\n%H:%M'))
    axs[0, 1].set_ylim(-100, 100)
    axs[0, 1].grid()
    axs[1, 1].set_title("Attitude")
    axs[1, 1].xaxis.set_major_formatter(dates.DateFormatter('%m/%d\n%H:%M'))
    axs[1, 1].set_ylim(-100, 100)
    axs[1, 1].grid()

    # データ描画
    while True:
        update(engine, fig, axs)
        rtc = stdscr.getch()
        if rtc == 0x1b:  # ESC
            break

    # 画面の後始末
    curses.nocbreak()
    stdscr.keypad(False)
    stdscr.nodelay(False)
    curses.echo()
    curses.endwin()


if __name__ == '__main__':
    curses.wrapper(main)
