from src.brain.function_executor import FunctionExecutor
from src.brain.question_to_function import QuestionToFunction
from src.brain.resolver import Resolver
from src.ipaas.jira_integration import function_name_to_function_map


class Orchestrator:
    def __init__(self):
        self.question_to_function_generator = QuestionToFunction(function_name_to_function_map.values())
        self.function_executor = FunctionExecutor(function_name_to_function_map)
        self.resolver = Resolver()

    def run_query(self, query):
        function_name, args = self.question_to_function_generator.get_apt_function_and_parameters(query)
        print("Decided to call the function: ", function_name, " with args: ", args)
        output_file_path = self.function_executor.execute_and_get_file_output(function_name, args)
        print("Function output file path: ", output_file_path)
        return self.resolver.resolve(query, function_name, output_file_path)
