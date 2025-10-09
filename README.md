# Taller Videojuegos

![commits](https://badgen.net/github/commits/UR-CC/lpa1-taller-videojuegos?icon=github) 
![last_commit](https://img.shields.io/github/last-commit/UR-CC/lpa1-taller-videojuegos)

- ver [badgen](https://badgen.net/) o [shields](https://shields.io/) para otros tipos de _badges_

## Autor

Jaider Francisco Asprilla reyes 

- [@estudiante](https://github.com/Jaider77)

## Descripción del Proyecto
🪐 Space Adventure

Space Adventure es un videojuego tipo shooter espacial 2D desarrollado en Python con Pygame, donde el jugador debe sobrevivir a múltiples oleadas de enemigos, usar poderes especiales y derrotar jefes épicos cada 5 niveles.
Cuenta con 10 escenarios animados con scroll, música ambiental (opcional), y una progresión de dificultad dinámica.

🎮 Características principales

🚀 10 niveles únicos con fondos animados (scroll infinito).

🧠 Dificultad progresiva: más enemigos, más rápidos y más agresivos.

💥 Power-ups con habilidades especiales:

🔫 Disparo doble – Doble proyectil durante 10s.

⚡ Disparo rápido – Mayor velocidad de disparo durante 10s.

❤️ Curación – Recupera 1 punto de vida (máx. 5).

🛡️ Escudo – Inmunidad durante 5 segundos.

👹 Jefes poderosos en los niveles 5 y 10.

🎨 Fondos de alta resolución (1280x720) con transición suave entre niveles.

🎵 Soporte para añadir música y efectos sonoros.

# 🧩 Estructura del proyecto
SpaceAdventure/
│
├── main.py
├── assets/
│   ├── player.png
│   ├── enemy_ground.png
│   ├── enemy_flying.png
│   ├── final_boss.png
│   ├── power_double.png
│   ├── heal.png
│   ├── fast.png
│   ├── power_shield.png
│   ├── background.png
│   ├── background2.png
│   ├── ...
│   └── background10.png
│
└── README.md


📂 Puedes agregar tus propias imágenes o reemplazar las existentes, manteniendo los nombres para que el juego las reconozca automáticamente.

# ⚙️ Instalación

Asegúrate de tener Python 3.9 o superior instalado.

1️⃣ Abre una terminal en la carpeta del juego.
2️⃣ Instala la librería pygame:

pip install pygame


# 3️⃣ Ejecuta el juego:

python main.py


💡 Si estás en Windows, puedes crear un acceso directo o un archivo .bat para iniciar automáticamente el juego.

🕹️ Controles del jugador
Acción	Tecla
Mover a la izquierda	⬅️
Mover a la derecha	➡️
Disparar	Barra espaciadora (SPACE)
Salir del juego	Cerrar ventana o ALT + F4
❤️ Mecánicas del juego

Comienzas con 3 vidas (puedes cambiarlo en Player.__init__()).

Cada nivel tiene una oleada más que el anterior.

Cada 5 niveles aparece un jefe final.

Si derrotas al jefe del nivel 10, ganas el juego.

Al morir, aparece el mensaje 💀 Game Over 💀.

🧠 Configuración avanzada (main.py)

Puedes ajustar fácilmente:

Número de niveles → NUM_LEVELS = 10

Vidas iniciales del jugador → self.hp = 3

Duración del escudo → 5000 ms (línea en update())

Velocidad del scroll → variable scroll_y

Enemigos por oleada → BASE_ENEMIES

# 🌌 Créditos

Desarrollado por Jaider Reyes
🎓 Estudiante de Ingeniería de Sistemas, apasionado por la mecatrónica, los robots y los videojuegos futuristas.
⚙️ Programado y diseñado completamente en Python + Pygame.

# 🚀 Próximas mejoras sugeridas

Sonido y música de fondo.

Sistema de puntuaciones guardadas (highscore).

Nuevos tipos de enemigos.

Modo cooperativo local o competitivo.

Selector de dificultad.