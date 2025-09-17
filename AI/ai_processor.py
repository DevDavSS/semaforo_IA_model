import ollama
import json
import re

class ai_processor:
    def __init__(self):
        self.model = "deepseek-r1:8b"



class summarize_ai(ai_processor):
    def __init__(self ):
        super()


    def summarize_observation(self, input_path, output_path):
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




ai_comander = summarize_ai()
ai_comander.summarize_observation("../input/input.json","../output/output_with_summaries.json")
