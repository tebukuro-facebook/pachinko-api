from napkin import response, request

import random
import pandas as pd
import numpy as np
import sys
import traceback


def main(normal, koukaku, tokuzu1, tokuzu2, challenge):
    # # 特図2での大当たり確率[1/n]
    # normal = float(args[1])
    # # 特図2での小当たり確率[1/n]
    # koukaku = float(args[2])
    # # 特図1当せん時の電サポ回数[回]
    # tokuzu1 = float(args[3])
    # # 特図2当せん時の電サポ回数[回]
    # tokuzu2 = float(args[4])
    # # 試行回数
    # challenge = int(args[5])
    # 確認
    print("低確率：1/" + str(normal))
    print("高確率：1/" + str(koukaku))
    # 乱数設定
    heso, denchu = random_select(normal, koukaku)
    # ラムクリア
    kaiten, kaiten_sum, mode = ram_clear()
    # 大当たり表の枠作成
    result = create_flame()
    # ここから抽せん開始。。
    for i in range(0, challenge):
        # 高確率か低確率か最終決戦中かを判定する
        if mode == "normal":
            kekka = chusen_normal(heso)
        elif mode == "koukaku":
            kekka = chusen_koukaku(heso, denchu, kaiten, tokuzu2)
        else:
            kekka = chusen_fine(denchu, kaiten, tokuzu1)
        # 0ははずれ。何もせずに回転数を足す
        # 1は特図1での大当たり。電サポをtokuzu1回す
        # 2は特図2での大当たり。電サポをtokuzu2回す
        # 9は左打ちに戻す
        if kekka == 0:
            # はずれ
            kaiten = kaiten + 1
            kaiten_sum = kaiten_sum + 1
        elif kekka == 1:
            # 特図１での大当たり。振り分け判定。
            furiwake = furiwake_heso()
            # 回転数を記録後、リセット
            record = pd.Series([kaiten, furiwake], index=result.columns)
            result = result.append(record, ignore_index=True)
            kaiten = 0
            kaiten_sum = kaiten_sum + 1
            # 最終決戦突入。ただし振り分けで1％を引くと高確率直行
            if furiwake != "全回転":
                mode = "fine"
            else:
                mode = "koukaku"
        elif kekka == 2:
            # 特図2大当たり。振り分け判定。
            furiwake = furiwake_denchu()
            # 回転数を記録後、リセット
            record = pd.Series([kaiten, furiwake], index=result.columns)
            result = result.append(record, ignore_index=True)
            kaiten = 0
            kaiten_sum = kaiten_sum + 1
            # 次回も高確率
            mode = "koukaku"
        else:
            # kekka==9を想定。不承不承ながら左打ち
            mode = "normal"
    # result.to_csv("result.csv", index=None)
    records = result.to_dict(orient='records')

    return records


def ram_clear():
    # ラムクリア
    kaiten = 0
    kaiten_sum = 0
    mode = "normal"
    return kaiten, kaiten_sum, mode


def random_select(normal, koukaku):
    # 乱数設定を行う。大当たり確率は65536個中のX個で決定している。
    heso_ran = 1 / normal * 65536
    heso_ran = int(heso_ran)
    denchu_ran = 1 / koukaku * 65536
    denchu_ran = int(denchu_ran)
    # 乱数生成
    a = list(range(0, 65536))
    heso_atari = random.sample(a, heso_ran)
    denchu_atari = random.sample(a, denchu_ran)
    return heso_atari, denchu_atari


def create_flame():
    # Pandasフレームの作成
    cols = ['回転数', '大当たり']
    df = pd.DataFrame(index=[], columns=cols)
    return df


def chusen_normal(tokuzu1):
    # 特図１での抽せん
    lottery = random.randint(0, 65536)
    if lottery in tokuzu1:
        # 大当たり
        result = 1
    else:
        # はずれ
        result = 0
    return result


def chusen_koukaku(tokuzu1_atari, tokuzu2_atari, kaiten, limit):
    # 特図2での抽せん
    if kaiten <= limit:
        lottery = random.randint(0, 65536)
        if lottery in tokuzu2_atari or lottery in tokuzu1_atari:
            # 大当たり
            result = 2
        else:
            # はずれ
            result = 0
    else:
        # 左打ちに戻す信号を送る
        result = 9
    return result


def chusen_fine(tokuzu2_atari, kaiten, limit):
    # 最終決戦中の扱い
    if kaiten <= limit:
        lottery = random.randint(0, 65536)
        if lottery in tokuzu2_atari:
            # 大当たり
            result = 2
        else:
            # はずれ
            result = 0
    else:
        # 左打ちに戻す信号を送る
        result = 9
    return result


def furiwake_heso():
    # 特図１の振り分けは99%が通常。1%は右打ち直行
    a = random.randint(0, 100)
    if a != 50:
        heso = "4R"
    else:
        heso = "全回転"
    return heso


def furiwake_denchu():
    # ここはラウンド振り分け。
    # シンフォギアは4Rが50%,8Rが7%,12Rが3%,15Rが40%
    a = random.randint(0, 100)
    if a < 50:
        denchu = "4R（SC）"
    elif a >= 50 and a < 57:
        denchu = "7R（SC）"
    elif a >= 57 and a < 60:
        denchu = "12R（SC）"
    else:
        denchu = "15R（SC）"
    return denchu


# main処理

print(str(request.args))

params = request.args

response.headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"}

try:
    # 特図2での大当たり確率[1/n]
    normal = float(params.get('normal', 199))
    # 特図2での小当たり確率[1/n]
    koukaku = float(params.get('koukaku', 60))
    # 特図1当せん時の電サポ回数[回]
    tokuzu1 = float(params.get('tokuzu1', 10))
    # 特図2当せん時の電サポ回数[回]
    tokuzu2 = float(params.get('tokuzu2', 10))
    # 試行回数
    challenge = int(params.get('challenge', 1000))

    result = main(normal, koukaku, tokuzu1, tokuzu2, challenge)

    response.status_code = 200
    response.body = result

except Exception as e:
    print(e)
    traceback.print_exc()
    response.status_code = 400

    response.body = {'status': 400, 'messege': "invalid request"}
