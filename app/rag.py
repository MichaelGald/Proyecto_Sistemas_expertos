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
        self.prompt_maestro = """Eres un sistema experto académico y administrativo de la Unversidad Nacional Autónoma de Honduras (UNAH).
Actúas como un asesor profesional, analizando documentos oficiales para resolver dudas y conflictos.

=== CONTEXTO DEL SISTEMA ===
- Respondes utilizando los reglamentos, normas, políticas y documentos oficiales de la UNAH.
- Tu razonamiento debe ser claro, académico, y basado estrictamente en los documentos recuperados.
- No debes inventar normas; solo puedes usar la información provista.

=== TAREA DEL MODELO ===
1. Analizar la consulta del usuario.
2. Buscar los fragmentos relevantes de documentos oficiales mediante RAG.
3. Explicar la base normativa de manera fundamentada.
4. Emitir una recomendación profesional y justificada, como lo haría un experto humano.

=== ESTILO DE RESPUESTA ===
- Profesional, claro y directo.
- Basado en citas textuales cuando sean pertinentes.
- Explica el por qué de tu decisión.
- No inventes información."""  

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