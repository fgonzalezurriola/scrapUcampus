import requests
from bs4 import BeautifulSoup
import re
import json
import os

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

# URLs para otoño y primavera
urls = [
    "https://ucampus.uchile.cl/m/fcfm_catalogo/?semestre=20241&depto=5",  # Otoño
    "https://ucampus.uchile.cl/m/fcfm_catalogo/?semestre=20242&depto=5"   # Primavera
]

# Variable modificable para el nombre del archivo en inglés
nombre_archivo = "CC_data"

# Diccionario para evitar duplicados
courses_dict = {}

# Función para formatear correctamente los prerrequisitos
def formatear_prerrequisitos(requisitos_text):
    requisitos = re.findall(r'[A-Z]{2,3}\d{4}[A-Z]*', requisitos_text)
    return requisitos

# Procesar cada URL
for url in urls:
    response = requests.get(url)
    semestre = "Otoño" if "20241" in url else "Primavera"
    print(f"\nProcesando semestre: {semestre}")

    # Verificar si la solicitud fue exitosa, si lo fue, obtener el html
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontrar todos los ramos en la página, por divs con clase 'ramo'
        ramos = soup.find_all('div', class_='ramo')
        print(f"Encontrados {len(ramos)} ramos en {semestre}")
        
        for ramo in ramos:
            try:
                # Extraer el nombre y código del ramo
                nombre = ramo.find('h1').get_text(strip=True)
                codigo = ramo.find('h2').get_text(strip=True)

                # Saltar si el código tiene menos de 6 caracteres (ramos de postgrado)
                if len(codigo) < 6:
                    continue

                # Extraer créditos y prerrequisitos
                leyenda = soup.find('dl', class_=f'leyenda c{codigo}')
                
                if leyenda:
                    creditos_elem = leyenda.find('dt', string=re.compile('Créditos:', re.IGNORECASE))
                    if creditos_elem:
                        creditos = int(creditos_elem.find_next_sibling('dd').get_text(strip=True))
                        
                        requisitos_elem = leyenda.find('dt', string=re.compile('Requisitos:', re.IGNORECASE))
                        requisitos = []
                        if requisitos_elem and requisitos_elem.find_next_sibling('dd'):
                            requisitos_text = requisitos_elem.find_next_sibling('dd').get_text(strip=True)
                            if requisitos_text.strip():
                                requisitos = formatear_prerrequisitos(requisitos_text)

                        course = {
                            "id": codigo,
                            "name": nombre,
                            "credits": creditos,
                            "prerequisites": requisitos,
                            "color": "bg-common" # Color definido en mi TailwindCSS
                        }
                        
                        # Si no apareció en otoño, añadirlo al diccionario
                        if codigo not in courses_dict:
                            courses_dict[codigo] = course
            except Exception as e:
                print(f"Error procesando ramo {codigo}: {str(e)}")
    else:
        print(f'Error al acceder a la página de {semestre}')

# Convertir el diccionario a lista
courses = list(courses_dict.values())
print(f"\nTotal de cursos únicos procesados: {len(courses)}")

# Crear el JSON de salida
json_output = {
    f"{nombre_archivo}": courses
}

# Guardar el JSON en un archivo en la misma con el nombre de la variable nombre_archivo (definida al inicio)
output_file = os.path.join(os.getcwd(), f"{nombre_archivo}.json")
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(json_output, file, indent=2, ensure_ascii=False)

print(f"\nArchivo JSON guardado en: {output_file}")