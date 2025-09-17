
import ollama
import json
import re
import os


def convert_to_txt(summarized_path = None, items_path = None): #opcion de la configuración
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
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

convert_to_txt()