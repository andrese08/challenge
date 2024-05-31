from flask import Flask, jsonify
from data import campos_combinados

app = Flask(__name__)

@app.route('/api/campos_combinados', methods=['GET'])
def obtener_campos_combinados():
    return jsonify(campos_combinados)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=2000, debug=True)
