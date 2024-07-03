# TESTs del proyecto

Divididos en

## Unitarios (Automáticos)

Tests que validan la estructura del código para ver su robustez. Recorren cada posible situación para ver si ocurre lo deseado

```sh
#Para ejecutar
./run_unitary.sh
```

## Integración

Notebooks en los que se verifica la funcionalidad de los elementos del código. Si en los unitarios verificabamos con una operación daba un texto, aqui verificamos la correctitud semántica de dicho texto.

Es por ello que la mayoría de tests de integración son binarios: o funcionan o no funcionan.

### Tiempos y Calidad de la respuesta

Dentro de los tests de integración se incluyen unas pruebas donde se cuantifica la velocidad que tarda el chat en responder (en base a su nivel de precisión) frente a la calidad de texto obtenido.

## Usabilidad

Se presenta un frontend mockeado con el que pueden interactuar los usuarios para tener acceso a las funcionalidades del bot.

Se presentan una serie de preguntas, respuestas y evaluaciones del chat para que las evaluen del 1 al 5 en como está siguiendo las instrucciones.

Esta carpeta es la que se comparte para realizar el estudio de usabilidad. Tiene su propio README para explicar como se realiza el estudio

## End to End

Se verifica ejecutando la aplicación.

## Despliegue

Se verifica realizando el despliegue.

## *Nota*

Por cuestiones de paths relativos, en la carpeta existe un directorio backend. En este estan situadas las bases de datos y el directorio de documentos que se pueden necesitar para las pruebas.