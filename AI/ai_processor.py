import ollama
import json
import re
import os
import configparser
import subprocess
import platform
from .result_docx import convert_to_docx

base_dir = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(base_dir, "../config.conf"), encoding="utf-8")

class ai_processor:
    def kill_ollama(self):
        try:
            system = platform.system()
            if system == "Windows":
                subprocess.run(["taskkill", "/IM", "ollama.exe", "/F"], check=False)
            else:
                subprocess.run(["pkill", "-f", "ollama"], check=False)
        except Exception as e:
            print(f"Unable to kill Ollama: {e}")

class summarize_ai(ai_processor):
    def __init__(self):
        super().__init__()

    def cataloj_iteration(self, cataloj_path=None, procedure_id=None):
        global base_dir
        if cataloj_path is None:
            cataloj_path = os.path.join(base_dir, "../tools/cataloj.json")
            cataloj_path = os.path.abspath(cataloj_path)
        
        with open(cataloj_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for cap in data["audit_catalog"]:
                for theme in cap["chapter_themes"]:
                    for subtheme in theme["theme_subthemes"]:
                        for procedure in subtheme["subtheme_procedures"]:     
                            id = procedure["id_procedure"]
                            if re.sub(r"\D", "", id) == re.sub(r"\D", "", procedure_id):
                                severity = procedure["severity"]
                                return severity

    def summarize_observation(self, input_path=None, output_path=None, progress_callback=None, log_callback=None):
        global base_dir

        try:
            version = subprocess.check_output(["ollama", "--version"], text=True).strip()
            if version != "ollama version is 0.11.10":
                log_callback(f"[{version}]...Error, msg Versión incorrecta, por favor instale la version 0.11.10")
                raise Exception
        except Exception:
            return

        config_prompt = config["settings"].get("ai_generative_prompt")
        config_model = config["settings"].get("model")

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
        processed_data = {"documents": []}  # To store processed documents for JSON output

        for doc in data["documents"]:
            if log_callback:
                log_callback(f"Procesando documento: {doc['filename']}...")

            for obs in doc["observations_fetched"]:
                texto = obs["observation"]
                id = obs["procedure"]
                id = re.findall(r"[0-9.]+", id)
                id_procedure = "".join(id)
                severity = self.cataloj_iteration(procedure_id=id_procedure)

                prompt = f"{config_prompt.strip()} {texto.strip()}"

                if log_callback:
                    log_callback(f"Enviando observación a la IA: {texto[:50]}...")

                response = ollama.chat(model=config_model, messages=[
                    {"role": "user", "content": prompt}
                ])

                raw_output = response["message"]["content"]
                think_match = re.search(r"<think>(.*?)</think>", raw_output, flags=re.DOTALL)
                think_content = think_match.group(1).strip() if think_match else ""
                clean_output = re.sub(r"<think>.*?</think>|\*", "", raw_output, flags=re.DOTALL).strip()

                obs["summary"] = clean_output
                obs["think"] = think_content
                obs["severity"] = severity

            # Generate .docx for this document immediately
            items_path = os.path.join(base_dir, "../items/")
            items_path = os.path.abspath(items_path)
            convert_to_docx(doc_data=doc, items_path=items_path)
            if log_callback:
                log_callback(f"Generado archivo DOCX para: {doc['filename']}")

            # Append to processed data for JSON output
            processed_data["documents"].append(doc)

            processed_docs += 1
            if progress_callback:
                progress_callback(int((processed_docs / total_docs) * 100))

        # Save all processed documents to JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def convert_to_docx_handler():
        # This method can be deprecated or kept for compatibility
        pass

def start_ai_processor(progress_callback=None, log_callback=None) -> bool:
    try:
        ai_comander = summarize_ai()
        ai_comander.summarize_observation(
            progress_callback=progress_callback,
            log_callback=log_callback
        )
        # No need to call convert_to_docx_handler here, as DOCX is generated per document
        ai_comander.kill_ollama()  # Kill Ollama process after all processing
        return True
    except Exception as e:
        if log_callback:
            log_callback(f"Error en la IA: {e}")
        return False