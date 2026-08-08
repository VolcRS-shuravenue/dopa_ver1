import librosa
import numpy as np


def analyze_mp3(path):

    # ------------------
    # 音源読み込み
    # ------------------

    y, sr = librosa.load(path)

    # ------------------
    # BPM
    # ------------------

    tempo, _ = librosa.beat.beat_track(
        y=y,
        sr=sr
    )

    tempo = float(np.mean(tempo))

    # BPM倍取り補正

    if tempo > 180:
        tempo = tempo / 2

    bpm_score = min(
        20,
        tempo / 150 * 20
    )

    # ------------------
    # 曲の長さ
    # ------------------

    duration = librosa.get_duration(
        y=y,
        sr=sr
    )

    if duration <= 180:
        duration_score = 10

    elif duration <= 300:
        duration_score = 5

    else:
        duration_score = 0

    # ------------------
    # 音量変化
    # ------------------

    rms = librosa.feature.rms(y=y)[0]

    volume_change = np.std(rms)

    volume_score = min(
        30,
        volume_change * 250
    )

    # ------------------
    # 音の高低差
    # ------------------

    centroid = librosa.feature.spectral_centroid(
        y=y,
        sr=sr
    )[0]

    pitch_range = (
        np.max(centroid)
        - np.min(centroid)
    )

    range_score = min(
        10,
        pitch_range / 1200
    )

    # ------------------
    # 音の高低変化率
    # ------------------

    pitch_speed = np.std(
        np.diff(centroid)
    )

    speed_score = min(
        30,
        (pitch_speed / 25) ** 1.3
    )

    # ------------------
    # 合計
    # ------------------

    score = (
        bpm_score
        + duration_score
        + volume_score
        + range_score
        + speed_score
    )

    score = int(
        min(score, 100)
    )

    # ------------------
    # ランク
    # ------------------

    if score >= 85:
        rank = "S"

    elif score >= 70:
        rank = "A"

    elif score >= 55:
        rank = "B"

    elif score >= 40:
        rank = "C"

    else:
        rank = "D"

    return {

        "bpm":
            round(tempo, 1),

        "duration":
            round(duration, 1),

        "volume_change":
            round(float(volume_change), 3),

        "pitch_range":
            round(float(pitch_range), 1),

        "pitch_speed":
            round(float(pitch_speed), 1),

        "bpm_score":
            round(float(bpm_score), 1),

        "duration_score":
            round(float(duration_score), 1),

        "volume_score":
            round(float(volume_score), 1),

        "range_score":
            round(float(range_score), 1),

        "speed_score":
            round(float(speed_score), 1),

        "score":
            score,

        "rank":
            rank

    }