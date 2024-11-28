# URLs para otoño y primavera

# Cambiar el número del final (en "...&depto={Numero a cambiar}") para obtener distintos departamentos
# 3: Astronomía
# 5: Ciencias de la Computación
# 6: Civil
# 10: Eléctrica
# 13: Física
# 15: Geofísica
# 16: Geología
# 19: Industrial
# 21: Matemática
# 22: Mecánica
# 23: Minas
# 307: Quimica y BT

import requests
from bs4 import BeautifulSoup
import re
import json
import os

# URLs para otoño y primavera
urls = [
    "https://ucampus.uchile.cl/m/fcfm_catalogo/?semestre=20241&depto=5",  # Otoño
    "https://ucampus.uchile.cl/m/fcfm_catalogo/?semestre=20242&depto=5"   # Primavera
]

# Metadatos
metadata = {
    "name": "V Semestre",
    "season": "Primavera",
    "degree": "Licenciatura"
}

# Diccionario para evitar duplicados
courses_dict = {}

# Función para formatear correctamente los prerrequisitos
def formatear_prerrequisitos(requisitos_text):
    return re.findall(r'[A-Z]{2,3}\d{4}[A-Z]*', requisitos_text)

# Procesar cada URL
for url in urls:
    response = requests.get(url)
    semestre = "Otoño" if "20241" in url else "Primavera"
    print(f"\nProcesando semestre: {semestre}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        ramos = soup.find_all('div', class_='ramo')
        print(f"Encontrados {len(ramos)} ramos en {semestre}")
        
        for ramo in ramos:
            try:
                # Extraer el nombre y código del ramo
                nombre = ramo.find('h1').get_text(strip=True)
                codigo = ramo.find('h2').get_text(strip=True)

                if len(codigo) < 6:  # Ignorar ramos de postgrado
                    continue

                leyenda = soup.find('dl', class_=f'leyenda c{codigo}')
                if leyenda:
                    creditos_elem = leyenda.find('dt', string=re.compile('Créditos:', re.IGNORECASE))
                    creditos = int(creditos_elem.find_next_sibling('dd').get_text(strip=True)) if creditos_elem else 0

                    requisitos_elem = leyenda.find('dt', string=re.compile('Requisitos:', re.IGNORECASE))
                    requisitos = []
                    if requisitos_elem:
                        requisitos_text = requisitos_elem.find_next_sibling('dd').get_text(strip=True)
                        requisitos = formatear_prerrequisitos(requisitos_text)

                    # Crear el curso con campos iniciales
                    course = {
                        "code": codigo,
                        "name": nombre,
                        "credits": creditos,
                        "requires": requisitos,
                        "unlocks": []  # Inicialmente vacío, se llenará después
                    }
                    
                    if codigo not in courses_dict:
                        courses_dict[codigo] = course
            except Exception as e:
                print(f"Error procesando ramo {codigo}: {str(e)}")
    else:
        print(f'Error al acceder a la página de {semestre}')

# Crear índice inverso para "unlocks"
unlock_index = {codigo: [] for codigo in courses_dict}

for codigo, curso in courses_dict.items():
    for prereq in curso["requires"]:
        if prereq in unlock_index:
            unlock_index[prereq].append(codigo)

# Actualizar los "unlocks" en cada curso
for codigo, unlocks in unlock_index.items():
    if codigo in courses_dict:
        courses_dict[codigo]["unlocks"] = unlocks

# Crear JSON de salida
output = {
    "metadata": metadata,
    "courses": list(courses_dict.values())
}

# Guardar el JSON en un archivo
nombre_archivo = "CC_data_primavera.json"
output_file = os.path.join(os.getcwd(), nombre_archivo)
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(output, file, indent=2, ensure_ascii=False)

print(f"\nArchivo JSON guardado en: {output_file}")
