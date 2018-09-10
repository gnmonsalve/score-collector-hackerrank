# Recolector de puntajes hackerrank

## Descripción
Este projecto tiene como objetivo automatizar la recolección y publicación de puntajes para los laboratorios del ramo IIC1103, desde [hackerrank](https://www.hackerrank.com).

El puntaje asignado a un alumno se calcula como pi + (pf-pi)/2, donde pi es el puntaje obtenido dentro del tiempo asignado para el laboratorio y pf el puntaje fuera de tiempo. Esto significa que los laboratorios pueden realizarse hasta fin de semestre, pero con la mitad del puntaje de los ejercicios realizados fuera de tiempo.

Este código está construido sobre https://github.com/mjjunemann/IIC1103-hacker-rank.
## Uso
1. Habilitar y crear credenciales para la API de Google Spreadsheets
  * Ir a la [consola de desarrolladores?](https://console.developers.google.com) y habilitar Google Sheets API.
  * Crear credenciales 'ID de cliente OAuth' y descargarlas. Guardar este archivo *credentials.json* y guardarlo en la carpeta del proyecto.

2. Crear una hoja de cálculo de Google, obtener su ID y agregarlo en el archivo *constants.py*.

  * Puedes obtener el `ID` desde el link:
`https://docs.google.com/spreadsheets/d/ID/edit#gid=0`
3. Actualizar la variable LABS en el archivo *constants.py*.
4. Crear el archivo *puntajes.csv*. En este archivo se almacenará el puntaje obtenido a tiempo (inicial) y fuera de tiempo (actual) para cada alumno. Se debe ver como:

```csv
n_alumno;l1_inicial;l1_actual;l2_inicial;l2_actual;...;l11_inicial;l11_actual
18XXXXX0;1200;1200;600;1200;...;0;0```
