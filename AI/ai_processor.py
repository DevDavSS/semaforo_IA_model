import ollama
import json
import re
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
class ai_processor:
    def __init__(self):
        self.model = "deepseek-r1:8b"



class summarize_ai(ai_processor):
    def __init__(self ):
        super()


    def summarize_observation(self, input_path = None, output_path = None):
        global base_dir

        if input_path == None:
            input_path = os.path.join(base_dir,"../input/input.json")
            input_path = os.path.abspath(input_path)
        if output_path == None:
            output_path = os.path.join(base_dir,"../output/output_with_summaries.json")
            output_path = os.path.abspath(output_path)

        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for doc in data["documents"]:
            for obs in doc["observations_fetched"]:
                texto = obs["observation"]

                prompt = f"""
                El texto anteriormente proveído, es una observación fiscal hacia una entidad fiscalizada, necesito que hagas un resumen breve pero detallado de la situación y el problema que se está identificando en la observación, no debe ser largo el resumen, pero si conciso y los más detallado posible en montos, contrataciones, servicios, etc. Todo hazlo en un párrafo
                La sigueinte observacion, {texto}
                """

                response = ollama.chat(model="deepseek-r1:8b", messages=[
                    {"role": "user", "content": prompt}
                ])

                raw_output = response["message"]["content"]
                clean_output = re.sub(r"<think>.*?</think>", "", raw_output, flags=re.DOTALL).strip()
                obs["summary"] = clean_output
                break
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def convert_to_txt(summarized_path = None, items_path = None): #opcion de la configuración
        global base_dir
        if summarized_path == None:
            summarized_path = os.path.join(base_dir,"../output/output_with_summaries.json")
            summarized_path = os.path.abspath(summarized_path)
        if items_path == None:
            items_path =os.path.join( base_dir,"../items/")
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


class chat_with_ai(ai_processor):
    def __init__(self, prompt):
        super().__init__(prompt)


    def generate_response(self):
        response = ollama.chat(model=self.model, messages=[
            {
                "role":"user",
                "content": self.prompt
            
            }
        ])
        return response



def start_ai_processor() -> bool:
    try:
        ai_comander = summarize_ai()
        ai_comander.summarize_observation()
        summarize_ai.convert_to_txt()
    except Exception as e:
        print("There was wn error:", e)
        return False
    return True