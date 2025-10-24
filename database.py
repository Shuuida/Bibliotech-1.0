import json
import os
import tempfile
from shutil import copy2
from datetime import date, datetime

DATA_DIR = "data"
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
GLOBAL_FILENAME = "biblioteca_global.json"
DAILY_PREFIX = "biblioteca_"

def asegurar_directorios():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

def nombre_archivo_diario(fecha_obj):
    # acepta date, datetime, string 'YYYY-MM-DD' o QDate si se desea
    if isinstance(fecha_obj, (date, datetime)):
        iso = fecha_obj.date().isoformat() if isinstance(fecha_obj, datetime) else fecha_obj.isoformat()
    elif isinstance(fecha_obj, str) and fecha_obj:
        iso = fecha_obj
    elif fecha_obj is None:
        iso = date.today().isoformat()
    else:
        iso = str(fecha_obj)
    return f"{DAILY_PREFIX}{iso}.json"

def ruta_para(fecha=None, global_file=False):
    asegurar_directorios()
    if global_file:
        return os.path.join(DATA_DIR, GLOBAL_FILENAME)
    if fecha is None:
        fecha = date.today()
    return os.path.join(DATA_DIR, nombre_archivo_diario(fecha))

def listar_archivos_diarios():
    """Lista de archivos diarios disponibles en data con el prefijo correcto."""
    asegurar_directorios()
    res = []
    for filename in os.listdir(DATA_DIR):
        if filename.startswith(DAILY_PREFIX) and filename.endswith(".json"):
            #intenta extraer la fecha
            try:
                iso = filename[len(DAILY_PREFIX):-5]
                datetime.fromisoformat(iso)  # Validar formato
                res.append(filename)
            except Exception:
                continue
    res.sort
    return res

def cargar_biblioteca(fecha: date = None, global_file: bool = False, path = None):
    """Carga el archivo JSON solicitado. Devuelve un dict vacío si no existe o está corrupto."""
    #Agregamos compatibilidad para cargar archivos dentro de _load_clicked
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    path = ruta_para(fecha, global_file)

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        #archivo corrupto: retornamos vacío para evitar romper la app
        return {}

def hacer_backup(path):
    """
    Crea una copia de seguridad (.bak) del archivo indicado.
    Si no existe o hay error de permisos, devuelve None.
    """
    try:
        if not path or not os.path.exists(path):
            print(f"⚠️ No se puede hacer backup: archivo no encontrado -> {path}")
            return None

        asegurar_directorios()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = os.path.basename(path)
        nombre_backup = f"{base}.bak.{timestamp}"
        dest = os.path.join(BACKUP_DIR, nombre_backup)

        copy2(path, dest)
        print(f"🗂️ Backup creado: {dest}")
        return dest

    except PermissionError:
        print(f"❌ Permiso denegado al intentar copiar: {path}")
        return None
    except Exception as e:
        print(f"⚠️ Error al crear backup: {e}")
        return None

def guardar_biblioteca(biblioteca: dict, fecha=None, global_file: bool=False):
    """
    Guarda el diccionario 'biblioteca' en un JSON de forma robusta:
    - hace backup del archivo existente
    - escribe en un temporal y hace fsync
    - reemplaza atómicamente con os.replace
    Lanza excepciones si algo falla (la UI debe capturarlas y mostrarlas).
    """
    asegurar_directorios()
    target_path = ruta_para(fecha, global_file)

    # Normalizar claves - compatibilidad con archivos antiguos
    for isbn, datos in list(biblioteca.items()):
        if isinstance(datos, dict):
            # claves antiguas -> nuevas
            if "Titulo" in datos and "Título" not in datos:
                datos["Título"] = datos.pop("Titulo")
            if "Fecha de publicacion" in datos and "Fecha de Publicación" not in datos:
                datos["Fecha de Publicación"] = datos.pop("Fecha de publicacion")
            biblioteca[isbn] = datos

    # backup del archivo existente (no obligatorio, pero recomendado)
    try:
        hacer_backup(target_path)
    except Exception:
        # no fallamos si no se pudo backup; lo registraremos mediante excepción posterior si aplica
        pass

    dirpath = os.path.dirname(target_path)
    # Crear archivo temporal en el mismo directorio para permitir reemplazo atómico
    tmp = None
    try:
        # NamedTemporaryFile con delete=False para control explícito del cierre
        fd, tmp_path = tempfile.mkstemp(prefix="tmp_bibl_", dir=dirpath, suffix=".json")
        # Escribir JSON en el descriptor
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            json.dump(biblioteca, tmp, indent=4, ensure_ascii=False)
            tmp.flush()
            os.fsync(tmp.fileno())  # asegurar que se escriba en disco
        # Intento de reemplazo atómico
        try:
            os.replace(tmp_path, target_path)
        except Exception as e_replace:
            # En Windows a veces el archivo destino está bloqueado; intentar eliminar y volver a reemplazar
            try:
                if os.path.exists(target_path):
                    os.remove(target_path)
                os.replace(tmp_path, target_path)
            except Exception as e2:
                # si falla, limpiar tmp y propagar excepción detallada
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
                raise RuntimeError(f"Fallo al reemplazar archivo: {e_replace}; intento2: {e2}") from e2

        # Si llegó aquí, se guardó correctamente
        return target_path

    except Exception as exc:
        # limpiar tmp si quedó
        try:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        # re-lanzar para que la UI pueda mostrar el error
        raise