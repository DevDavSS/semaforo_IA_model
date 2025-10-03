
import os, json

base_dir = os.path.dirname(os.path.abspath(__file__))

def add_border(cell, border="top"):
    """Agrega borde a una celda (para separar secciones)"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    borders = tcPr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement('w:tcBorders')
        tcPr.append(borders)

    element = OxmlElement(f"w:{border}")
    element.set(qn("w:val"), "single")
    element.set(qn("w:sz"), "12")      # grosor
    element.set(qn("w:space"), "0")
    element.set(qn("w:color"), "000000")
    borders.append(element)

def set_cell_font(cell, size=9, bold=False):
    """Aplica formato de letra a todo el texto dentro de una celda"""
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = RGBColor(0, 0, 0)

def convert_to_docx(summarized_path=None, items_path=None):  
    global base_dir
    if summarized_path is None:
        summarized_path = os.path.join(base_dir, "../output/output_with_summaries.json")
        summarized_path = os.path.abspath(summarized_path)
    if items_path is None:
        items_path = os.path.join(base_dir, "../items/")
        items_path = os.path.abspath(items_path)

    with open(summarized_path, "r", encoding="utf-8") as fr:
        data = json.load(fr)

        for doc in data["documents"]:
            # Crear documento Word
            document = Document()
            
            # Título del documento
            document.add_heading(f"Resultados de {doc['filename']}", level=1)

            # Crear tabla de una sola columna
            table = document.add_table(rows=0, cols=1)
            table.style = "Light Grid Accent 1"

            # Agregar observaciones
            for obs in doc["observations_fetched"]:
                # 1) Número de observación
                row1 = table.add_row().cells
                row1[0].text = f"OBSERVACIÓN N° {obs['no_observation']}"
                add_border(row1[0], "top")
                set_cell_font(row1[0], size=9)

                # 2) Pensamiento IA
                row2 = table.add_row().cells
                row2[0].text = f"Razonamiento de la IA:\n{obs['think']}"
                set_cell_font(row2[0], size=9)

                # 3) Severidad
                row3 = table.add_row().cells
                row3[0].text = f"Nivel de Severidad: {obs['severity']}"
                set_cell_font(row3[0], size=9)

                # 4) Resumen (negritas)
                row4 = table.add_row().cells
                p = row4[0].paragraphs[0]
                run = p.add_run(f"Resumen:\n{obs['summary']}")
                run.bold = True
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(0, 0, 0)

            # Guardar DOCX
            filename = os.path.splitext(doc["filename"])[0] + ".docx"
            output_path = os.path.join(items_path, filename)
            document.save(output_path)

convert_to_docx()
