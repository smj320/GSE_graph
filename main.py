"""
df3_gseのrecordテーブルから、データをプロットする
"""
# モジュールの取得
# 基本
import math
import datetime as dt
# DB
import pandas as pd
import sqlalchemy as sa
# プロット
import matplotlib
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
# キー操作
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


def update(engine, ax):
    """ 描画の更新 """
    # 描画パラメータ取得
    t0, start, stop, query = get_time_range()
    ax.set_xlim(start, stop)

    # DB接続と解除
    sqlcmd = "select * from record where TS > '%s'" % start.strftime("%Y-%m-%d %H:%M:%S")
    df = pd.read_sql(sqlcmd, con=engine)

    # プロット
    lines = [ax.plot(df.TS, df.BAT_T, ".", label="BAT_T", color='g'),
             ax.plot(df.TS, df.SYS_T, ".", label="SYS_T", color='r'),
             ax.plot(df.TS, df.SYS_H, ".", label="SYS_H", color='b'),
             ax.plot(df.TS, df.MOT_T, ".", label="MOT_T", color='y'),
             ax.plot(df.TS, df.GEA_T, ".", label="GEA_T", color='m')]
    ax.set_title("System Temperature    [%s]" % t0.strftime("%F %H:%M:%S"))
    ax.legend(loc='lower left')

    # 後始末
    plt.pause(1)
    for line in lines:
        line[0].remove()


def main():
    # スクリーン初期化
    stdscr = curses.initscr()
    curses.cbreak()
    stdscr.keypad(True)

    # DB接続と解除
    url = f'mysql+pymysql://root:pass@localhost:3306/df3_gse'
    engine = sa.create_engine(url, echo=False)

    # キャンバスの準備
    matplotlib.use("TkAgg")
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 5)

    # 座標軸の設定
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%H:%M'))
    ax.set_ylim(-60, 60)
    ax.grid()

    # データ描画
    stdscr.addstr(1, 1, "Plot Start: Exit ESC key", curses.A_BOLD)
    while True:
        update(engine, ax)
        c = stdscr.getch()
        if c == 0x1B:  # ESC
            break

    # 後始末
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()


if __name__ == "__main__":
    main()
