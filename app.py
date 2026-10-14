
from flask import Flask, render_template, request, session, jsonify
from dopa_analyzer import analyze_mp3
import os, uuid

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

@app.route('/dopa_test')
def dopa_test():
    return render_template('dopa_test.html')





#開発用
if __name__ == '__main__':
    app.run(debug=True)

