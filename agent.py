import json
import ollama

from tools import (
    get_employee,
    get_department_employees,
    find_employee_name
)


MODEL = "llama3.2:1b"


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_employee",
            "description": "Find employee information by employee name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The employee's name"
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_department_employees",
            "description": "Find all employees belonging to a department.",
            "parameters": {
                "type": "object",
                "properties": {
                    "department": {
                        "type": "string",
                        "description": "The department name"
                    }
                },
                "required": ["department"]
            }
        }
    }
]


def execute_tool(tool_name, arguments, user_question=""):

    if not isinstance(arguments, dict):
        arguments = {}

    # Some smaller models may return the arguments
    # inside a "properties" object.
    if isinstance(arguments.get("properties"), dict):
        arguments = arguments["properties"]

    if tool_name == "get_employee":
        name = arguments.get("name")
        if not isinstance(name, str):
            name = find_employee_name(user_question)
        if name is None:
            return 'Invalid arguments for get_employee: expected {"name": "employee name"}.'
        return get_employee(name)

    elif tool_name == "get_department_employees":
        department = arguments.get("department")
        if not isinstance(department, str):
            return 'Invalid arguments for get_department_employees: expected {"department": "department name"}.'
        return get_department_employees(
            department
        )

    return "Unknown tool"


def format_employee_answer(employee, user_question):
    question = user_question.lower()
    fields = []

    if any(term in question for term in ("joining date", "join date", "start date", "joined")):
        fields.append(("joining date", "joining_date"))
    if any(term in question for term in ("salary", "pay")):
        fields.append(("salary", "salary"))
    if any(term in question for term in ("department", "team")):
        fields.append(("department", "department"))

    if not fields:
        fields = [
            ("department", "department"),
            ("joining date", "joining_date"),
            ("salary", "salary")
        ]

    details = []
    for label, key in fields:
        value = employee[key]
        if key == "salary":
            value = f"{value:,}"
        details.append(f"{label}: {value}")

    return f"{employee['name']}: " + "; ".join(details) + "."


def run_agent(user_question):

    messages = [
        {
            "role": "system",
            "content": """
You are an employee information assistant.

You have access to tools that can search an Excel
employee database.

Use the tools when the user's question requires
employee information.

Do not invent employee information.

For get_employee, pass only an object with a "name" string.

After receiving the tool result, provide a clear
and simple answer to the user.
"""
        },
        {
            "role": "user",
            "content": user_question
        }
    ]

    while True:

        response = ollama.chat(
            model=MODEL,
            messages=messages,
            tools=tools
        )

        assistant_message = response["message"]

        messages.append(assistant_message)

        # Check whether the model wants to call a tool
        if "tool_calls" not in assistant_message:
            return assistant_message["content"]

        # Execute each requested tool
        for tool_call in assistant_message["tool_calls"]:

            function_name = tool_call["function"]["name"]

            arguments = tool_call["function"]["arguments"]

            print(
                f"\n[Agent calling tool: {function_name}]"
            )

            print(
                f"[Arguments: {arguments}]"
            )

            result = execute_tool(
                function_name,
                arguments,
                user_question
            )

            print(
                f"[Tool result: {result}]"
            )

            if function_name == "get_employee" and isinstance(result, dict):
                return format_employee_answer(result, user_question)

            messages.append(
                {
                    "role": "tool",
                    "content": json.dumps(result)
                }
            )


def main():

    print("================================")
    print(" Ollama Employee AI Agent")
    print("================================")
    print("Type 'exit' to quit.\n")

    while True:

        question = input("You: ")

        if question.lower() == "exit":
            break

        answer = run_agent(question)

        print("\nAgent:", answer)
        print()


if __name__ == "__main__":
    main()