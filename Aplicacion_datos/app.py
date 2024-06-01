from flask import Flask, render_template, request, redirect, url_for, flash
import subprocess
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para usar flash messages

# Ruta de la carpeta específica para guardar archivos JSON y CSV
DATA_FOLDER = 'data'
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def ejecutar_script_batch():
    try:
        # Ejecutar el script batch
        subprocess.run(["ejecutar_script.bat"], shell=True)
        print("El script batch se ha ejecutado correctamente.")
        flash('El script batch se ha ejecutado correctamente.')
    except Exception as e:
        print(f"Error al ejecutar el script batch: {e}")
        flash('Error al ejecutar el script batch.')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        cantidad = request.form['cantidad']
        
        # Validación del valor ingresado
        if not cantidad.isdigit() or int(cantidad) < 1:
            flash('Por favor ingresa una cantidad válida (>= 1).')
            return redirect(url_for('index'))
        
        cantidad = int(cantidad)
        return redirect(url_for('form', cantidad=cantidad))
    
    return render_template('index.html')

@app.route('/form/<int:cantidad>', methods=['GET', 'POST'])
def form(cantidad):
    if request.method == 'POST':
        datos = []
        
        for i in range(cantidad):
            # Obtener valores de cada campo
            db_name = request.form.get(f'db_name_{i}')
            user_id = request.form.get(f'user_id_{i}')
            db_class = request.form.get(f'db_class_{i}')
            
            # Validación para asegurar que todos los campos estén diligenciados
            if not db_name or not user_id or not db_class:
                flash('Todos los campos deben ser diligenciados.')
                return redirect(url_for('form', cantidad=cantidad))
            
            # Agregar los datos al arreglo
            datos.append({
                'db_name': db_name,
                'user_id': user_id,
                'db_class': db_class
            })

        # Guardar los datos en un archivo JSON en la carpeta específica
        archivo_path = os.path.join(DATA_FOLDER, 'datos.json')
        with open(archivo_path, 'w') as json_file:
            json.dump(datos, json_file)

        return redirect(url_for('upload'))

    return render_template('form.html', cantidad=cantidad)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se ha seleccionado ningún archivo.')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No se ha seleccionado ningún archivo.')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            file_path = os.path.join(DATA_FOLDER, file.filename)
            file.save(file_path)
            flash('Archivo CSV cargado de manera correcta, si desea ejecutar el proceso de carga utiliza el boton.')
            return redirect(url_for('validate'))  # Redirigir a la página 'validate.html'
        else:
            flash('El archivo debe ser un CSV.')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/validate')
def validate():
    return render_template('validate.html')

@app.route('/execute_import', methods=['POST'])
def execute_import():
    if request.method == 'POST':
        try:
            # Ejecutar el script import_data.py
            script_path = 'C:/Users/Juli-Edd/Documents/challenge/Aplicacion_datos/codigo/import_data.py'
            print(f"Ejecutando el script: {script_path}")
            subprocess.run(['python', script_path])
                        
            return redirect(url_for('enviado'))
        except Exception as e:
            flash('Error al ejecutar el proceso de carga: ' + str(e))
            return redirect(url_for('validate'))

@app.route('/enviado', methods=['GET'])
def enviado():
    try:
        # Cargar datos desde validate_data.json
        validate_data_path = 'templates/validate_data.json'
        with open(validate_data_path, 'r') as file:
            validate_data = json.load(file)
        
        # Cargar datos desde no_sent_data.json
        validate_data_path_sent = 'templates/no_sent_data.json'
        with open(validate_data_path_sent, 'r') as file:
            validate_data_sent = json.load(file)
        
        return render_template('enviado.html', validate_data=validate_data, validate_data_sent=validate_data_sent)
    
    except Exception as e:
        # Manejo de errores (puedes personalizar este mensaje o redirigir a una página de error)
        return f"Error al cargar los datos: {e}"
   

if __name__ == '__main__':
    app.run(debug=True)