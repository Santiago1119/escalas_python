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
            1: 'Totalmente en desacuerdo',
            2: 'En desacuerdo',
            3: 'Ni de acuerdo ni en desacuerdo',
            4: 'De acuerdo',
            5: 'Totalmente de acuerdo'
        }

        return {i+1: response_options[answers[i]] for i in range(10)}
                
    with connection_db().cursor() as cursor:

        try:
            sql = (f"SELECT answer_1, answer_2, answer_3, answer_4, answer_5, answer_6, answer_7, answer_8, answer_9, answer_10, date, id_answers, doctor_id FROM answers_bmq WHERE user_id = %s AND date = %s")  
            value = (id_user, date)
            
            cursor.execute(sql, value)
            answers = cursor.fetchone()
            
            doctor_id = answers[-1]
            id_answers = answers[-2]
            
            dictionary_return = question_value(answers)
            dictionary_return['info_user'] = {'user_id': id_user,  'id_answers': id_answers}
            
            sql_2 = (f"SELECT need_items, preocupation_items FROM result_bmq WHERE answers_id = %s")
            values2 = (id_answers,)
            
            cursor.execute(sql_2, values2)
            result = cursor.fetchone()
            
            need_items = result[-2]
            preocupation_items = result[-1]
            
            intervention_alert = False
            
            if need_items >= 13 or preocupation_items >= 13:
                intervention_alert = True
            
            dictionary_return['intervention_alert'] = intervention_alert
            dictionary_return['doctor_id'] = doctor_id    
            dictionary_return['date'] = date
            
            return json.dumps(dictionary_return)
        except Exception as e:
            return json.dumps({'message': f'Error al consultar los datos: {e}'})

# print(get_answers(5, '2023-02-23 21:30:00'))
    
def register_phq9(info_user:json)->json:
    """Ingresa en la base de datos la información ingresada en formato json con dos query(SQL) para dos tablas distintas, una almacena el resultado y la otra almacena las respuestas del usuario

    Args:
        dictionary (json): archivo json con la siguiente estructura: 
        
        {"user_id": 1,
        "doctor_id": 1,
        "answer_1": 3,
        "answer_2": 3,
        "answer_3": 2,
        "answer_4": 1,
        "answer_5": 2,
        "answer_6": 1,
        "answer_7": 2,
        "answer_8": 3,
        "answer_9": 4,
        "answer_10": 5
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
            answer_6 = args['answer_6']
            answer_7 = args['answer_7']
            answer_8 = args['answer_8']
            answer_9 = args['answer_9']
            answer_10 = args['answer_10']
                 
            need_items = [answer_1, answer_3, answer_5, answer_7, answer_10]
            preocupation_items = [answer_2, answer_4, answer_6, answer_8, answer_9]
            
            need_items_sumatory = sum(need_items)
            preocupation_items_sumatory = sum(preocupation_items)
            
            intervention_alert = False
            
            if need_items_sumatory >= 13 or preocupation_items_sumatory >= 13:
                intervention_alert = True
            
            from_zone = tz.gettz('UTC')
            to_zone = tz.gettz('America/Bogota')
            date = datetime.utcnow()
            date = date.replace(tzinfo=from_zone)
            date = date.astimezone(to_zone)
            date = date.strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                sql = f"INSERT INTO answers_bmq (answer_1, answer_2, answer_3, answer_4, answer_5, answer_6, answer_7, answer_8, answer_9, answer_10, date, doctor_id, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (answer_1, answer_2, answer_3, answer_4, answer_5, answer_6, answer_7, answer_8, answer_9, answer_10, date, doctor_id, user_id)
                    
                cursor.execute(sql, values)
                answers_id = cursor.lastrowid
                
                sql_2 = f"INSERT INTO result_bmq (need_items, preocupation_items, user_id, answers_id) VALUES (%s, %s, %s, %s)"
                values_2 = (need_items_sumatory, preocupation_items_sumatory ,user_id, answers_id)
                
                cursor.execute(sql_2, values_2) 
                conn.commit()
                
                    
                return json.dumps({
                    "id_user": user_id,
                    "answer_1": answer_1,
                    "answer_2": answer_2,
                    "answer_3": answer_3,
                    "answer_4": answer_4,
                    "answer_5": answer_5,
                    "answer_6": answer_6,
                    "answer_7": answer_7,
                    "answer_8": answer_8,
                    "answer_9": answer_9,
                    "answer_10": answer_10,
                    "doctor_id": doctor_id,
                    "need_items": need_items_sumatory,
                    "preocupation_items": preocupation_items_sumatory,
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
        "answer_2": 3,
        "answer_3": 2,
        "answer_4": 1,
        "answer_5": 2,
        "answer_6": 3,
        "answer_7": 2,
        "answer_8": 1,
        "answer_9": 3,
        "answer_10": 5
        }

print(register_phq9(json.dumps(dictionary)))"""