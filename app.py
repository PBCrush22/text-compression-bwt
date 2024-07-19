from flask import Flask, request, render_template, send_file, redirect, url_for
from encoder import RunLengthEncoder
from decoder import RunLengthDecoder
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    action = request.form.get('action')
    
    if file and action == 'encode':
        filename = 'uploaded.txt'
        file.save(filename)
        with open(filename, "r") as f:
            string = f.read()
        if string[-1] != '$':
            string += '$'
        encoder = RunLengthEncoder(string)
        return send_file('encoder_output.bin', as_attachment=True)

    if file and action == 'decode':
        filename = 'uploaded.bin'
        file.save(filename)
        decoder = RunLengthDecoder(filename)
        return send_file('decoder_output.txt', as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
