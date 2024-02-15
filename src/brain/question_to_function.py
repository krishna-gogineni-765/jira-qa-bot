import json

from langchain_openai import ChatOpenAI

from langchain_core.utils.function_calling import convert_to_openai_tool

class QuestionToFunction:
    def __init__(self, supported_functions, llm_name="gpt-3.5-turbo"):
        self.supported_functions = supported_functions
        self.llm = ChatOpenAI(model=llm_name)

    def get_apt_function_and_parameters(self, question):
        response = self.llm.invoke(question, tools=[convert_to_openai_tool(func) for func in self.supported_functions])
        args = json.loads(response.additional_kwargs["tool_calls"][0]["function"]["arguments"])
        function_name = response.additional_kwargs["tool_calls"][0]["function"]["name"]
        return (function_name, args)


