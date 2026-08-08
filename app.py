
from flask import Flask, render_template, request, session, jsonify
from dopa_analyzer import analyze_mp3
import os, uuid

app = Flask(__name__)
app.secret_key = 'dopagaki'
UPLOAD='uploads'
os.makedirs(UPLOAD, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

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

if __name__ == '__main__':
    app.run(debug=True)

