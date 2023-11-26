import os
import pysftp
from datetime import datetime
import questionary

HOST = '192.168.1.11'
USERNAME = 'cesar'
PASSWORD = 'kali'
REMOTE_DIR = '/home/cesar/prueba/'
REMOTE_BACKUP_DIR = '/home/cesar/copias/'
LOCAL_DIR = r'D:\Desktop\Sistemas_distribuidos\\'
file_registry = {}

def establish_connection():
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    cnopts.compression = True  # Habilitar la compresión
    cnopts.ciphers = ['aes128-ctr', 'aes192-ctr', 'aes256-ctr']  # Ejemplo de algoritmos de cifrado
    return pysftp.Connection(host=HOST, username=USERNAME, password=PASSWORD, cnopts=cnopts)

def create_remote_directories(sftp):
    try:
        sftp.chdir('/home/cesar')
    except IOError:
        pass

    try:
        sftp.chdir('copias')
    except IOError:
        sftp.mkdir('copias')

    try:
        sftp.chdir('/home/cesar')
    except IOError:
        pass

    try:
        sftp.chdir('prueba')
    except IOError:
        sftp.mkdir('prueba')

def upload_file(sftp):
    print("Connection successfully established...")
    create_remote_directories(sftp)  # Create necessary folders on the remote server

    print("Archivos disponibles:\n")
    os.system('cmd /c "dir"')

    print("¿Qué archivo quiere subir?\n")
    asw = input()

    local_file_path = LOCAL_DIR + asw
    remote_file_path = REMOTE_DIR + asw

    # Print the local file path to verify if it exists
    print(f"Local file path: {local_file_path}")

    # Check if the file exists before attempting to upload it
    if os.path.exists(local_file_path):
        sftp.chdir('/home/cesar/prueba')
        sftp.put(local_file_path, remote_file_path)

        now = datetime.now()
        current_time = now.strftime("%Y%m%d%H%M%S")
        backup_remote_path = REMOTE_BACKUP_DIR + asw + '_' + current_time
        sftp.put(local_file_path, backup_remote_path)

        file_registry[asw] = {'metadata': ''}
        print(f"Archivo {asw} subido al servidor remoto y registrado en el sistema.")
    else:
        print("Local file does not exist.")

def download_file(sftp):
    print("Connection successfully established...")
    create_remote_directories(sftp)  # Create necessary folders on the remote server

    print("Archivos disponibles:\n")
    sftp.chdir('/home/cesar/prueba')
    print(sftp.listdir())

    print("¿Qué archivo quiere descargar?\n")
    asw = input()

    local_file_path = LOCAL_DIR + asw
    remote_file_path = REMOTE_DIR + asw
    sftp.get(remote_file_path, local_file_path)

def initialize_project(sftp):
    create_remote_directories(sftp)
    print("Project initialized. Directories 'prueba' and 'copias' created on the server.")
    
def create_directory(sftp, dir_name):
    try:
        remote_dir_path = REMOTE_DIR + dir_name
        sftp.chdir(remote_dir_path)
    except IOError:
        sftp.mkdir(remote_dir_path)
        print(f"Carpeta '{dir_name}' creada en el servidor remoto.")

        # También crea la carpeta en el directorio de copias
        try:
            sftp.chdir(REMOTE_BACKUP_DIR)
        except IOError:
            sftp.mkdir(REMOTE_BACKUP_DIR)

        sftp.chdir(REMOTE_BACKUP_DIR)
        sftp.mkdir(dir_name)
        print(f"Carpeta '{dir_name}' creada en el directorio de copias.")
    else:
        print(f"La carpeta '{dir_name}' ya existe en el servidor remoto.")

def create_file(sftp, file_name, content):
    current_directory = sftp.pwd
    remote_file_path = current_directory + '/' + file_name
    try:
        with sftp.open(remote_file_path, mode='w') as file:
            file.write(content)
        print(f"Archivo {file_name} creado en el servidor remoto en el directorio actual.")

        # También crea una copia del archivo en el directorio de copias
        now = datetime.now()
        current_time = now.strftime("%Y%m%d%H%M%S")
        backup_remote_path = f'{REMOTE_BACKUP_DIR}{current_directory.split("/")[-1]}/{current_time}_{file_name}'
        with sftp.open(backup_remote_path, mode='w') as backup_file:
            backup_file.write(content)
        print(f"Copia del archivo {file_name} creada en el directorio de copias.")
    except IOError as e:
        print(f"Error al crear el archivo en el servidor remoto: {e}")


def read_directory(sftp, dir_name):
    try:
        sftp.chdir(REMOTE_DIR + dir_name)
        files = sftp.listdir()
        for file in files:
            print(file)
    except IOError:
        print("La carpeta no existe.")

def read_file(sftp, file_name):
    remote_file_path = REMOTE_DIR + file_name
    if sftp.exists(remote_file_path):
        with sftp.open(remote_file_path, mode='r') as file:
            content = file.read()
            print(f"Contenido del archivo {file_name}:\n{content}")
    else:
        print("El archivo remoto no existe.")

def update_file(sftp, file_name):
    remote_file_path = REMOTE_DIR + file_name
    if sftp.exists(remote_file_path):
        content = input("Ingrese el nuevo contenido del archivo: ")
        with sftp.open(remote_file_path, mode='w') as file:
            file.write(content)
        print("Archivo actualizado en el servidor remoto.")
    else:
        print("El archivo remoto no existe.")

def delete_directory(sftp, dir_name):
    try:
        sftp.rmdir(REMOTE_DIR + dir_name)
        print(f"Carpeta '{dir_name}' eliminada.")
    except IOError:
        print("La carpeta no existe o no está vacía.")

def delete_file(sftp, file_name, current_directory):
    remote_file_path = current_directory + file_name
    if sftp.exists(remote_file_path):
        sftp.remove(remote_file_path)
        print(f"Archivo '{file_name}' eliminado.")
    else:
        print("El archivo no existe.")


def nav():
    current_directory = REMOTE_DIR
    sftp = establish_connection()
    esc = True
    while esc:
        answer = questionary.select(
            "¿Qué operación desea realizar?",
            choices=[
                "Crear Carpeta",
                "Crear Archivo",
                "Leer Carpeta",
                "Leer Archivo",
                "Actualizar Archivo",
                "Eliminar Carpeta",
                "Eliminar Archivo",
                "Cambiar Carpeta",
                "Ir hacia atrás",
                "Salir",
            ],
        ).ask()

        if answer == "Crear Carpeta":
            dir_name = input("Nombre de la carpeta: ")
            create_directory(sftp, dir_name)
        elif answer == "Crear Archivo":
            file_name = input("Nombre del archivo: \n")
            content = input("Contenido del archivo: ")
            create_file(sftp, file_name, content)
        elif answer == "Leer Carpeta":
            dir_name = input("Nombre de la carpeta: ")
            read_directory(sftp, dir_name)
        elif answer == "Leer Archivo":
            file_name = input("Nombre del archivo: ")
            read_file(sftp, file_name)
        elif answer == "Actualizar Archivo":
            file_name = input("Nombre del archivo: ")
            update_file(sftp, file_name)
        elif answer == "Eliminar Carpeta":
            dir_name = input("Nombre de la carpeta: ")
            delete_directory(sftp, dir_name)
        elif answer == "Eliminar Archivo":
            file_name = input("Nombre del archivo: ")
            delete_file(sftp, file_name, current_directory)
        elif answer == "Cambiar Carpeta":
            dir_name = input("Nombre de la carpeta: ")
            current_directory = current_directory + dir_name + '/'
            print(f"Ahora estás en el directorio: {current_directory}")
            try:
                sftp.chdir(current_directory)
            except IOError as e:
                print(f"No se pudo cambiar al directorio {current_directory}: {e}")
        elif answer == "Ir hacia atrás":
            current_directory = '/'.join(current_directory.split('/')[:-2]) + '/'
            print(f"Ahora estás en el directorio: {current_directory}")
            try:
                sftp.chdir(current_directory)
            except IOError as e:
                print(f"No se pudo cambiar al directorio {current_directory}: {e}")
        elif answer == "Salir":
            esc = False
        else:
            print("Opción no válida.")

    sftp.close()

def add_metadata(filename, metadata):
    if filename in file_registry:
        file_registry[filename]['metadata'] = metadata
    else:
        file_registry[filename] = {'metadata': metadata}
        print(f"Archivo {filename} no existía en el registro. Se ha creado con los metadatos.")
        
def search_files(keyword):
    results = []
    for filename, data in file_registry.items():
        if keyword in filename or (data.get('metadata') and keyword in data['metadata']):
            results.append(filename)
    if results:
        print(f"Archivos encontrados para '{keyword}':")
        for result in results:
            print(result)
    else:
        print(f"No se encontraron archivos relacionados con '{keyword}'.")

def main():
    sftp = establish_connection()
    esc = True
    while esc:
        answer = questionary.select(
            "¿Qué desea realizar?",
            choices=[
                "Subir un archivo",
                "Descargar un archivo",
                "Inicializar Proyecto",
                "Navegar por el servidor",
                "Salir",
                "Agregar metadatos",
                "Buscar archivos por nombre o metadatos",
            ],
        ).ask()

        if answer == "Subir un archivo":
            upload_file(sftp)
        elif answer == "Descargar un archivo":
            download_file(sftp)
        elif answer == "Inicializar Proyecto":
            initialize_project(sftp)
        elif answer == "Salir":
            esc = False
        elif answer == "Navegar por el servidor":
            nav()
        elif answer == "Agregar metadatos":
            file_name = input("Ingrese el nombre del archivo al que desea agregar metadatos: ")
            metadata = input("Ingrese los metadatos para el archivo: ")
            add_metadata(file_name, metadata)
        elif answer == "Buscar archivos por nombre o metadatos":
            keyword = input("Ingrese la palabra clave para buscar archivos: ")
            search_files(keyword)
        else:
            print("Opción no válida.")

    sftp.close()

# main()