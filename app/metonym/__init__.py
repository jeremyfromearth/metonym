import json
import requests
import markdown
from flask import Flask, render_template, request
from metonym.parser import MetonymParser

app = Flask(__name__)
parser = MetonymParser()

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/parse', methods=['POST'])
def parse():
  ast = None
  try:
    parser.go(request.get_data(as_text=True))
  except Exception as e:
    return json.dumps({
          'error': str(e)
        })
  return str(parser.output)
