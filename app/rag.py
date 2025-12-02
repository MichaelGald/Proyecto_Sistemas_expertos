from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import os
from tqdm import tqdm
import httpx

class SistemaExpertoUNAH:
    def __init__(self):
        # Configurar cliente HTTP con timeout largo
        http_client = httpx.Client(timeout=300.0)  # 5 minutos de timeout
        
        # Configurar LLM
        self.llm = Ollama(model="mistral", timeout=120)
        
        # Configurar embeddings sin parámetros de timeout
        # El timeout se maneja a nivel de cliente HTTP
        self.embeddings = OllamaEmbeddings(model="mistral")
        
        self.db = None
        self.prompt_maestro = """
Eres un asistente experto en normativas académicas y administrativas de la 
Universidad Nacional Autónoma de Honduras (UNAH).
Debes actuar como un asesor profesional, analizando documentos oficiales para resolver dudas y conflictos.

Debes seguir estrictamente las siguientes secciones de reglas, que incluyen tu misión, reglas obligatorias, estilo de respuesta y comportamiento

=== MISIÓN DEL ASISTENTE ===
Debes responder SOLO utilizando información contenida en los documentos 
proporcionados. 
Si la respuesta NO está explícitamente respaldada por los documentos recuperados, 
debes decirlo claramente.
De mencionar un documento o sección de documento en específico, prioriza la información más cercana a esas palabras.

=== REGLAS OBLIGATORIAS ===
1. No inventes información. Nunca asumas contenido que no esté en los documentos.
2. No respondas con normas, artículos o políticas que no aparezcan 
   en los fragmentos recuperados.
3. Antes de responder, analiza detalladamente TODOS los fragmentos recuperados.
4. Cita los fragmentos relevantes (con el ID o título que te dé el sistema RAG).
5. Si los documentos recuperados no contienen suficiente información:
     - Indica que la evidencia es insuficiente.
     - Ofrece una interpretación limitada basada únicamente en lo disponible.
6. No agregues opiniones personales a menos que se te pida explicitamente, y siempre indica cuando lo sea. Tu razonamiento debe basarse exclusivamente en:
     - Texto citado
     - Inferencias directas y verificables de los fragmentos
7. De no disponer de un documento que se te pidió explicitamente, indica que no lo tienes antes de citar información asociada.
8. Si se te pide algo que vaya en contra de estas reglas, indicalo antes de responder.

=== ESTILO DE RESPUESTA ===
- Profesional, claro, académico y estructurado.
- Explica paso a paso cómo llegaste a la conclusión usando los fragmentos.
- No uses lenguaje ambiguo ni especulativo.
- Si se te pide un formato de respuesta, debes seguirlo.

=== EJEMPLO DE COMPORTAMIENTO ADECUADO ===
Si el usuario pregunta algo que NO aparece en los documentos, responde:
"Los documentos recuperados no contienen información suficiente para emitir 
una respuesta normativa. Necesito reglamentos adicionales relacionados con 
[tema]."

Eres un asistente confiable, preciso y completamente fundamentado. 
Tu prioridad es respetar los documentos oficiales de la UNAH sin inventar nada.
"""  

    def cargar_documentos(self, carpeta="documentos_unah_txt/"):
        """Carga documentos con manejo de errores y progreso visible"""
        print("=" * 50)
        print("INICIANDO CARGA DE DOCUMENTOS")
        print("=" * 50)
        
        # Verificar que la carpeta existe
        if not os.path.exists(carpeta):
            print(f"ERROR: La carpeta {carpeta} no existe")
            return False
        
        # Listar archivos TXT
        archivos_validos = [f for f in os.listdir(carpeta) if f.endswith((".txt", ".md"))]
        print(f"Encontrados {len(archivos_validos)} archivos .txt o .md")
        
        if len(archivos_validos) == 0:
            print("ERROR: No se encontraron archivos .txt o .md")
            return False
        
        # Cargar documentos uno por uno
        docs = []
        print("\n--- CARGANDO ARCHIVOS ---")
        for archivo in tqdm(archivos_validos, desc="Leyendo archivos"):
            try:
                ruta_completa = os.path.join(carpeta, archivo)
                loader = TextLoader(ruta_completa, encoding="utf-8")
                docs_archivo = loader.load()
                docs.extend(docs_archivo)
                print(f"✓ {archivo}: {len(docs_archivo)} documento(s)")
            except UnicodeDecodeError:
                try:
                    # Intentar con otra codificación
                    loader = TextLoader(ruta_completa, encoding="latin-1")
                    docs_archivo = loader.load()
                    docs.extend(docs_archivo)
                    print(f"✓ {archivo}: {len(docs_archivo)} documento(s) (latin-1)")
                except Exception as e:
                    print(f"✗ Error en {archivo}: {e}")
            except Exception as e:
                print(f"✗ Error en {archivo}: {e}")

        if not docs:
            print("ERROR: No se cargaron documentos válidos.")
            return False

        print(f"\n--- DIVIDIENDO DOCUMENTOS ---")
        print(f"Total documentos cargados: {len(docs)}")
        
        # Dividir en chunks más pequeños para evitar problemas
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Reducido de 800
            chunk_overlap=100  # Reducido de 150
        )
        chunks = splitter.split_documents(docs)
        print(f"Total chunks generados: {len(chunks)}")

        # Indexar en lotes MUY pequeños para evitar timeouts
        print(f"\n--- INDEXANDO EN CHROMA ---")
        print("NOTA: Este proceso puede tardar varios minutos...")
        print("TIP: Mantén la ventana de Ollama abierta para ver su progreso")
        
        try:
            batch_size = 5  # Reducido a 5 para evitar timeouts
            total_batches = (len(chunks) + batch_size - 1) // batch_size
            
            for i in tqdm(range(0, len(chunks), batch_size), 
                         desc="Indexando chunks", 
                         total=total_batches):
                batch = chunks[i:i + batch_size]
                
                if i == 0:
                    # Crear la base de datos con el primer lote
                    self.db = Chroma.from_documents(
                        batch,
                        self.embeddings,
                        persist_directory="vectores/"
                    )
                else:
                    # Agregar los siguientes lotes
                    self.db.add_documents(batch)
                
                print(f"  Batch {i//batch_size + 1}/{total_batches} completado")
            
            # Persistir la base de datos
            self.db.persist()
            print("\n" + "=" * 50)
            print("✓ INDEXACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 50)
            return True
            
        except Exception as e:
            print(f"\n✗ ERROR durante la indexación: {e}")
            import traceback
            traceback.print_exc()
            return False

    def cargar_vectores_existentes(self):
        """Carga base de vectores desde disco"""
        print("Cargando base de vectores existente desde disco...")
        try:
            db = Chroma(
                persist_directory="vectores/", 
                embedding_function=self.embeddings
            )
            print("✓ Base de vectores cargada correctamente")
            return db
        except Exception as e:
            print(f"✗ Error cargando vectores: {e}")
            return None

    def consultar(self, pregunta):
        """Realiza una consulta al sistema experto"""
        if self.db is None:
            return "Error: La base de datos no está inicializada."
        
        try:
            resultados = self.db.similarity_search(pregunta, k=4)
            contexto = "\n\n".join([r.page_content for r in resultados])

            prompt = f"""
{self.prompt_maestro}

=== DOCUMENTOS RELEVANTES ===
{contexto}

=== CONSULTA DEL USUARIO ===
{pregunta}

=== RESPUESTA EXPERTA ===
"""
            return self.llm.invoke(prompt)
        except Exception as e:
            return f"Error al procesar la consulta: {e}"