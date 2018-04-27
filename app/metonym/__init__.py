import json
import requests
import markdown
from flask import Flask, render_template, request, jsonify
from metonym.parser import MetonymParser, RasaCompiler

app = Flask(__name__)
parser = MetonymParser()
compiler = RasaCompiler()

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/parse', methods=['POST'])
def parse():
  try:
    ast = parser.go(request.get_data(as_text=True))
    ast_json = json.loads(repr(ast))
    rasa = compiler.go(ast, 'test-intent')
    rasa_json = json.loads(rasa)
    return jsonify({
      'ast': ast_json,
      'rasa': rasa_json
      })
  except Exception as e:
    print(e)
    return json.dumps({
      'error': str(e)
    })
