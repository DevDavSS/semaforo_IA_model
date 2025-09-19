import ollama
import json
import re
import os
import logging

base_dir = os.path.dirname(os.path.abspath(__file__))

class ai_processor:
    def __init__(self):
        self.model = "deepseek-r1:8b"


class summarize_ai(ai_processor):
    def __init__(self):
        super().__init__()

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

                prompt = f"""
                El texto anteriormente proveído, es una observación fiscal hacia una entidad fiscalizada, necesito que hagas un resumen breve pero detallado de la situación y el problema que se está identificando en la observación, no debe ser largo el resumen, pero si conciso y los más detallado posible en montos, contrataciones, servicios, etc. Todo hazlo en un párrafo
                La siguiente observación: {texto}
                """

                if log_callback:
                    log_callback(f"Enviando observación a la IA: {texto[:50]}...")

                response = ollama.chat(model="deepseek-r1:8b", messages=[
                    {"role": "user", "content": prompt}
                ])

                raw_output = response["message"]["content"]
                clean_output = re.sub(r"<think>.*?</think>|\*", "", raw_output, flags=re.DOTALL).strip()

                obs["summary"] = clean_output

            processed_docs += 1
            if progress_callback:
                progress_callback(int((processed_docs / total_docs) * 100))

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

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
                        title = f"\n--------------------- Numero de observación: {no_observation} ---------------------\n"
                        fw.write(title)
                        fw.write(summary + "\n")


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
            log_callback(f"❌ Error en la IA: {e}")
        return False
    return True
