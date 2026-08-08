import librosa
import numpy as np


def analyze_mp3(path):
    y, sr = librosa.load(path)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(np.mean(tempo))

    if tempo > 180:
        tempo /= 2

    bpm_score = min(15, tempo / 160 * 15)

    duration = librosa.get_duration(y=y, sr=sr)
    minutes = duration / 60

    if minutes < 3:
        duration_score = 10
    elif minutes < 4:
        duration_score = 8
    elif minutes < 5:
        duration_score = 6
    elif minutes < 6:
        duration_score = 4
    else:
        duration_score = 0

    rms = librosa.feature.rms(y=y)[0]
    volume_change = float(np.std(rms))
    volume_score = min(20, volume_change * 180)

    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

    pitch_speed = float(np.std(np.diff(centroid)))
    speed_score = min(20, (pitch_speed / 25) ** 1.5)

    block = max(10, len(centroid) // 20)
    changes = 0

    for i in range(block, len(centroid), block):
        prev = np.mean(centroid[i-block:i])
        cur = np.mean(centroid[i:min(i + block, len(centroid))])

        if abs(cur - prev) > np.std(centroid) * 0.3:
            changes += 1

    progression_score = min(20, changes * 1.5)

    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    instrument_density = float(np.mean(bandwidth))
    density_score = min(15, instrument_density / 250)

    score = (
        bpm_score +
        duration_score +
        volume_score +
        speed_score +
        progression_score +
        density_score
    )

    score = int(min(score, 100))

    if score >= 85:
        rank = 'S'
    elif score >= 70:
        rank = 'A'
    elif score >= 55:
        rank = 'B'
    elif score >= 40:
        rank = 'C'
    else:
        rank = 'D'

    return {
        'bpm': round(tempo, 1),
        'duration': round(duration, 1),
        'volume_change': round(volume_change, 3),
        'pitch_speed': round(pitch_speed, 1),
        'progression_count': changes,
        'instrument_density': round(instrument_density, 1),
        'bpm_score': round(bpm_score, 1),
        'duration_score': round(duration_score, 1),
        'volume_score': round(volume_score, 1),
        'speed_score': round(speed_score, 1),
        'progression_score': round(progression_score, 1),
        'density_score': round(density_score, 1),
        'score': score,
        'rank': rank
    }
