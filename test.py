import json

def dictionary_generator(stream: list[str], delimiter="<END>"):
    buffer = ''
    
    for chunk in stream:
        if delimiter not in chunk:
            buffer+=chunk
        else:
            yield buffer + chunk.split(delimiter)[0]
            buffer = chunk.split(delimiter)[1]
        
# Пример использования генератора
if __name__ == "__main__":
    # Пример потока данных с неполными словарями
    packets = ['{"1": "cxv" ,', 
               '"2": "cxv"}<END>{', 
               '"3": "cxv"}<END>']

    for dictionary in dictionary_generator(packets):
        print(json.loads(dictionary))  # Выводит полные словари
