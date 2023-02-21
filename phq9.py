import pymysql
import json
from connection_db import connection_db

def get_answers(id_user:int)->json:
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
        
        user_responses = {}
        for answer in range(0, 9):
            position_question = answer + 1
            
            if answers[answer] == 0:
                user_responses[position_question] = 'Ningun dia'
            elif answers[answer] == 1:
                user_responses[position_question] = 'Varios dias'    
            elif answers[answer] == 2:
                user_responses[position_question] = 'Mas de la mitad de los dias' 
            elif answers[answer] == 3:
                user_responses[position_question] = 'Casi todos los dias' 
        
        return user_responses
                
    with connection_db().cursor() as cursor:

        cursor.execute(f"SELECT answer_1, answer_2, answer_3, answer_4, answer_5, answer_6, answer_7, answer_8, answer_9, id_answers, user_id FROM answers_phq9 WHERE user_id = {id_user}")
        
        answers = cursor.fetchone()
        
        dictionary_return = question_value(list(answers))
        dictionary_return['info_user'] = {'user_id': list(answers)[-1],  'id_answers': list(answers)[-2]}
        
        return json.dumps(dictionary_return)
    
    
def register_phq9(info_user:json)->json:
    """Ingresa en la base de datos la información ingresada en formato json con dos query(SQL) para dos tablas distintas, una almacena el resultado y la otra almacena las respuestas del usuario

    Args:
        dictionary (json): archivo json con la siguiente estructura: 
        
        {"user_id": 8,
        "answer_1": 1,
        "answer_2": 3,
        "answer_3": 2,
        "answer_4": 1,
        "answer_5": 2,
        "answer_6": 3,
        "answer_7": 2,
        "answer_8": 1,
        "answer_9": 0}
        

    Returns:
        json: json con la información
    """
    args = json.loads(info_user)
    with connection_db() as conn:
        with conn.cursor() as cursor:
            
            user_id = args['user_id']
            answer_1 = args['answer_1']
            answer_2 = args['answer_2']
            answer_3 = args['answer_3']
            answer_4 = args['answer_4']
            answer_5 = args['answer_5']
            answer_6 = args['answer_6']
            answer_7 = args['answer_7']
            answer_8 = args['answer_8']
            answer_9 = args['answer_9']
                
                
            answers = [answer_1, answer_2, answer_3, answer_4, answer_5, answer_6, answer_7, answer_8, answer_9]
            total_score = sum(answers)
                
                
            try:
                sql = f"INSERT INTO answers_phq9 (answer_1, answer_2, answer_3, answer_4, answer_5, answer_6, answer_7, answer_8, answer_9, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (answer_1, answer_2, answer_3, answer_4, answer_5, answer_6, answer_7, answer_8, answer_9, user_id)
                    
                cursor.execute(sql, values)
                
                sql2 = f"INSERT INTO result_phq9 (result, user_id) VALUES (%s, %s)"
                values_2 = (total_score, user_id)
                
                cursor.execute(sql2, values_2)
                
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
                    "result_test": total_score
                })
            except:
                return json.dumps({
                    "message": "Error al insertar datos en la base de datos"
                })
        
        
"""
parametros register_phq9()
dictionary = {"user_id": 5,
        "answer_1": 1,
        "answer_2": 3,
        "answer_3": 2,
        "answer_4": 1,
        "answer_5": 2,
        "answer_6": 3,
        "answer_7": 2,
        "answer_8": 1,
        "answer_9": 0}

print(register_phq9(json.dumps(dictionary)))"""


def delete_all_phq9(id_user:int)->json:
    """Elimina todos los formularios PHQ9 que realizó el usuario

    Args:
        id_user (int): id del usuario

    Returns:
        json: mensaje que indica que se eliminó correctamente el usuario de la base de datos o indica error
    """
    with connection_db() as conn:
        with conn.cursor() as cursor:
    
            try:
                sql = f"DELETE FROM answers_phq9 WHERE user_id = %s"
                values = (id_user,)
                    
                cursor.execute(sql, values)
                
                sql2 = f"DELETE FROM result_phq9 WHERE user_id = %s"
                values_2 = (id_user,)
                
                cursor.execute(sql2, values_2)
                
                conn.commit()
                    
                return json.dumps({
                    "se eliminaron las respuestas del usuario": id_user
                })
            except:
                return json.dumps({
                    "message": "Error al eliminar datos en la base de datos"
                })


# print(delete_all_phq9(3))


def delete_one_phq9(info_user:json)->json:
    
    args = json.loads(info_user)
    with connection_db() as conn:
        with conn.cursor() as cursor:
            id_user = args['user_id']
            id_answers = args['id_answers']
            id_result = args['id_result']
            
            try: 
                sql = f"DELETE FROM answers_phq9 WHERE user_id = %s AND id_answers = %s"
                values = (id_user,id_answers)
                    
                cursor.execute(sql, values)
                
                sql2 = f"DELETE FROM result_phq9 WHERE user_id = %s AND id_result = %s"
                values_2 = (id_user, id_result)
                
                cursor.execute(sql2, values_2)
                
                conn.commit()
                
                return json.dumps({
                    "message": "se eliminaron correctamente los registros y resultados de la escala PHQ9"
                })
            
            except:
                return json.dumps({
                    "message": "No se pudieron eliminar los registros y resultados de la escala PHQ9"
                })

"""
parametros delete_one_phq9()

parameters_delete_one_phq9 = {'user_id': 5,
                                'id_answers': 20,
                                'id_result': 3}

print(delete_one_phq9(json.dumps(parameters_delete_one_phq9)))"""