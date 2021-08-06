from napkin import response, request
import numpy as np
import sys
import random
import pandas as pd
import traceback


def atari(percentage):
    # 乱数設定
    percentage = int(10000 / percentage)
    # 1 - 10000 の中で乱数をpercentage個決めればいいから、
    atari = []
    while len(atari) < percentage:
        temp = random.randint(1, 10000)
        if not temp in atari:
            atari.append(temp)
    return atari


def chusen(mode, normal_atari, koukaku_atari):
    lottery = random.randint(1, 10000)
    if mode == "通常":
        # 低確率状態での抽せん
        if lottery in normal_atari:
            result = "atari"
        else:
            result = "hazure"
    elif mode == "高確率":
        # 高確率状態での抽せん
        if lottery in koukaku_atari:
            result = "atari"
        else:
            result = "hazure"
    else:
        pass
    return result


def furiwake(result, mode, kakuhen, keizoku):
    if result == "atari":
        if mode == "高確率":
            # 高確率中の連荘
            judge = random.randint(1, 100)
            if judge <= keizoku:
                # 確変大当たり
                next = "高確率"
            else:
                # 通常大当たり
                next = "通常"
        else:
            # 低確率中の大当たり
            judge = random.randint(1, 100)
            if judge <= kakuhen:
                # 確変大当たり
                next = "高確率"
            else:
                # 通常大当たり
                next = "通常"
    else:
        if mode == "高確率":
            # 高確率中のはずれ
            next = "高確率"
        else:
            # 低確率中のはずれ
            next = "通常"
    return next


def main(dammy, normal, koukaku, kakuhen, keizoku):
    # # 低確率状態での大当たり確率[1/n]
    # normal = float(args[1])
    # # 高確率状態での大当たり確率[1/n]
    # koukaku = float(args[2])
    # # 高確率状態突入率[%]
    # kakuhen = float(args[3])
    # # 高確率状態継続率[%]
    # keizoku = float(args[4])
    # 確認
    print("低確率：" + str(normal))
    print("高確率：" + str(koukaku))
    # ラムクリア
    kaiten = 0
    kaiten_sum = 0
    mode = "通常"
    cols = ['kaiten', 'mode', 'next']
    df = pd.DataFrame(index=[], columns=cols)
    # 乱数設定(大当たりとなる数値を決める)
    normal_atari = atari(normal)
    koukaku_atari = atari(koukaku)
    # 試行回数分回す
    while kaiten_sum < 2000:
        kaiten = kaiten + 1
        kaiten_sum = kaiten_sum + 1
        # 抽せん
        result = chusen(mode, normal_atari, koukaku_atari)
        # 抽せん結果で振り分け
        next = furiwake(result, mode, kakuhen, keizoku)
        # データに記入
        if result == "atari":
            result_df = pd.Series([kaiten, mode, next], index=df.columns)
            df = df.append(result_df, ignore_index=True)
            mode = next
            kaiten = 0
        else:
            pass
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)

    records = df.to_dict(orient='records')

    return records


# main処理

print(str(request.args))

params = request.args

response.headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"}

try:
    # 低確率状態での大当たり確率[1/n]
    normal = float(params.get('normal', 5))
    # 高確率状態での大当たり確率[1/n]
    koukaku = float(params.get('koukaku', 10))
    # 高確率状態突入率[%]
    kakuhen = float(params.get('kakuhen', 5))
    # 高確率状態継続率[%]
    keizoku = float(params.get('keizoku', 5))

    result = main("", normal, koukaku, kakuhen, keizoku)

    response.status_code = 200
    response.body = result

except Exception as e:
    print(e)
    traceback.print_exc()
    response.status_code = 400

    response.body = {'status': 400, 'messege': "invalid request"}
