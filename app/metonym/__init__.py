import json
from flask import Flask, render_template, request
from metonym.parser import MetonymParser

app = Flask(__name__)
parser = MetonymParser()

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/parse', methods=['POST'])
def parse():
  ast = parser.go(request.get_data(as_text=True))
  return str(ast)
