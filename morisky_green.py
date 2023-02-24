import pymysql
import json
from connection_db import connection_db
from datetime import datetime, date
from dateutil import tz

def get_answers(id_user:int, date:str)->json:
    """Consulta las respuestas del usuario en la base de datos

    Args:
        id_user (int): id del usuario del cual se requieren las respuestas

    Returns:
        json: formato json con las respuestas del formulario
    """
                
    with connection_db().cursor() as cursor:

        try:
            sql = (f"SELECT answer_1, answer_2, answer_3, answer_4, date, id_answers, doctor_id FROM answers_morisky_green WHERE user_id = %s AND date = %s")  
            value = (id_user, date)
            
            cursor.execute(sql, value)
            answers = cursor.fetchone()
            
            doctor_id = answers[-1]
            id_answers = answers[-2]
            values_answers = answers[0:4]
            values_answers = [False if answer == 0 else True for answer in values_answers]
            
            dictionary_return = {}
            dictionary_return['answers'] = values_answers
            dictionary_return['info_user'] = {'user_id': id_user,  'id_answers': id_answers}
            
            sql_2 = (f"SELECT result FROM result_morisky_green WHERE answers_id = %s")
            values2 = (id_answers,)
            
            cursor.execute(sql_2, values2)
            result = cursor.fetchone()
            intervention_alert = False if result[0] == 0 else True
            
            dictionary_return['intervention_alert'] = intervention_alert
            dictionary_return['doctor_id'] = doctor_id    
            dictionary_return['date'] = date
            
            return json.dumps(dictionary_return)
        except Exception as e:
            return json.dumps({'message': f'Error al consultar los datos: {e}'})

# print(get_answers(5, '2023-02-23 16:15:46'))
    
def register_who5(info_user:json)->json:
    """Ingresa en la base de datos la información ingresada en formato json con dos query(SQL) para dos tablas distintas, una almacena el resultado y la otra almacena las respuestas del usuario

    Args:
        dictionary (json): archivo json con la siguiente estructura: 
        
        {"user_id": 3,
        "doctor_id": 1,
        "answer_1": 1,
        "answer_2": 0,
        "answer_3": 1,
        "answer_4": 1
        }
        

    Returns:
        json: json con la información
    """
    args = json.loads(info_user)
    with connection_db() as conn:
        with conn.cursor() as cursor:
            
            user_id = args['user_id']
            doctor_id = args['doctor_id']
            answer_1 = args['answer_1']
            answer_2 = args['answer_2']
            answer_3 = args['answer_3']
            answer_4 = args['answer_4']
                
            answers = [answer_1, answer_2, answer_3, answer_4]
            answers = [False if answer == 0 else True for answer in answers]
            
            expected_values = [False, True, False, False]
            intervention_alert = 1 if any([answer != expected for answer, expected in zip(answers, expected_values)]) else 0
            
            
            from_zone = tz.gettz('UTC')
            to_zone = tz.gettz('America/Bogota')
            date = datetime.utcnow()
            date = date.replace(tzinfo=from_zone)
            date = date.astimezone(to_zone)
            date = date.strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                sql = f"INSERT INTO answers_morisky_green (answer_1, answer_2, answer_3, answer_4, date, doctor_id, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                values = (answer_1, answer_2, answer_3, answer_4, date, doctor_id, user_id)
                    
                cursor.execute(sql, values)
                answers_id = cursor.lastrowid
                
                sql_2 = f"INSERT INTO result_morisky_green (result, user_id, answers_id) VALUES (%s, %s, %s)"
                values_2 = (intervention_alert, user_id, answers_id)
                
                cursor.execute(sql_2, values_2) 
                conn.commit()
                
                    
                return json.dumps({
                    "id_user": user_id,
                    "answer_1": answer_1,
                    "answer_2": answer_2,
                    "answer_3": answer_3,
                    "answer_4": answer_4,
                    "doctor_id": doctor_id,
                    "date": date,
                    "intervention_alert": intervention_alert
                })
            except Exception as e:
                return json.dumps({
                    "message": f"Error al insertar datos en la base de datos: {e}"
                })
        
"""
dictionary = {"user_id": 5,
        "doctor_id": 1,
        "answer_1": 1,
        "answer_2": 0,
        "answer_3": 0,
        "answer_4": 0
        }

print(register_who5(json.dumps(dictionary)))"""