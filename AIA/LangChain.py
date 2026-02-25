from langchain_ollama import OllamaLLM
import json


class AI_Manager:

    def __init__(self, llm_model="deepseek-r1:1.5b"):
        self.llm = OllamaLLM(
                model=llm_model,
                temperature=0
            )
        
        self.telemetry_line = []
        self.data = {}

    def read_data(self, path='data.json'):
        with open(path, 'r') as f:
            self.data = json.load(f)

    def make_response(self):

        self.read_data()

        # Loops through to replace _ with spaces in the keys and '.title()' uppercases first letter
        # Ex) primary_oxygen -> Primary Oxygen
        for key, value in self.data.items():
            self.telemetry_line.append(f"{key.replace('_', ' ').title()}: {value}")

        # Combines list into one string block that has endline per element 
        telemetry_block = "\n".join(self.telemetry_line)


        # Creating Prompt using 3 quotes for multi-line f-string
        prompt = f"""
        You are an EVA SUIT assistant.

        Telemetry:
        {telemetry_block}

        Respond by listing the telemetry in this format:
        Key is at value, Key is at value, Key is at value

        Replace Key and value with the actual telemetry names and numbers.
        Only include the keys shown.
        Do not write the words "Key" or "value".
        Do not write ":" use "is at" instead.
        """
        response = self.llm.invoke(prompt)

        print(f"\n{response}\n")

        self.save_response(response=response, path="response.json")

    def save_response(self, response, path):
        with open (path, 'w') as f:
            json.dump(response, f, indent=2)


ai_manager = AI_Manager()
ai_manager.make_response()



