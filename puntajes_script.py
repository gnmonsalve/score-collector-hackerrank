# Spreadsheet

from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# Scheduler
import atexit

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


from docopt import docopt
from tabulate import tabulate
from datetime import datetime
from functools import reduce

import requests as req
import json
import sys
import csv

SPREADSHEET_ID = '1NDcpn7vmAyWpu9h44DaMYsYMWPUgjmxkdkxAuCBwn3Y'
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
service = None

LABS = {
    'lab1': {
        'id': 'lab1',
        'link': 'iic1103-2018-1-lab1',
        'start': datetime(2018, 3, 17, 0),
        'end': datetime(2018, 3, 27, 15, 30)
        },
    'lab2': {
        'id': 'lab2',
        'link': 'iic1103-2018-1-lab2',
        'start': datetime(2018, 3, 20, 0),
        'end': datetime(2018, 4,  3, 15, 30)
        },
    'lab3': {
        'id': 'lab3',
        'link': 'iic1103-2018-1-lab3',
        'start': datetime(2018, 3, 20, 0),
        'end': datetime(2018, 4, 10, 15, 30)
        },
    'lab4': {
        'id': 'lab4',
        'link': 'iic1103-2018-1-lab4',
        'start': datetime(2018, 3, 20, 0),
        'end': datetime(2018, 4, 17, 15, 30)
        },
    'repaso-i1': {
        'id': 'repaso-i1',
        'link': 'iic1103-2018-1-repaso-i1',
        'start': datetime(2018, 4, 13, 0),
        'end': datetime(2018, 4, 24, 15, 30)
        },
    'lab5': {
        'id': 'lab5',
        'link': 'iic1103-2018-1-lab5',
        'start': datetime(2018, 3, 23, 0),
        'end': datetime(2018, 5, 1, 15, 30)
        },
    'lab6': {
        'id': 'lab6',
        'link': 'iic1103-2018-1-lab6',
        'start': datetime(2018, 3, 23, 0),
        'end': datetime(2018, 5, 8, 15, 30)
        },
    'lab7': {
        'id': 'lab7',
        'link': 'iic1103-2018-1-lab7',
        'start': datetime(2018, 4, 23, 0),
        'end': datetime(2018, 5, 15, 15, 30)
        },
    'repaso-i2': {
        'id': 'repaso-i2',
        'link': 'iic1103-2018-1-repaso-i2',
        'start': datetime(2018, 4, 13, 0),
        'end': datetime(2018, 5, 22, 15, 30)
        },
    'lab8': {
        'id': 'lab8',
        'link': 'iic1103-2018-1-lab8',
        'start': datetime(2018, 3, 23, 0),
        'end': datetime(2018, 5, 29, 0)
        },
    'lab9': {
        'id': 'lab9',
        'link': 'iic1103-2018-1-lab9',
        'start': datetime(2018, 3, 23, 0),
        'end': datetime(2018, 6, 5, 15, 30)
        },
    'lab10': {
        'id': 'lab10',
        'link': 'iic1103-2018-1-lab10',
        'start': datetime(2018, 3, 23, 0),
        'end': datetime(2018, 6, 12, 15, 30)
        },
    'lab11': {
        'id': 'lab11',
        'link': 'iic1103-2018-1-lab11',
        'start' : datetime(2018, 3, 23, 0),
        'end': datetime(2018, 6, 19, 15, 30)
        },
    # 'lab12': {
    #     'id': 'lab12',
    #     'link': 'iic1103-2018-1-lab12',
    #     'start' : datetime(2018, 3, 23, 0),
    #     'end': datetime(2018, 6, 26, 0)
    # },
}

def on_time(start, end, actual):
    return start <= actual <= end

def get_leadearboard(url):
    hackers = []

    finish = False
    offset = 0
    while not finish:
        res = req.get(url(offset,100))
        res = json.loads(res.text)

        _hackers = res['models']
        _page = res['page']

        # Filtar usuario, puntaje y timestamp
        hackers_filtered = [
            { k:v for k,v in _hacker.items() if k in ['hacker', 'score', 'timestamp']}
            for _hacker in _hackers
        ]
        hackers.extend(hackers_filtered)

        offset = _page * 100
        if (_page-1)*100 + len(_hackers) >= res['total']:
            finish = True
    return hackers

def assign_score(hackers, alumnos, lab):
    alumnos_keys = list(alumnos.keys())
    lab_id = lab['id']
    for user in hackers:
        if '_' in user['hacker'] and user['hacker'][3] == '1':
            hacker = user['hacker'].split('_')[1]

            if hacker in alumnos_keys:
                timestamp = user['timestamp']

                if on_time(lab['start'], lab['end'], datetime.fromtimestamp(timestamp)):
                    alumnos[hacker]['puntajes'][lab_id][0] = int(user['score'])
                alumnos[hacker]['puntajes'][lab_id][1] = int(user['score'])
    return alumnos

def get_hackers(lab, alumnos):
    url = (
        "https://www.hackerrank.com/rest/contests/"
        "{0}/"
        "leaderboard?offset={1}&limit={2}&_=1489594857572"
        )
    url2 = lambda offset,limit: url.format(lab['link'],offset,limit)

    hackers = get_leadearboard(url2)
    return assign_score(hackers, alumnos, lab)

def actualizar(service):
    print('===================================================================')
    print(date_time())
    alumnos = {}
    lab_keys = list(LABS.keys())


#     Leer archivo
    with open('puntajes.csv', 'r') as csvfile:
        file = csv.reader(csvfile, delimiter=';')
        next(file)

        for row in file:
            puntajes = {}

            for i in range(0,13):
                inicial, actual = int(row[2 + 2*i]), int(row[2 + 2*i + 1])

                puntajes[lab_keys[i]] = [inicial, actual]
            alumnos[row[1]] = {'n_alumno':row[0], 'user':row[1], 'puntajes': puntajes}
#     Obtener puntajes
    for lab in LABS:
        alumnos = get_hackers(LABS[lab], alumnos)

#     Actualizar archivo
    with open('puntajes.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['n_alumno', 'usuario', 'l1_inicial', 'l1_actual', 'l2_inicial', 'l2_actual', 'l3_inicial', 'l3_actual', 'l4_inicial', 'l4_actual', 'repaso1_inicial', 'repaso1_actual', 'l5_inicial', 'l5_actual', 'l6_inicial', 'l6_actual', 'l7_inicial', 'l7_actual', 'repaso2_inicial', 'repaso2_actual', 'l8_inicial', 'l8_actual', 'l9_inicial', 'l9_actual', 'l10_inicial', 'l10_actual', 'l11_inicial', 'l11_actual'])
        for alumno, value in alumnos.items():
            row = [value['n_alumno'],alumno]
            for lab_key in value['puntajes']:
                row.append(value['puntajes'][lab_key][0])
                row.append(value['puntajes'][lab_key][1])
            writer.writerow(row)

#     Actualizar spreadsheet
    requests = []

    i=2
    requests.append({
        "pasteData": {
          "coordinate": { "rowIndex": 0, "columnIndex": 2},
          "data": 'Última actualización: {}'.format(date_time()),
          "delimiter": ";",
        },
    })
    for alumno, value in alumnos.items():

        s = ''
        for lab_key in value['puntajes']:
            p_i, p_a = value['puntajes'][lab_key]
            s += '{};'.format(int(min(1200,p_i+(p_a - p_i)/2)))
        requests.append({
            "pasteData": {
              "coordinate": { "rowIndex": i, "columnIndex": 2},
              "data": s[:-1],
              "delimiter": ";",
            },
        })
        i+=1
    body = {
        'requests': requests
    }

    response = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                                   body=body).execute()

def date_time():
    return datetime.now()


if __name__ == '__main__':
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    actualizar(service)
