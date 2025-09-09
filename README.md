# Data-Com.-Game
Esto es un juego de turnos que se creo para la clase de comunicación de datos en la universidad de UPRB. La aplicación debe tener una estructura de cliente-servidor. 
El cliente y servidor deben comunicarse mediante [sockets](https://docs.python.org/3/library/socket.html).

## Equipo de trabajo 
* Eduardo J. Matos Pérez
* Guillermo Myers

## Como correr el programa
* OJO: La aplicación esta compuesta de dos partes: el cliente y el servidor.
    - Solo debe haber 1 servidor corriendo.
    - Pueden haber varios clientes corriendo.
* OJO: El servidor tiene que estar corriendo para que funcione la aplicación.
* Para probar la aplicación en un ambiente de prueba:
    1. Ir al directorio de `Data-Com.-Game`.
    2. Abrir al menos tres instancias del terminal en este directorio (1 para el servidor y 2 para el cliente).
    3. En un terminal, ir al directorio del servidor `cd server` y luego correrlo `python main.py`.
    4. En los otros dos terminales, ir al directorio del cliente `cd client` y correrlos `python main.py`.
 
## Documentacion
### Protocolo
* [Enlace a documentacion del protocolo](docs/PROTOCOL.md).

## Ideas
* Simple RPB (Puede ser complicado pensar en las mecanicas)
* Juego de cartas
* Juegos de mesa
  * Stratego ([video tutorial](https://youtu.be/3R7d0A9ymwQ?si=mtdiY1v7GfDuuOxt))
      - Desventaja: las partidas pueden ser largas (30 min.)
  * Go ([video tutorial](https://youtu.be/gOvG5ACfeL4?si=De_OHUljeq2VZBPb))
      - Desventaja: Los juegos pueden ser muy largos
* Juego inspirado por [Wordle](https://en.wikipedia.org/wiki/Wordle), pero con elementos de multijugador.
    - Wordle típicamente es un juego de un solo jugador.
* ect.

## Herramientas
* Lenguaje de programacián: Python
* Framework para gráficas y UI: Pygame y pygame-menu

## Tutoriales de programación
* [Tutoriales de pygame](https://www.pygame.org/wiki/tutorials)
  * [Como crear menus con pygame-menu](https://coderslegacy.com/python/create-menu-screens-in-pygame-tutorial/)
