from connection_db import connection_db
from datetime import datetime, date
from dateutil import tz

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

tuple = (1, 3, 2, 1, 2, 3, 2, 1, 0, 5, datetime(2023, 2, 23, 20, 54, 6), 3, 1)
print(question_value(tuple))