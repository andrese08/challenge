from flask import Flask, jsonify, request

app = Flask(__name__)

# Datos de ejemplo
campos_combinados = [
    {"id": 1, "nombre": "Campo 1"},
    {"id": 2, "nombre": "Campo 2"},
    {"id": 3, "nombre": "Campo 3"}
]

# Ruta para obtener todos los campos combinados
@app.route('/api/campos_combinados', methods=['GET'])
def obtener_campos_combinados():
    return jsonify(campos_combinados)

# Ruta para obtener un campo combinado por su ID
@app.route('/api/campos_combinados/<int:campo_id>', methods=['GET'])
def obtener_campo_combinado(campo_id):
    campo = next((campo for campo in campos_combinados if campo['id'] == campo_id), None)
    if campo:
        return jsonify(campo)
    else:
        return jsonify({'mensaje': 'Campo combinado no encontrado'}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=2000, debug=True)

