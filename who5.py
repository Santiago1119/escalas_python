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

    def question_value(answers:list)->dict:
        """Trasforma la información de la base de datos en las respuestas en texto del usuario

        Args:
            answers (list): valores registrados en la base de datos

        Returns:
            dict: diccionario con el número de la pregunta y lo que respondió
        """
        
        response_options = {
            0: 'Nunca',
            1: 'De vez en cuando',
            2: 'Menos de la mitad del tiempo',
            3: 'Mas de la mitad del tiempo',
            4: 'La mayor parte del tiempo',
            5: 'Todo el tiempo'
        }

        return {i+1: response_options[answers[i]] for i in range(5)}
                
    with connection_db().cursor() as cursor:

        try:
            sql = (f"SELECT answer_1, answer_2, answer_3, answer_4, answer_5, date, id_answers, doctor_id, user_id FROM answers_who5 WHERE user_id = %s AND date = %s")  
            value = (id_user, date)
            
            cursor.execute(sql, value)
            answers = cursor.fetchone()
            
            user_id = answers[-1]
            doctor_id = answers[-2]
            id_answers = answers[-3]
            values_answers = answers[0:4]
             
            dictionary_return = question_value(answers)
            dictionary_return['info_user'] = {'user_id': user_id,  'id_answers': id_answers}
            
            sql_2 = (f"SELECT result FROM result_who5 WHERE answers_id = %s")
            values2 = (id_answers,)
            
            cursor.execute(sql_2, values2)
            result = cursor.fetchone()
            
            total_score = int(result[0])
            intervention_alert = False
            
            if total_score <= 13 or 0 in values_answers or 1 in values_answers:
                intervention_alert = True
            
            dictionary_return['intervention_alert'] = intervention_alert
            dictionary_return['doctor_id'] = doctor_id    
            dictionary_return['date'] = date
            
            return json.dumps(dictionary_return)
        except Exception as e:
            return json.dumps({'message': f'Error al consultar los datos: {e}'})

# print(get_answers(5, '2023-02-23 13:27:19'))
    
def register_who5(info_user:json)->json:
    """Ingresa en la base de datos la información ingresada en formato json con dos query(SQL) para dos tablas distintas, una almacena el resultado y la otra almacena las respuestas del usuario

    Args:
        dictionary (json): archivo json con la siguiente estructura: 
        
        {"user_id": 8,
        "doctor_id": 1,
        "answer_1": 2,
        "answer_2": 4,
        "answer_3": 5,
        "answer_4": 5,
        "answer_5": 0
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
            answer_5 = args['answer_5']
                
            answers = [answer_1, answer_2, answer_3, answer_4, answer_5]
            total_score = sum(answers) * 4
            
            intervention_alert = False
            
            if total_score <= 13 or 0 in answers or 1 in answers:
                intervention_alert = True
            
            from_zone = tz.gettz('UTC')
            to_zone = tz.gettz('America/Bogota')
            date = datetime.utcnow()
            date = date.replace(tzinfo=from_zone)
            date = date.astimezone(to_zone)
            date = date.strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                sql = f"INSERT INTO answers_who5 (answer_1, answer_2, answer_3, answer_4, answer_5, date, doctor_id, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                values = (answer_1, answer_2, answer_3, answer_4, answer_5, date, doctor_id, user_id)
                    
                cursor.execute(sql, values)
                answers_phq9_id = cursor.lastrowid
                
                sql_2 = f"INSERT INTO result_who5 (result, user_id, answers_id) VALUES (%s, %s, %s)"
                values_2 = (total_score, user_id, answers_phq9_id)
                
                cursor.execute(sql_2, values_2) 
                conn.commit()
                
                    
                return json.dumps({
                    "id_user": user_id,
                    "answer_1": answer_1,
                    "answer_2": answer_2,
                    "answer_3": answer_3,
                    "answer_4": answer_4,
                    "answer_5": answer_5,
                    "doctor_id": doctor_id,
                    "date": date,
                    "result_test": total_score,
                    "intervention_alert": intervention_alert
                })
            except Exception as e:
                return json.dumps({
                    "message": f"Error al insertar datos en la base de datos: {e}"
                })
        
"""
dictionary = {"user_id": 5,
        "doctor_id": 1,
        "answer_1": 2,
        "answer_2": 4,
        "answer_3": 3,
        "answer_4": 4,
        "answer_5": 5
        }

print(register_who5(json.dumps(dictionary)))"""