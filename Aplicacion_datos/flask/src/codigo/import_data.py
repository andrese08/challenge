import csv
import json
import psycopg2
from config import config
from correo import enviar_correo

def read_csv_file(file_path):
    """Lee un archivo CSV y devuelve los datos como un diccionario."""
    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file, delimiter=';')
            csv_data = {row['user_id']: row for row in reader}
            print("Datos del archivo CSV:", csv_data)
            return csv_data
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return {}

import json

def read_json_file(file_path):
    """Lee un archivo JSON y devuelve los datos como una lista de diccionarios."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            if not json_data:
                print("El archivo JSON está vacío.")
            else:
                print("Datos del archivo JSON:", json_data)
            return json_data
    except json.JSONDecodeError as e:
        print(f"Error al leer el archivo JSON: {e}")
        return []
    except Exception as e:
        print(f"Error al abrir el archivo JSON: {e}")
        return []



def combine_data(csv_data, json_data):
    """Combina datos del archivo CSV y JSON."""
    data_to_update = []  # Lista para almacenar los datos combinados
    for json_entry in json_data:
        db_name = json_entry['db_name']
        user_id = json_entry['user_id']  # Mantener user_id como cadena
        db_class = json_entry['db_class']
        
        # Verificar si el user_id está en el CSV
        if user_id in csv_data:
            csv_entry = csv_data[user_id]
            user_state = csv_entry['user_state']
            user_manager = csv_entry['user_manager']
            
            # Crear entrada combinada
            combined_entry = {
                'db_name': db_name,
                'user_id': user_id,  # user_id como cadena
                'db_class': db_class,
                'user_state': user_state,
                'user_manager': user_manager
            }
            # Agregar entrada combinada a la lista de datos para actualizar
            data_to_update.append(combined_entry)
            print("Entrada combinada:", combined_entry)  # Verificar la entrada combinada
            
    return data_to_update



def insert_into_postgresql(data):
    """Inserta o actualiza los datos en una base de datos PostgreSQL."""
    connection = None  # Definir la variable connection
    try:
        # Obtener la configuración de la base de datos desde data.ini
        db_config = config(filename='data.ini', section='postgresql')

        # Establecer la conexión a la base de datos
        connection = psycopg2.connect(**db_config)

        """db_config = {
            'host': 'localhost',
            'database': 'melidb',
            'user': 'meli',
            'password': 'p4ssw0rd',
            'port': '5454'
    
        }"""
        cursor = connection.cursor()

        # Verificar si la tabla existe
        cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'db_info')")
        table_exists = cursor.fetchone()[0]

        # Crear la tabla si no existe
        if not table_exists:
            cursor.execute("""
                CREATE TABLE db_info (
                    db_name VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255),
                    db_class VARCHAR(255),
                    user_state VARCHAR(255),
                    user_manager VARCHAR(255)
                )
            """)
            connection.commit()
            print("Tabla creada exitosamente.")

        # Insertar o actualizar datos en la tabla
        for entry in data:
            cursor.execute("""
                INSERT INTO db_info (db_name, user_id, db_class, user_state, user_manager)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (db_name)
                DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    db_class = EXCLUDED.db_class,
                    user_state = EXCLUDED.user_state,
                    user_manager = EXCLUDED.user_manager
            """, (
                entry['db_name'],
                entry['user_id'],
                entry['db_class'],
                entry['user_state'],
                entry['user_manager']
            ))

        # Confirmar los cambios
        connection.commit()

    except Exception as e:
        print(f"Error al insertar o actualizar datos en PostgreSQL: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()

    

if __name__ == "__main__":
       # Ruta del archivo JSON a actualizar
    json_validate_path = 'C:/Users/Juli-Edd/Documents/challenge/Aplicacion_datos/flask/src/templates/validate_data.json'

    # Borrar los valores almacenados en el archivo JSON
    with open(json_validate_path, 'w') as file:
        json.dump([], file)

    print("Valores del archivo JSON borrados correctamente.")

    # Especifica las rutas de los archivos CSV y JSON
    csv_file_path = 'C:/Users/Juli-Edd/Documents/challenge/Aplicacion_datos/flask/src/data/info.csv'
    json_file_path = 'C:/Users/Juli-Edd/Documents/challenge/Aplicacion_datos/flask/src/data/datos.json'

    # Lee los datos del archivo CSV y JSON
    csv_data = read_csv_file(csv_file_path)
    json_data = read_json_file(json_file_path)

    # Combinar los datos
    combined_data = combine_data(csv_data, json_data)
    print("Datos combinados:", combined_data)  # Imprimir el diccionario de datos combinados para verificar

    # test del filtro
    # Extraer los campos deseados y crear el nuevo diccionario data_to_send solo si db_class es 'High'
    data_to_send = [
        {
            'db_name': item['db_name'],
            'db_class': item['db_class'],
            'user_manager': item['user_manager']
        }
        for item in combined_data if item['db_class'] == 'High'
    ]
    print("ESTA ES LA VERDADERA DATA PARA ENVIAR", data_to_send)

    # Insertar los datos combinados en PostgreSQL
    insert_into_postgresql(combined_data)

    # Ruta del archivo JSON donde se guardarán los datos
    json_file_path = 'C:/Users/Juli-Edd/Documents/challenge/Aplicacion_datos/flask/src/templates/validate_data.json'

    # Crear una lista de diccionarios con los campos específicos
    data_to_save = [{'db_name': entry['db_name'], 'db_class': entry['db_class'], 'user_manager': entry['user_manager']} for entry in combined_data]

    # Guardar los datos en el archivo JSON
    with open(json_file_path, 'w') as file:
        json.dump(data_to_send, file)

    print("Datos guardados correctamente en el archivo JSON.")

    # Imprimir datos combinados en formato JSON para ser capturados por Flask
    print(json.dumps(combined_data), "salida JSON")


    # Validación de db_class y envío de correo electrónico
    """for dato in combined_data:
        if dato['db_class'] == 'High':
            mensaje_correo = f"De acuerdo a la información suministrada, la clasificación para la tabla {dato['db_name']} es crítica, por esta razón es necesario que envíe la respuesta con el OK de aprobación al E-mail: xxxx@meli.com"
            enviar_correo(dato['user_manager'], mensaje_correo)"""