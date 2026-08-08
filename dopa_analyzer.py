
import librosa
import numpy as np


def analyze_mp3(path):

    # ==================================================
    # 音源読み込み
    # ==================================================

    y, sr = librosa.load(path)

    # ==================================================
    # BPM
    # ==================================================

    tempo, _ = librosa.beat.beat_track(
        y=y,
        sr=sr
    )

    tempo = float(np.mean(tempo))

    # BPMが倍取りされている場合
    if tempo > 180:
        tempo /= 2

    # ------------------------------------------
    # BPMスコア
    # 最大15点
    # ------------------------------------------

    bpm_score = min(
        15,
        max(
            0,
            (tempo / 150) ** 1.2 * 7.5
        )
    )

    # ==================================================
    # 曲の長さ
    # ==================================================

    duration = librosa.get_duration(
        y=y,
        sr=sr
    )

    minutes = duration / 60

    # ------------------------------------------
    # 短い曲ほどドパ曲寄り
    # 最大20点
    # ------------------------------------------

    if minutes < 2.5:
        duration_score = 20

    elif minutes < 3.0:
        duration_score = 18

    elif minutes < 3.5:
        duration_score = 16

    elif minutes < 4.0:
        duration_score = 13

    elif minutes < 5.0:
        duration_score = 8

    elif minutes < 6.0:
        duration_score = 3

    else:
        duration_score = 0

    # ==================================================
    # 音量変化
    # ==================================================

    rms = librosa.feature.rms(
        y=y
    )[0]

    volume_change = float(
        np.std(rms)
    )

    # ------------------------------------------
    # 最大20点
    # ------------------------------------------

    volume_score = min(
        20,
        volume_change * 180
    )

    # ==================================================
    # 音の高低変化
    # ==================================================

    centroid = librosa.feature.spectral_centroid(
        y=y,
        sr=sr
    )[0]

    pitch_speed = float(
        np.std(
            np.diff(centroid)
        )
    )

    # ------------------------------------------
    # 最大10点
    # ------------------------------------------

    speed_score = min(
        10,
        (pitch_speed / 100) ** 1.7
    )

    # ==================================================
    # 展開密度
    # ==================================================

    bandwidth = librosa.feature.spectral_bandwidth(
        y=y,
        sr=sr
    )[0]

    segments = 24

    step = max(
        1,
        len(rms) // segments
    )

    transition_strength = []

    for i in range(
        step,
        len(rms) - step,
        step
    ):

        prev_energy = np.mean(
            rms[i-step:i]
        )

        next_energy = np.mean(
            rms[i:i+step]
        )

        prev_tone = np.mean(
            centroid[i-step:i]
        )

        next_tone = np.mean(
            centroid[i:i+step]
        )

        prev_band = np.mean(
            bandwidth[i-step:i]
        )

        next_band = np.mean(
            bandwidth[i:i+step]
        )

        energy_change = abs(
            next_energy -
            prev_energy
        ) * 1000

        tone_change = abs(
            next_tone -
            prev_tone
        )

        band_change = abs(
            next_band -
            prev_band
        ) / 5

        transition_strength.append(
            energy_change +
            tone_change +
            band_change
        )

    avg_change = float(
        np.mean(
            transition_strength
        )
    )

    # ------------------------------------------
    # 展開密度 最大20点
    # ------------------------------------------

    progression_score = min(
        20,
        (avg_change / 80) ** 1.3
    )

    # ==================================================
    # 楽器密度
    # ==================================================

    instrument_density = float(
        np.mean(
            bandwidth
        )
    )

    # ------------------------------------------
    # 最大15点
    # ------------------------------------------

    density_score = min(
        15,
        (instrument_density / 700) ** 1.5
    )

    # ==================================================
    # 基礎スコア
    # ==================================================

    # 各項目を100点基準に正規化してから
    # 重みを掛ける
    #
    # BPM       : 15
    # 曲の長さ   : 20
    # 音量変化   : 20
    # 高低変化   : 10
    # 展開密度   : 20
    # 楽器密度   : 15

    base_score = (

        (bpm_score / 15) * 15 +

        (duration_score / 20) * 20 +

        (volume_score / 20) * 20 +

        (speed_score / 10) * 10 +

        (progression_score / 20) * 20 +

        (density_score / 15) * 15

    )

    # ==================================================
    # スコアのコントラスト調整
    # ==================================================

    # 50点前後に固まりすぎるのを防ぐ

    score = (
        base_score * 1.8
        - 20
    )

    # ==================================================
    # 全体的に刺激が弱い曲へのペナルティ
    # ==================================================

    # 1～2項目だけ強くても、
    # 全体として刺激が弱ければドパ曲とはしない

    if base_score < 40:

        score -= (
            40 - base_score
        ) * 2

    # 0～100に収める

    score = int(
        np.clip(
            score,
            0,
            100
        )
    )

    # ==================================================
    # ランク
    # ==================================================

    # 80点をSの境界に変更
    #
    # S : 80～100
    # A : 65～79
    # B : 50～64
    # C : 35～49
    # D : 0～34

    if score >= 80:
        rank = "S"

    elif score >= 65:
        rank = "A"

    elif score >= 50:
        rank = "B"

    elif score >= 35:
        rank = "C"

    else:
        rank = "D"

    # ==================================================
    # 特殊評価
    # ==================================================

    # 「滅」はランクではなく、
    # 「好きすぎて滅」という特殊評価として扱う。
    #
    # 現時点では自動判定せず、
    # ランクとは独立した項目にしておく。

    special_evaluation = None

    # ==================================================
    # 出力
    # ==================================================

    return {

        "bpm":
            round(tempo, 1),

        "duration":
            round(duration, 1),

        "volume_change":
            round(volume_change, 3),

        "pitch_speed":
            round(pitch_speed, 1),

        "avg_change":
            round(avg_change, 1),

        "instrument_density":
            round(
                instrument_density,
                1
            ),

        "bpm_score":
            round(bpm_score, 1),

        "duration_score":
            round(duration_score, 1),

        "volume_score":
            round(volume_score, 1),

        "speed_score":
            round(speed_score, 1),

        "progression_score":
            round(
                progression_score,
                1
            ),

        "density_score":
            round(
                density_score,
                1
            ),

        "base_score":
            round(
                base_score,
                1
            ),

        "score":
            score,

        "rank":
            rank,

        "special_evaluation":
            special_evaluation
    }


# ==================================================
# 実行例
# ==================================================

if __name__ == "__main__":

    result = analyze_mp3(
        "your_music.mp3"
    )

    print("========== 分析結果 ==========")

    print(
        f"BPM: {result['bpm']}"
    )

    print(
        f"曲の長さ: {result['duration']} 秒"
    )

    print(
        f"音量変化: {result['volume_change']}"
    )

    print(
        f"高低変化: {result['pitch_speed']}"
    )

    print(
        f"展開密度: {result['avg_change']}"
    )

    print(
        f"楽器密度: {result['instrument_density']}"
    )

    print("------------------------------")

    print(
        f"BPMスコア: {result['bpm_score']}"
    )

    print(
        f"曲の長さスコア: {result['duration_score']}"
    )

    print(
        f"音量変化スコア: {result['volume_score']}"
    )

    print(
        f"高低変化スコア: {result['speed_score']}"
    )

    print(
        f"展開密度スコア: {result['progression_score']}"
    )

    print(
        f"楽器密度スコア: {result['density_score']}"
    )

    print("------------------------------")

    print(
        f"基礎スコア: {result['base_score']}"
    )

    print(
        f"最終スコア: {result['score']}"
    )

    print(
        f"ランク: {result['rank']}"
    )

    print(
        f"特殊評価: {result['special_evaluation']}"
    )

