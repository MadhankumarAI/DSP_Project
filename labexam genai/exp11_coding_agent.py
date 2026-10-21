"""
Experiment 11: Design a Coding AI Agent
- Accept a natural language query
- Decompose into multiple subtasks
- Decide which tool to use for each subtask (calculator, web search, debugger)
- Maintain short-term memory (STM)
- Implement conditional decision making, e.g. if info is insufficient
  search again, or if calc is needed use it again
- Generate final answer by showing the agent execution trace
"""
import re

short_term_memory = []  # STM: list of {subtask, tool, result}

def calculator(expression):
    match = re.search(r"[-+*/0-9.()\s]{3,}", expression)
    if not match:
        return None  # insufficient info -> triggers fallback
    try:
        return eval(match.group(), {"__builtins__": {}})
    except Exception:
        return None

def web_search(query):
    return f"[stubbed search result for: '{query}']"

def debugger(code_snippet):
    try:
        compile(code_snippet, "<subtask>", "exec")
        return "No syntax errors found."
    except SyntaxError as error:
        return f"Syntax error: {error}"

def choose_tool(subtask):
    if any(char.isdigit() for char in subtask) and any(op in subtask for op in "+-*/"):
        return "calculator"
    if "debug" in subtask.lower() or "code" in subtask.lower() or "error" in subtask.lower():
        return "debugger"
    return "web_search"

def run_agent(query):
    subtasks = [s.strip() for s in query.split(" and ") if s.strip()]  # decompose
    trace = []
    for subtask in subtasks:
        tool = choose_tool(subtask)
        if tool == "calculator":
            result = calculator(subtask)
            if result is None:  # conditional decision: insufficient info -> fall back to search
                tool = "web_search"
                result = web_search(subtask)
        elif tool == "debugger":
            result = debugger(subtask)
        else:
            result = web_search(subtask)
        short_term_memory.append({"subtask": subtask, "tool": tool, "result": result})
        trace.append(f"  Subtask: '{subtask}' -> Tool: {tool} -> Result: {result}")

    print("=== Agent Execution Trace ===")
    print("\n".join(trace))
    final_answer = " | ".join(str(m["result"]) for m in short_term_memory)
    print("\n=== Final Answer ===")
    print(final_answer)

if __name__ == "__main__":
    user_query = "what is 23*17 and search for python list comprehension and debug this code: def f(:"
    run_agent(user_query)
