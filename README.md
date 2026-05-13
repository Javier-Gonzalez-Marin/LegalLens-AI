## Guía de inicio rápido
Sigue estos pasos para levantar el entorno completo utilizando Docker:

# Levantar los servicios con Docker Compose:

docker-compose up -d --build

Preparar el Backend:
Ejecuta las migraciones para crear las tablas en la base de datos y crea un usuario de acceso:

# Crear tablas
docker-compose exec backend python manage.py migrate

# Crear usuario administrador (Abogado)
docker-compose exec backend python manage.py createsuperuser

Acceso:
Abre tu navegador en http://localhost/ e inicia sesión.

Variables de entorno (.env)
Para que el proyecto funcione correctamente, debes crear un archivo .env en la raíz del proyecto (o donde lo gestione tu docker-compose) con la siguiente estructura:

Fragmento de código
# Claves de APIs Externas
GOOGLE_API_KEY=tu_clave_de_gemini_aqui
O si usas OpenAI:
OPENAI_API_KEY=tu_clave_de_openai_aqui

# Configuración de Django
DJANGO_SECRET_KEY=una_clave_secreta_para_desarrollo
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Esquema de clases y aplicación de POO
En este proyecto es la base de la lógica de negocio para procesar los contratos de forma organizada:

1. Modelo de Datos (Contrato)
Hemos definido una clase Contrato que hereda de models.Model. definineod el comportamiento de un contrato dentro del sistema

Atributos: Almacena el nombre del archivo, cliente, tipo , fecha y el resultado del análisis.

Relaciones: Implementa una relación de clave foránea (ForeignKey) con el modelo User, permitiendo que cada objeto contrato pertenezca a un abogado 

2. Interacción entre Servicios
El flujo de datos entre el backend y el ai_engine se basa en mantener la integridad de la información desde que el archivo PDF se introduce en el servidor hasta que el motor de IA devuelve los atributos procesados.
