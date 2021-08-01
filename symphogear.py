import random
import time
import pandas as pd
# --------------------------------------------------------------------
#  ____                        _
# / ___| _   _ _ __ ___  _ __ | |__   ___   __ _  ___  __ _ _ __
# \___ \| | | | '_ ` _ \| '_ \| '_ \ / _ \ / _` |/ _ \/ _` | '__|
#  ___) | |_| | | | | | | |_) | | | | (_) | (_| |  __/ (_| | |
# |____/ \__, |_| |_| |_| .__/|_| |_|\___/ \__, |\___|\__,_|_|
#        |___/          |_|                |___/
# --------------------------------------------------------------------
# 何回転試行するか
challenge = 1000
# --------------------------------------------------------------------
# 特図1の分母
heso = 199.4
# 特図2の分母
denchu = 7.7
# 最終決戦の回数
fine = 5
# STの回数
st = 11
# --------------------------------------------------------------------
# 当せん乱数の個数の計算
heso_ran = 1 / heso * 65536
heso_ran2 = int(heso_ran)
denchu_ran = 1 / denchu * 65536
denchu_ran2 = int(denchu_ran)
# 乱数生成
a = list(range(0, 65536))
heso_atari = random.sample(a, heso_ran2)
denchu_atari = random.sample(a, denchu_ran2)
# --------------------------------------------------------------------
# pandasフレームの作成
cols = ['回転数', '大当たり', '備考']
df = pd.DataFrame(index=[], columns=cols)
# --------------------------------------------------------------------
print("------------------")
print("大当たり確率(特図1) : 1/" + str(heso))
print("大当たり確率(特図2) : 1/" + str(denchu))
print("------------------")
# --------------------------------------------------------------------
mode = "normal"
kaiten = 0
for i in range (0, challenge):
    if mode == "normal" :
        kaiten = kaiten + 1
        hesoheso = random.randint(0, 65536)
        if hesoheso in heso_atari:
            print("大当たり！(通常中)" + str(kaiten) + "回転")
            time.sleep(1.0)
            record = pd.Series([kaiten, "通常", "---"], index=df.columns)
            df = df.append(record, ignore_index=True)
            kaiten = 0
            print("最終決戦開幕")
            for j in range (0, fine):
                kaiten = kaiten + 1
                i = i + 1
                kessen = random.randint(0, 65536)
                if kessen in denchu_atari:
                    print("大当たり！(確変中)" + str(kaiten) + "回転\n確変突入")
                    record = pd.Series([kaiten, "確変", "連荘"], index=df.columns)
                    df = df.append(record, ignore_index=True)
                    kaiten = 0
                    mode = "kakuhen"
                    time.sleep(1.0)
                    break
                else:
                    if j == (fine - 1):
                        print("不承不承ながら左打ちしましょう。")
                        time.sleep(1.0)
                        mode = "normal"
                    else:
                        print("あと" + str(fine - j - 1) + "回")
                        time.sleep(1.0)
        else :
            continue
    elif mode == "kakuhen" :
        for k in range(0, st):
            kaiten = kaiten + 1
            i = i + 1
            denchu = random.randint(0, 65536)
            if denchu in denchu_atari:
                print("大当たり！(確変中)" + str(kaiten) + "回転")
                time.sleep(1.0)
                record = pd.Series([kaiten, "確変", "連荘"], index=df.columns)
                df = df.append(record, ignore_index=True)
                mode = "kakuhen"
                kaiten = 0
                break
            else:
                if k == (st - 1):
                    print("不承不承ながら左打ちしましょう。")
                    time.sleep(1.0)
                    mode = "normal"
                else :
                    print("あと" + str(st - k - 1) + "回")
                    time.sleep(1.0)

print("------------------")
print(df)
