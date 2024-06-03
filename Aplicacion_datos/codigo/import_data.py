
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import json
import psycopg2
from config import config
from correo import enviar_correo

def read_csv_file(file_path):
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
    data_to_update = []  
    for json_entry in json_data:
        db_name = json_entry['db_name']
        user_id = json_entry['user_id']  
        db_class = json_entry['db_class']
        
        
        if user_id in csv_data:
            csv_entry = csv_data[user_id]
            user_state = csv_entry['user_state']
            user_manager = csv_entry['user_manager']
        
            combined_entry = {
                'db_name': db_name,
                'user_id': user_id,  
                'db_class': db_class,
                'user_state': user_state,
                'user_manager': user_manager
            }
            data_to_update.append(combined_entry)
           
    return data_to_update


def data_check(csv_data, json_data):
    data_check_result = []
             
    for json_entry in json_data:
        db_name = json_entry['db_name']
        user_id = json_entry['user_id']  
        db_class = json_entry['db_class']
    
        if user_id in csv_data:
            csv_entry = csv_data[user_id]
            user_state = csv_entry['user_state']
            user_manager = csv_entry['user_manager']
            
            combined = {
                'db_name': db_name,
                'user_id': user_id,
                'db_class': db_class,
                'user_state': user_state,
                'user_manager': user_manager
            }
            
            #data_check_result.append(data_check_result)  # Añade el diccionario combinado a data_check_result
        else:
            no_combined = {
                'db_name': db_name,
                'user_id': user_id,
                'db_class': db_class,  
            }
            
            data_check_result.append(no_combined) 
            
    return data_check_result

def insert_into_postgresql(data):
    connection = None  
    try:
    
        db_config = config(filename='data.ini', section='postgresql')
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'db_info')")
        table_exists = cursor.fetchone()[0]

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

  
        connection.commit()

    except Exception as e:
        print(f"Error al insertar o actualizar datos en PostgreSQL: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()

    

if __name__ == "__main__":
     
    json_validate_path = '/usr/src/app/templates/json/validate_data.json'
    json_no_sent_path = '/usr/src/app/templates/json/no_sent_data.json'
    csv_file_path = '/usr/src/app/data/info.csv'
    json_file_path = '/usr/src/app/data/datos.json'
    
    with open(json_validate_path, 'w') as file:
        json.dump([], file)
    with open(json_no_sent_path, 'w') as file:
        json.dump([], file)

    csv_data = read_csv_file(csv_file_path)
    json_data = read_json_file(json_file_path)

  
    combined_data = combine_data(csv_data, json_data)
   
    insert_into_postgresql(combined_data)  
        
    data_to_send = [
        {
            'db_name': item['db_name'],
            'db_class': item['db_class'],
            'user_manager': item['user_manager']
        }
        for item in combined_data if item['db_class'] == 'High'
    ]
        
    data_check_result = data_check(csv_data, json_data)

    data_check_result_sent = [
        {
            'db_name': item_sent['db_name'],
            'db_class': item_sent['db_class'],
            'user_id': item_sent['user_id']
        }
        for item_sent in data_check_result if item_sent['db_class'] == 'High'
    ]

     
    with open(json_validate_path, 'w') as file:
        json.dump(data_to_send, file)
    with open(json_no_sent_path, 'w') as file:
        json.dump(data_check_result_sent, file)
    

  
# ENVIO CORREO
    for dato in combined_data:
        if dato['db_class'] == 'High':
            mensaje_correo = f"De acuerdo a la información suministrada, la clasificación para la tabla {dato['db_name']} es crítica, por esta razón es necesario que envíe la respuesta con el OK de aprobación al E-mail: xxxx@meli.com"
            enviar_correo(dato['user_manager'], mensaje_correo)