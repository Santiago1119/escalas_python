import pymysql
import json
from numpy import mean
from connection_db import connection_db

def get_answers(id_user:int)->json:
    """Consulta las respuestas del usuario en la base de datos

    Args:
        id_user (int): id del usuario del cual se requieren las respuestas

    Returns:
        json: formato json con las respuestas del formulario
    """
                
    with connection_db().cursor() as cursor:
        try:
            sql = (f"SELECT answer_1, answer_2, answer_3, answer_4, id_answers, user_id FROM answers_efficacy WHERE user_id = %s")
            values = (id_user,)
            
            cursor.execute(sql, values)
            answers = cursor.fetchone()
            
            user_id = answers[-1]
            id_answers = answers[-2]
            values_answers = answers[0:4]
            
            dictionary_return = {}
            dictionary_return['info_user'] = {'user_id': user_id,  'id_answers': id_answers}
            dictionary_return['answers'] = values_answers
            
            sql2 = (f"SELECT result FROM result_efficacy WHERE answers_id = %s")
            values2 = (id_answers,)
            
            cursor.execute(sql2, values2)
            result = cursor.fetchone()
            
            intervention_alert = False
            total_score = int(result[0])        
            if total_score <= 7:
                intervention_alert = True
            
            dictionary_return['intervention_alert'] = intervention_alert
            
            return json.dumps(dictionary_return)
        
        except Exception as e:
            return json.dumps({'message': f'Error al consultar los datos: {e}'})

# print(get_answers(5))
    
def register_self_efficacy(info_user:json)->json:
    """Ingresa en la base de datos la información ingresada en formato json con dos query(SQL) para dos tablas distintas, una almacena el resultado y la otra almacena las respuestas del usuario

    Args:
        dictionary (json): archivo json con la siguiente estructura: 
        
        {"user_id": 8,
        "answer_1": 1,
        "answer_2": 3,
        "answer_3": 2,
        "answer_4": 1
        }
        

    Returns:
        json: json con la información ingresada a la base de datos
    """
    args = json.loads(info_user)
    with connection_db() as conn:
        with conn.cursor() as cursor:
            
            user_id = args['user_id']
            answer_1 = args['answer_1']
            answer_2 = args['answer_2']
            answer_3 = args['answer_3']
            answer_4 = args['answer_4']

                
            answers = [answer_1, answer_2, answer_3, answer_4]
            total_score = mean(answers)
                
            intervention_alert = False
            
            if total_score <= 7:
                intervention_alert = True
                
            try:
                sql = f"INSERT INTO answers_efficacy (answer_1, answer_2, answer_3, answer_4, user_id) VALUES (%s, %s, %s, %s, %s)"
                values = (answer_1, answer_2, answer_3, answer_4, user_id)
                    
                cursor.execute(sql, values)
                answers_id = cursor.lastrowid
                
                sql2 = f"INSERT INTO result_efficacy (result, user_id, answers_id) VALUES (%s, %s, %s)"
                values_2 = (total_score, user_id, answers_id)
                
                cursor.execute(sql2, values_2)
                
                conn.commit()
                    
                return json.dumps({
                    "id_user": user_id,
                    "answer_1": answer_1,
                    "answer_2": answer_2,
                    "answer_3": answer_3,
                    "answer_4": answer_4,
                    "result_test": total_score,
                    "intervention_alert": intervention_alert
                })
            except Exception as e:
                return json.dumps({
                    "message": f"Error al insertar datos en la base de datos {e}"
                })
        
        

# parametros register_rosenberg()
dictionary = {"user_id": 3,
        "answer_1": 10,
        "answer_2": 10,
        "answer_3": 2,
        "answer_4": 7
        }

print(register_self_efficacy(json.dumps(dictionary)))