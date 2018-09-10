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

from constants import LABS, SPREADSHEET_ID

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

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
        if '_' in user['hacker'] and len(user['hacker'])>6 and user['hacker'][5] == '2' and user['hacker'][6] == '4':
            hacker = user['hacker'].split('_')[1]
            if hacker in alumnos_keys:
                timestamp = user['timestamp']

                if on_time(lab['start'], lab['end'], datetime.fromtimestamp(timestamp)):
                    alumnos[hacker][lab_id][0] = int(user['score'])
                alumnos[hacker][lab_id][1] = int(user['score'])
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
    lista_nalumnos = []
    alumnos = {}
    lab_keys = list(LABS.keys())
    lab_keys.sort()

#     Leer archivo
    with open('puntajes.csv', 'r') as csvfile:
        file = csv.reader(csvfile, delimiter=';')
        next(file)

        for row in file:
            puntajes = {}
            for i in range(0,11):
                inicial, actual = int(row[2 + 2*i-1]), int(row[2 + 2*i])

                puntajes[lab_keys[i]] = [inicial, actual]
            lista_nalumnos.append(row[0])
            alumnos[row[0]] = puntajes
#     Obtener puntajes
    for lab in LABS:
        alumnos = get_hackers(LABS[lab], alumnos)

#     Actualizar archivo
    with open('puntajes.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['n_alumno', 'l1_inicial', 'l1_actual', 'l2_inicial', 'l2_actual', 'l3_inicial', 'l3_actual', 'l4_inicial', 'l4_actual', 'l5_inicial', 'l5_actual', 'l6_inicial', 'l6_actual', 'l7_inicial', 'l7_actual', 'l8_inicial', 'l8_actual', 'l9_inicial', 'l9_actual', 'l10_inicial', 'l10_actual', 'l11_inicial', 'l11_actual'])
        for n_alumno in lista_nalumnos:
            row = [n_alumno]
            puntajes = alumnos[n_alumno]
            lab_keys = list(puntajes.keys())
            lab_keys.sort()
            for lab_key in lab_keys:
                row.append(puntajes[lab_key][0])
                row.append(puntajes[lab_key][1])
            writer.writerow(row)

#     Actualizar spreadsheet
    requests = []

    i=3
    requests.append({
        "pasteData": {
          "coordinate": { "rowIndex": 0, "columnIndex": 1},
          "data": 'Última actualización;{}'.format(date_time()),
          "delimiter": ";",
        },
    })
    requests.append({
        "pasteData": {
          "coordinate": { "rowIndex": 2, "columnIndex": 1},
          "data": 'número alumno;L1;L2;L3;L4;L5;L6;L7;L8;L9;L10;L11',
          "delimiter": ";",
        },
    })
    for n_alumno in lista_nalumnos:
        puntajes = alumnos[n_alumno]
        lab_keys = list(puntajes.keys())
        lab_keys.sort()
        
        s = '{};'.format(n_alumno)
        for lab_key in lab_keys:
            p_i, p_a = puntajes[lab_key]

            # Cálculo del puntaje
            s += '{};'.format(int(min(1200,p_i+(p_a - p_i)/2)))
        requests.append({
            "pasteData": {
              "coordinate": { "rowIndex": i, "columnIndex": 1},
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
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    actualizar(service)
