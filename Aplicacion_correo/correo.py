from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import smtplib
from email.mime.text import MIMEText
import json

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Ruta al archivo de configuración
CONFIG_FILE = 'config.json'

# Función para cargar la configuración desde un archivo JSON
def cargar_configuracion():
    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
    return config

config = cargar_configuracion()

API_URL = 'http://remote_api_server/api/combined_data'  # URL API informacion

def enviar_correo(destinatario, mensaje):
    remitente = config['usuario_smtp']
    asunto = 'Asunto del correo'
    
    mensaje = MIMEText(mensaje)
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto

    servidor = smtplib.SMTP(config['servidor_smtp'], config['puerto_smtp'])
    servidor.starttls()
    servidor.login(config['usuario_smtp'], config['password_smtp'])
    servidor.send_message(mensaje)
    servidor.quit()

@app.route('/api/verificar_y_enviar_emails', methods=['POST'])
def verificar_y_enviar_emails():
    response = requests.get(API_URL)
    if response.status_code == 200:
        datos_combinados = response.json()
        for dato in datos_combinados:
            if dato['db_class'] == 'High':
                mensaje_correo = f"De acuerdo a la información suministrada, la clasificación para la tabla {dato['db_class']} es crítica, por esta razón es necesario que envíe la respuesta con el OK de aprobación al E-mail: xxxx@meli.com"
                enviar_correo(dato['user_manager'], mensaje_correo)
        return jsonify({'message': 'Correos enviados exitosamente.'}), 200
    else:
        return jsonify({'error': 'Error al obtener datos de la API'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
