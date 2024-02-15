import json
import os
import tempfile
from threading import Timer


class FunctionExecutor:
    def __init__(self, function_name_to_function_map):
        self.function_name_to_function_map = function_name_to_function_map

    def _execute(self, function_name, args):
        func = self.function_name_to_function_map.get(function_name)
        if func and callable(func):
            return func(**args)
        else:
            raise ValueError(f"Function {func} not found or is not callable.")

    def _function_output_to_temp_file(self, function_output, ttl=3600):
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', prefix='temp_', dir="tmp")

        json.dump(function_output, temp_file)
        temp_file.close()

        # Schedule the file to be deleted after a ttl
        Timer(ttl, os.remove, args=[temp_file.name]).start()

        return os.path.join("tmp", temp_file.name)

    def execute_and_get_file_output(self, function_name, args):
        function_output = self._execute(function_name, args)
        return self._function_output_to_temp_file(function_output)