import ollama
import json
import re
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

class ai_processor:
    def __init__(self):
        self.model = "deepseek-r1:8b"


class summarize_ai(ai_processor):
    def __init__(self):
        super().__init__(self)
    

    def cataloj_iteration(self, cataloj_path = None, observation_id = None):
        global base_dir
        if cataloj_path is None:
            cataloj_path = os.path.join(base_dir, "../tools/cataloj.json")
            cataloj_path = os.path.abspath(cataloj_path)
        
        with open(cataloj_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            #En esta iteración se puede modificar en el caso de que la severidad no se obtenga en la parte del subtema.
            for cap in data["audit_catalog"]:
                for theme in cap["chapter_themes"]:
                    for subtheme in theme["theme_subthemes"]:
                        
                        id = subtheme["subtheme_id"]
                        severity = subtheme["severity"]
                        if re.sub(r"\D", "",id) == re.sub(r"\D", "",observation_id):
                            return severity


    def summarize_observation(self, input_path=None, output_path=None, progress_callback=None, log_callback=None):
        global base_dir

        if input_path is None:
            input_path = os.path.join(base_dir, "../input/input.json")
            input_path = os.path.abspath(input_path)
        if output_path is None:
            output_path = os.path.join(base_dir, "../output/output_with_summaries.json")
            output_path = os.path.abspath(output_path)

        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        total_docs = len(data["documents"])
        processed_docs = 0

        for doc in data["documents"]:
            for obs in doc["observations_fetched"]:
                texto = obs["observation"]
                id = obs["subtheme"]  #normalizar id para futura comparación con catálogo de auditorias
                id = re.findall(r"[0-9.]+", id)
                id_subtheme = "".join(id)
                severity = self.cataloj_iteration(observation_id=id_subtheme)
 

    @staticmethod
    def convert_to_txt(summarized_path=None, items_path=None):
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
                filename = os.path.splitext(doc["filename"])[0] + ".txt"
                with open(os.path.join(items_path, filename), "w", encoding="utf-8") as fw:
                    for obs in doc["observations_fetched"]:
                        no_observation = obs["no_observation"]
                        summary = obs["summary"]
                        thinking = obs["think"]
                        severity = obs["severity"]
                        severity = f"\n {severity} \n"
                        title = f"\n--------------------- Numero de observación: {no_observation} ---------------------\n"
                        thinking_text = f"\n--Razonmiento de la IA: {thinking}"
                        fw.write(title)
                        fw.write(thinking_text)
                        fw.write(severity)
                        fw.write(summary)


def start_ai_processor(progress_callback=None, log_callback=None) -> bool:
    try:
        ai_comander = summarize_ai()
        ai_comander.summarize_observation(
            progress_callback=progress_callback,
            log_callback=log_callback
        )
        summarize_ai.convert_to_txt()
    except Exception as e:
        if log_callback:
            log_callback(f" Error en la IA: {e}")
        return False
    return True
