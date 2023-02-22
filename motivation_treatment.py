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
        
        response_options = {
            1: 'Desacuerdo fuertemente',
            2: 'No estoy de acuerdo',
            3: 'Algo en desacuerdo',
            4: 'Neutral',
            5: 'Un poco de acuerdo',
            6: 'De acuerdo',
            7: 'Estoy muy de acuerdo'
        } 
        
        return {i+1: response_options[answers[i]] for i in range(19)}
                
    with connection_db().cursor() as cursor:
        try:
            sql = (f"SELECT answer_1, answer_2, answer_3, answer_4, answer_5, answer_6, answer_7, answer_8, answer_9, answer_10, answer_11, answer_12, answer_13, answer_14, answer_15, answer_16, answer_17, answer_18, answer_19, id_answers, user_id FROM answers_motivation_treatment WHERE user_id = %s")
            values = (id_user,)
            
            cursor.execute(sql, values)
            answers = cursor.fetchone()
            
            user_id = answers[-1]
            id_answers = answers[-2]
            
            dictionary_return = question_value(list(answers))
            dictionary_return['info_user'] = {'user_id': user_id,  'id_answers': id_answers}
            
            sql2 = (f"SELECT result FROM result_motivation_treatment WHERE answers_id = %s")
            values2 = (id_answers,)
            
            cursor.execute(sql2, values2)
            result = cursor.fetchone()
            
            intervention_alert = False
            total_score = int(result[0])        
            if total_score >= 68:
                intervention_alert = True
            
            dictionary_return['intervention_alert'] = intervention_alert
            
            return json.dumps(dictionary_return)
        
        except Exception as e:
            return json.dumps({'message': f'Error al consultar los datos: {e}'})

# print(get_answers(1))
    
def register_motivation_treatment(info_user:json)->json:
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
        "answer_9": 7,
        "answer_10": 5,
        "answer_11": 1,
        "answer_12": 2,
        "answer_13": 3,
        "answer_14": 1,
        "answer_15": 1,
        "answer_16": 1,
        "answer_17": 4,
        "answer_18": 6,
        "answer_19": 1}
        

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
            answer_5 = args['answer_5']
            answer_6 = args['answer_6']
            answer_7 = args['answer_7']
            answer_8 = args['answer_8']
            answer_9 = args['answer_9']
            answer_10 = args['answer_10']
            answer_11 = args['answer_11']
            answer_12 = args['answer_12']
            answer_13 = args['answer_13']
            answer_14 = args['answer_14']
            answer_15 = args['answer_15']
            answer_16 = args['answer_16']
            answer_17 = args['answer_17']
            answer_18 = args['answer_18']
            answer_19 = args['answer_19']

                
            answers = [answer_1, answer_2, answer_3, answer_4, answer_5, answer_6, answer_7, answer_8, answer_9, answer_10, answer_11, answer_12, answer_13, answer_14, answer_15, answer_16, answer_17, answer_18, answer_19]
            total_score = sum(answers)
                
            intervention_alert = False
            
            if total_score >= 10:
                intervention_alert = True
                
            try:
                sql = f"INSERT INTO answers_motivation_treatment (answer_1, answer_2, answer_3, answer_4, answer_5, answer_6, answer_7, answer_8, answer_9, answer_10, answer_11, answer_12, answer_13, answer_14, answer_15, answer_16, answer_17, answer_18, answer_19, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (answer_1, answer_2, answer_3, answer_4, answer_5, answer_6, answer_7, answer_8, answer_9, answer_10, answer_11, answer_12, answer_13, answer_14, answer_15, answer_16, answer_17, answer_18, answer_19, user_id)
                    
                cursor.execute(sql, values)
                answers_id = cursor.lastrowid
                
                sql2 = f"INSERT INTO result_motivation_treatment (result, user_id, answers_id) VALUES (%s, %s, %s)"
                values_2 = (total_score, user_id, answers_id)
                
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
                    "answer_10": answer_10,
                    "answer_11": answer_11,
                    "answer_12": answer_12,
                    "answer_13": answer_13,
                    "answer_14": answer_14,
                    "answer_15": answer_15,
                    "answer_16": answer_16,
                    "answer_17": answer_17,
                    "answer_18": answer_18,
                    "answer_19": answer_19,
                    "result_test": total_score,
                    "intervention_alert": intervention_alert
                })
            except:
                return json.dumps({
                    "message": "Error al insertar datos en la base de datos"
                })
        
        
"""
# parametros register_phq9()
dictionary = {"user_id": 1,
        "answer_1": 1,
        "answer_2": 3,
        "answer_3": 2,
        "answer_4": 1,
        "answer_5": 2,
        "answer_6": 3,
        "answer_7": 2,
        "answer_8": 1,
        "answer_9": 7,
        "answer_10": 5,
        "answer_11": 1,
        "answer_12": 2,
        "answer_13": 3,
        "answer_14": 1,
        "answer_15": 1,
        "answer_16": 1,
        "answer_17": 4,
        "answer_18": 6,
        "answer_19": 1}

print(register_motivation_treatment(json.dumps(dictionary)))"""


def delete_all_motivation_treatment(id_user:int)->json:
    """Elimina todos los formularios PHQ9 que realizó el usuario

    Args:
        id_user (int): id del usuario

    Returns:
        json: mensaje que indica que se eliminó correctamente el usuario de la base de datos o indica error
    """
    with connection_db() as conn:
        with conn.cursor() as cursor:
    
            try:
                sql = f"DELETE FROM result_motivation_treatment WHERE user_id = %s"
                values = (id_user,)
                    
                cursor.execute(sql, values)
                
                sql2 = f"DELETE FROM answers_motivation_treatment WHERE user_id = %s"
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


# print(delete_all_motivation_treatment(1))


def delete_one_motivation_treatment(info_user:json)->json:
    
    args = json.loads(info_user)
    with connection_db() as conn:
        with conn.cursor() as cursor:
            id_user = args['user_id']
            id_answers = args['id_answers']
            id_result = args['id_result']
            
            try: 
                sql = f"DELETE FROM result_motivation_treatment WHERE user_id = %s AND id_result = %s"
                values = (id_user, id_result)
                
                    
                cursor.execute(sql, values)
                
                sql_2 = f"DELETE FROM answers_motivation_treatment WHERE user_id = %s AND id_answers = %s"
                values_2 = (id_user,id_answers)
                
                cursor.execute(sql_2, values_2)
                
                conn.commit()
                
                return json.dumps({
                    "message": "se eliminaron correctamente los registros y resultados de la escala PHQ9"
                })
            
            except:
                return json.dumps({
                    "message": "No se pudieron eliminar los registros y resultados de la escala PHQ9"
                })
                

"""
# parametros delete_one_phq9()

parameters_delete_one_motivation_treatment = {'user_id': 1,
                                        'id_answers': 7,
                                        'id_result': 7}

print(delete_one_motivation_treatment(json.dumps(parameters_delete_one_motivation_treatment)))"""
