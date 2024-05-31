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
            result = subprocess.run(['python', script_path], capture_output=True, text=True)
            print("Salida estándar del proceso:")
            print(result.stdout)
            print("Salida de error del proceso:")
            print(result.stderr)
            if result.returncode == 0:
                # Si la ejecución es exitosa, procesa los datos y devuelve a la plantilla
                data = json.loads(result.stdout)
                print("salida")
                return render_template('validate.html', table_data=data)
            else:
                # Si hay un error, muestra un mensaje flash
                flash('Error al ejecutar el proceso de carga: ' + result.stderr)
        except Exception as e:
            flash('Error al ejecutar el proceso de carga: ' + str(e))

    # Renderiza la plantilla 'validate.html'
    return render_template('validate.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000, debug=True)
