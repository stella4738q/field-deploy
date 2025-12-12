import requests
from bs4 import BeautifulSoup


def STR_to_NUM(data):
    line = tuple(data.split(',')) #註1
    num1 = float(line[1])
    num2 = float(line[2])
    line = [num1, num2]
    return line


def coordination(url):
    response = requests.get(url)
    # soup = BeautifulSoup(response.text, "html.parser")
    text = response.text
    initial_pos = text.find(";window.APP_INITIALIZATION_STATE")
    #尋找;window.APP_INITIALIZATION_STATE所在位置
    data = text[initial_pos+36:initial_pos+85] #將其後的參數進行存取
    num_data = STR_to_NUM(data)
    return num_data
