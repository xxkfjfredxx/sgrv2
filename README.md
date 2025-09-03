# 🛡️ Sistema de Gestión de Riesgos – Backend

¡Bienvenido al backend del **Sistema de Gestión de Riesgos Laborales**!  
Este proyecto está construido con **Django** + **Django REST Framework**, y forma parte de una solución integral para la gestión de empleados, documentos y riesgos laborales en organizaciones.

---

## 📦 Tecnologías utilizadas

- 🐍 **Python 3.10+**
- 🌐 **Django** y **Django REST Framework**
- 🗂️ Modularización profesional por apps (`apps/`)
- 🔐 **JWT Authentication**
- 🗃️ **MariaDB / MySQL compatible**
- 📂 Gestión de documentos con `FileField` y estructura organizada por tipo/fecha

---

## ⚙️ Instalación del proyecto en una nueva máquina (Windows)

### 1️⃣ Clona el repositorio
```bash
git clone https://github.com/xxkfjfredxx/sgr_backend.git
cd sgr_backend
```

### 2️⃣ Crea y activa el entorno virtual
```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Instala las dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ Instala dependencias del sistema (si hace falta)

- Si falta `mysqlclient`:
```bash
pip install mysqlclient
```

- Si da error con `ImageField` (Pillow):
```bash
pip install Pillow
```

> ⚠️ **Importante (Windows):**  
> Si `mysqlclient` falla, asegúrate de tener:
> - ✅ **MySQL Server** instalado  
> - ✅ **MySQL Connector C**: https://dev.mysql.com/downloads/connector/c/  
> - ✅ **Microsoft C++ Build Tools**

---

### 5️⃣ Configura la base de datos

Abre el archivo `config/settings/development.py` y revisa la sección `DATABASES`:

```python
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'sgr_db',
    'USER': 'root',
    'PASSWORD': 'tu_contraseña',
    'HOST': 'localhost',
    'PORT': '3306',
  }
}
```

---

### 6️⃣ Crea la base de datos (desde Workbench o CLI)

```sql
CREATE DATABASE sgr_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

### 7️⃣ Aplica las migraciones
```bash
python manage.py migrate
```

---

### 8️⃣ (Opcional) Crea un superusuario
```bash
python manage.py createsuperuser
```

---

### 9️⃣ Ejecuta el servidor
```bash
python manage.py runserver
```

Accede en tu navegador a: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

✅ **Listo para trabajar o continuar desarrollando tu sistema.**  
Para dudas o mejoras, crea un issue o contáctame.
