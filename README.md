# 🎓 Documentación del Proyecto: Sistema Experto RAG con Ollama

Esta guía describe el proceso paso a paso para configurar y ejecutar el Sistema Experto, una aplicación que utiliza el modelo **Mistral** a través de **Ollama** y la librería **LangChain** para proporcionar asesoría basada en documentos (RAG).

## 📥 1. Prerrequisitos Iniciales

Antes de comenzar, asegúrate de tener el entorno de desarrollo listo.

### 1.1. Clonar el Repositorio

Abre tu terminal y ejecuta el siguiente comando para clonar el repositorio del proyecto en tu máquina local. Reemplaza `"URL"` con la dirección real de tu repositorio (por ejemplo, en GitHub).

```bash
git clone https://github.com/MichaelGald/Proyecto_Sistemas_expertos.git
cd Proyecto_Sistemas_expertos
```

### 1.2. Instalar Python

Debes tener **Python** instalado en tu sistema.

  * **Versión Mínima Requerida:** **Python 3.10** o superior.

Puedes verificar tu versión actual ejecutando:

```bash
python --version 
# o 
python3 --version
```

-----

## 🛠️ 2. Configuración de Ollama (Servidor LLM Local)

**Ollama** es el *software* que actúa como servidor local para ejecutar el modelo de lenguaje (LLM) Mistral.

### 2.1. Instalación de Ollama

Descarga el instalador oficial de Ollama, según tu sistema operativo (Windows, macOS o Linux):

🔗 **Enlace de Descarga:** [https://ollama.com/download](https://ollama.com/download)

  * **Usuarios de Windows/macOS:** Ejecuta el archivo descargado para instalar Ollama como un servicio en segundo plano.
  * **Usuarios de Linux:** Sigue las instrucciones proporcionadas en el sitio web o usa el *script* de instalación recomendado.

### 2.2. Verificación de la Instalación

Una vez que la instalación haya finalizado, abre una nueva terminal y escribe `ollama`. Deberías ver la lista de comandos disponibles, confirmando que el servicio está instalado y es accesible.

```bash
ollama
```

**Salida Esperada (Resumen):**

```
Available Commands:
  serve       Start ollama
  create      Create a model
  ...
  pull        Pull a model from a registry
  ...
```

### 2.3. Instalar el Modelo Mistral

Ahora, descarga el modelo específico que utilizará la aplicación: **Mistral**. Es recomendable usar la versión instructiva (`mistral:instruct`) ya que está optimizada para seguir instrucciones (útil para tu `prompt_maestro`).

Asegúrate de que el servicio Ollama esté activo y ejecuta:

```bash
ollama pull mistral:instruct
```

> **Nota:** El archivo es de aproximadamente 4.1 GB y puede tardar en descargarse dependiendo de tu conexión.

> **Nota:** Instalar de igual manera el modelo por defecto, este pesa aproximadamente 4.4 GB

```bash
ollama pull mistral
```

-----

## 📦 3. Instalación de Dependencias de Python

Dentro de la carpeta raíz de tu repositorio clonado, instala todas las librerías de Python necesarias para el funcionamiento del proyecto (LangChain, Chroma, Streamlit, etc.).

### 3.1. Instalar Paquetes

Instala todas las dependencias:

```bash
pip install langchain-community chromadb langchain-text-splitters httpx tqdm pdfplumber streamlit
```

-----

## ▶️ 4. Ejecución del Proyecto (Web)

El proyecto se ejecuta a través de **Streamlit**, que creará una interfaz web local para interactuar con el Sistema Experto.

### 4.1. Pre-procesar Documentos (Opcional)

Si los documentos originales están en PDF legible o con texto (no imagenes), primero ejecuta el *script* de conversión `convert_pdf.py` o `convert_tablas` para generar los archivos `.md` que el sistema RAG puede leer:

> **Nota:** La carpeta documentos_unah fue ignorada en este punto del repositorio, si se requiere solicitarla a @CristianGmz7

```bash
python convert_pdf.py "nombre_completo_archivo_sin_extension"
```

```bash
python convert_tablas.py "nombre_completo_archivo_con_extension.pdf"
```

> **Resultado:** Los archivos de texto serán colocados en la carpeta `documentos_unah_txt/`.

### 4.1. Iniciar la Interfaz Web

1.  Abre tu terminal.
2.  **Asegúrate de estar en la carpeta raíz del repositorio o donde se encuentre `interface.py`.**
3.  Ejecuta el comando de Streamlit:

<!-- end list -->

```bash
streamlit run interface.py
```

### 4.2. Acceso a la Aplicación

Streamlit iniciará el servidor web. La terminal te proporcionará los enlaces.

  * **Accede a la aplicación en tu navegador:**
      * **Local URL:** `http://localhost:8501` (o similar)

### 4.3. Indexación Inicial

La primera vez que cargues la interfaz web:

1.  La aplicación detectará si la base de datos de vectores existe.
2.  Si no existe, utiliza el botón **"📥 Indexar documentos"** en el panel lateral (sidebar).
3.  **Importante:** La indexación es el proceso donde se crean los *embeddings* con Ollama. **Este proceso tardará varios minutos.** Revisa la **terminal** donde ejecutaste el comando `streamlit run` para ver el progreso detallado de la indexación (barra de `tqdm`).
4. Esta carpeta esta siendo ignorada, cualquier actualizacion pasarle por medios extras

Una vez completada la indexación, el mensaje cambiará a **"¡Documentos indexados correctamente\!"** y podrás comenzar a hacer consultas. El proyecto debería ejecutarse sin problemas.
