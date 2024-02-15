from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType
import ast
import re
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Dict, Optional, Type

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools.base import BaseTool
from langchain_core.runnables.config import run_in_executor


def sanitize_input(query: str) -> str:
    # Removes `, whitespace & python from start
    query = re.sub(r"^(\s|`)*(?i:python)?\s*", "", query)
    # Removes whitespace & ` from end
    query = re.sub(r"(\s|`)*$", "", query)
    return query


class PythonInputs(BaseModel):
    query: str = Field(description="code snippet to run")


class PythonInterpreter(BaseTool):
    name: str = "python_repl_ast"
    description: str = (
        "A Python shell. Use this to execute python commands. "
        "Input should be a valid python command. "
    )
    globals: Optional[Dict] = Field(default_factory=dict)
    locals: Optional[Dict] = Field(default_factory=dict)
    sanitize_input: bool = True
    args_schema: Type[BaseModel] = PythonInputs

    def _run(
            self,
            query: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            if self.sanitize_input:
                query = sanitize_input(query)
            tree = ast.parse(query)
            module = ast.Module(tree.body[:-1], type_ignores=[])
            exec(ast.unparse(module), self.globals, self.locals)  # type: ignore
            module_end = ast.Module(tree.body[-1:], type_ignores=[])
            module_end_str = ast.unparse(module_end)  # type: ignore
            io_buffer = StringIO()
            try:
                with redirect_stdout(io_buffer):
                    ret = eval(module_end_str, self.globals, self.locals)
                    if ret is None:
                        return io_buffer.getvalue()
                    else:
                        return ret
            except Exception:
                with redirect_stdout(io_buffer):
                    exec(module_end_str, self.globals, self.locals)
                return io_buffer.getvalue()
        except Exception as e:
            return "{}: {}".format(type(e).__name__, str(e))

    async def _arun(
            self,
            query: str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Any:
        return await run_in_executor(None, self._run, query)


class Resolver:
    def __init__(self, llm_name="gpt-3.5-turbo"):
        self.resolver_prompt = """
        I want you to answer the following question: {question}.
        The data needed to answer this is present in the following file as a json (dictionary or list)
        and can be loaded into a variable with json.load() : {function_output_file_path}.
        """
        python_interpreter = PythonInterpreter()
        python_interpreter_tool = Tool("python_interpreter", description=python_interpreter.description,
                                       func=python_interpreter.run)
        self.resolver_agent = initialize_agent([python_interpreter_tool], ChatOpenAI(model=llm_name), agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)


    def resolve(self, question, invoked_helper_function, function_output_file_path):
        prompt = self.resolver_prompt.format(question=question, invoked_helper_function=invoked_helper_function, function_output_file_path=function_output_file_path)
        print("Resolver prompt: ", prompt)
        response = self.resolver_agent.invoke(prompt)
        if response and response["output"]:
            return str(response["output"])
        else:
            raise Exception("No response from the resolver agent")
