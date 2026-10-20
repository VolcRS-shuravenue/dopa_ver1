
from flask import Flask, render_template, request, session, jsonify
from dopa_analyzer import analyze_mp3
import os, uuid
import random


app = Flask(__name__)
app.secret_key = 'dopagaki'
UPLOAD='uploads'
os.makedirs(UPLOAD, exist_ok=True)


#トップページ
@app.route('/')
def index():
    return render_template('index.html')

#曲のドパ度判定
@app.route('/song_terms')
def song_terms():
    return render_template('song_terms.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    f = request.files['mp3']
    p = os.path.join(UPLOAD, str(uuid.uuid4()) + '.mp3')
    f.save(p)
    session['mp3_path'] = p
    return render_template('judging.html')

@app.route('/finish_analysis', methods=['POST'])
def finish_analysis():
    p = session['mp3_path']
    result = analyze_mp3(p)
    
    session['result'] = result
    os.remove(p)
    return jsonify({'ok':True})

@app.route('/result')
def result_page():
    return render_template('result.html', result=session.get('result',{}))


#ドパガキ判定
@app.route('/person_terms')
def person_terms():
    return render_template('person_terms.html')


TOPICS = [
    "essay",
    "explanation",
    "novel"
]


@app.route('/readings')
def dopa_test():
    article_type = random.choice(TOPICS)
    if article_type == "essay":
        readings_type = "readings1.html"
    elif article_type == "explanation":
        readings_type = "readings2.html"
    elif article_type == "novel":
        readings_type = "readings3.html"

    return render_template(readings_type)


user_data = {}

@app.route('/submit_metrics', methods=['POST'])
def submit_metrics():

    global user_data

    user_data = request.json

    score = calculate_score(user_data)

    return jsonify({'score': score})

@app.route("/result_metrics")
def result_metrics():

    score = int(request.args.get('score',0))

    return render_template('result_metrics.html', score=score)


def calculate_score(data):

    scroll_count = data.get('scrollCount', 0)
    scroll_speed = data.get('scrollSpeed', 0)
    load_clicks = data.get('loadClicks', 0)
    quiz_score = data.get('quizScore', 0)

    score = 0

    score += min(scroll_count * 0.4, 20)#スクロール回数
    score += min(scroll_speed * 0.2, 20)#スクロール速度
    score += min(load_clicks * 5, 30)#ロードクリック回数
    score += (100 - quiz_score) * 0.3 #クイズの正答率

    return round(score)


if __name__ == "__main__":
    app.run(debug=True)

#開発用
if __name__ == '__main__':
    app.run(debug=True)

