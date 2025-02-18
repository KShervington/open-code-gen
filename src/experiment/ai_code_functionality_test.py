import unittest
from langchain.llms import Ollama
from langchain import PromptTemplate

class TestCodeCompletion(unittest.TestCase):

    def setUp(self):
        # Initialize Ollama model.  Adjust model name as needed.
        self.llm = Ollama(model="qwen2.5-coder:7b")  # Or another suitable code model

        self.prompt_template = """
        Write a Python function called `calculate` that performs the following operation: {operation}

        The function should take two numerical arguments, `a` and `b`, and return the result of the operation.  
        Do not include any docstrings or comments in the generated function.
        Only provide the function definition.
        """
        self.prompt = PromptTemplate(
            input_variables=["operation"],
            template=self.prompt_template,
        )
        self.chain = self.prompt | self.llm # DEPRECATED: LLMChain(llm=self.llm, prompt=self.prompt)


    def test_multiplication(self):
        operation = "Multiply two numbers."
        expected_output = 15
        a = 3
        b = 5

        code = self.chain.invoke(operation)

        # Dynamically execute the generated code
        try:
            # First, clean up the code to remove any extra text.
            # This is a basic approach. More robust parsing might be needed.
            cleaned_code = code.strip()  # Remove leading/trailing whitespace
            if cleaned_code.startswith("```python"):
                cleaned_code = cleaned_code[len("```python"):]
            if cleaned_code.endswith("```"):
                cleaned_code = cleaned_code[:-len("```")]

            # Compile the generated code to ensure it's valid Python
            compiled_code = compile(cleaned_code, "<string>", "exec")

            # Execute the compiled code in a local namespace
            local_namespace = {}
            exec(compiled_code, local_namespace)

            # Get the generated function from the local namespace
            generated_function = local_namespace['calculate']

            actual_output = generated_function(a, b)
            self.assertEqual(actual_output, expected_output)

        except Exception as e: # Catch any errors during execution
            self.fail(f"Code execution failed: {e}. Generated code: \n{code}")



    def test_addition(self):
        operation = "Add two numbers."
        expected_output = 8
        a = 3
        b = 5
        code = self.chain.invoke(operation)
        try:
            cleaned_code = code.strip()
            if cleaned_code.startswith("```python"):
                cleaned_code = cleaned_code[len("```python"):]
            if cleaned_code.endswith("```"):
                cleaned_code = cleaned_code[:-len("```")]

            compiled_code = compile(cleaned_code, "<string>", "exec")
            local_namespace = {}
            exec(compiled_code, local_namespace)
            generated_function = local_namespace['calculate']
            actual_output = generated_function(a, b)
            self.assertEqual(actual_output, expected_output)

        except Exception as e:
            self.fail(f"Code execution failed: {e}. Generated code: \n{code}")

    def test_subtraction(self):
        operation = "Subtract two numbers."
        expected_output = 2
        a = 5
        b = 3
        code = self.chain.invoke(operation)
        try:
            cleaned_code = code.strip()
            if cleaned_code.startswith("```python"):
                cleaned_code = cleaned_code[len("```python"):]
            if cleaned_code.endswith("```"):
                cleaned_code = cleaned_code[:-len("```")]

            compiled_code = compile(cleaned_code, "<string>", "exec")
            local_namespace = {}
            exec(compiled_code, local_namespace)
            generated_function = local_namespace['calculate']
            actual_output = generated_function(a, b)
            self.assertEqual(actual_output, expected_output)

        except Exception as e:
            self.fail(f"Code execution failed: {e}. Generated code: \n{code}")

    def test_division(self):
        operation = "Divide two numbers."
        expected_output = 5
        a = 10
        b = 2

        code = self.chain.invoke(operation)

        # Dynamically execute the generated code
        try:
            # First, clean up the code to remove any extra text.
            # This is a basic approach. More robust parsing might be needed.
            cleaned_code = code.strip()  # Remove leading/trailing whitespace
            if cleaned_code.startswith("```python"):
                cleaned_code = cleaned_code[len("```python"):]
            if cleaned_code.endswith("```"):
                cleaned_code = cleaned_code[:-len("```")]

            # Compile the generated code to ensure it's valid Python
            compiled_code = compile(cleaned_code, "<string>", "exec")

            # Execute the compiled code in a local namespace
            local_namespace = {}
            exec(compiled_code, local_namespace)

            # Get the generated function from the local namespace
            generated_function = local_namespace['calculate']

            actual_output = generated_function(a, b)
            self.assertEqual(actual_output, expected_output)

        except Exception as e: # Catch any errors during execution
            self.fail(f"Code execution failed: {e}. Generated code: \n{code}")

if __name__ == "__main__":
    unittest.main()

# Base code genrated by Gemini 2.0 Flash with the following prompt:
# Create a python script which goes through several test cases. The script should request code completion from an Ollama model via LangChain (such as qwen2.5-coder). The code completion should result in a simple function, like multiplying two numbers. Using each test case, the script should execute execute the AI-generated function and make sure the output matches the expected output.
