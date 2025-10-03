import pandas as pd
import json

# Pandas manejará NaN para celdas vacías.

df = pd.read_excel('new_audit_cataloj.xlsx')

# Eliminar filas donde 'NÚMERO' esté vacío o NaN
df = df.dropna(subset=['NÚMERO'])
df = df[df['NÚMERO'].astype(str).str.strip() != '']

# Inicializar la estructura del JSON
audit_catalog = []
current_chapter = None
current_theme = None
current_subtheme = None

for index, row in df.iterrows():
    numero = str(row['NÚMERO']).strip()
    if not numero:
        continue
    
    # Contar el número de puntos para determinar el nivel
    dots = numero.count('.')
    
    if dots == 0:
        # Capítulo (nivel 1, e.g., "1")
        current_chapter = {
            "chapter": str(row['CAPÍTULO']) if not pd.isna(row['CAPÍTULO']) else "",
            "chapter_id": numero,
            "chapter_themes": []
        }
        audit_catalog.append(current_chapter)
        current_theme = None
        current_subtheme = None
    
    elif dots == 1:
        # Tema (nivel 2, e.g., "1.1")
        if current_chapter is None:
            continue  # Error si no hay capítulo previo
        current_theme = {
            "theme": str(row['TEMA']) if not pd.isna(row['TEMA']) else "",
            "theme_id": numero,
            "theme_subthemes": []
        }
        current_chapter['chapter_themes'].append(current_theme)
        current_subtheme = None
    
    elif dots == 2:
        # Subtema (nivel 3, e.g., "1.1.1")
        if current_theme is None:
            continue  # Error si no hay tema previo
        current_subtheme = {
            "subtheme": str(row['SUBTEMA']) if not pd.isna(row['SUBTEMA']) else "",
            "subtheme_id": numero,
            "subtheme_procedures": [],

        }
        current_theme['theme_subthemes'].append(current_subtheme)
    
    elif dots == 3:
        # Procedimiento (nivel 4, e.g., "1.1.1.1")
        if current_subtheme is None:
            continue  # Error si no hay subtema previo
        procedure = {
            "id_procedure": numero,
            "procedure": str(row['PROCEDIMIENTO']) if not pd.isna(row['PROCEDIMIENTO']) else "",
            "description_cases_noncompliance": str(row['DESCRIPCIÓN SUPUESTOS DE INCUMPLIMIENTO']) if not pd.isna(row['DESCRIPCIÓN SUPUESTOS DE INCUMPLIMIENTO']) else "",
            "normative": f"{str(row['MARCO NORMATIVO']) if not pd.isna(row['MARCO NORMATIVO']) else ''} {str(row['ARTÍCULOS DE LA LEY PARA INCUMPLIMIENTO']) if not pd.isna(row['ARTÍCULOS DE LA LEY PARA INCUMPLIMIENTO']) else ''}".strip(),
            "severity": "--" #futura lógica para la implementación del nivel de severidad mediante un diccionario que asiganará los niveles de severidad.
        }
        current_subtheme['subtheme_procedures'].append(procedure)

# Crearcion de json
json_output = {"audit_catalog": audit_catalog}

# Imprimir o guardar el JSON
print(json.dumps(json_output, indent=4, ensure_ascii=False))

with open('cataloj.json', 'w', encoding='utf-8') as f:
    json.dump(json_output, f, indent=4, ensure_ascii=False)