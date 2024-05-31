import csv
import json
import psycopg2
from config import config  # Asegúrate de tener este archivo configurado correctamente

def read_csv_file(file_path):
    """Lee un archivo CSV y devuelve los datos como un diccionario."""
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file, delimiter=';')
        csv_data = {row['user_id']: row for row in reader}
        print("Datos del archivo CSV:", csv_data)
        return csv_data

def read_json_file(file_path):
    """Lee un archivo JSON y devuelve los datos como una lista de diccionarios."""
    with open(file_path, 'r') as file:
        json_data = json.load(file)
        print("Datos del archivo JSON:", json_data)
        return json_data

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
    try:
        # Obtener la configuración de la base de datos desde data.ini
        db_config = config(filename='data.ini', section='postgresql')

        # Establecer la conexión a la base de datos
        connection = psycopg2.connect(**db_config)
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

    except psycopg2.Error as e:
        print(f"Error al insertar o actualizar datos en PostgreSQL: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    # Especifica las rutas de los archivos CSV y JSON
    csv_file_path = 'C:\Users\Juli-Edd\Documents\challenge\Aplicacion_datos\flask\src\data\info.csv'
    json_file_path = 'C:\Users\Juli-Edd\Documents\challenge\Aplicacion_datos\flask\src\data\datos.json'

    # Lee los datos del archivo CSV y JSON
    csv_data = read_csv_file(csv_file_path)
    json_data = read_json_file(json_file_path)

    # Combinar los datos
    combined_data = combine_data(csv_data, json_data)
    print("Datos combinados:", combined_data)  # Imprimir el diccionario de datos combinados para verificar

    # Insertar los datos combinados en PostgreSQL
    insert_into_postgresql(combined_data)
