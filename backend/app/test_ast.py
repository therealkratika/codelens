from app.rag.ast_parser import JavaScriptParser


def main():

    parser = JavaScriptParser()

    code = """
import express from "express";
import { Battle } from "../model/battle.js";
import { Question } from "../model/question.js";

const app = express();

function startBattle() {
    console.log("Starting battle");
    Question.find();
}

const joinBattle = () => {
    console.log("Joining battle");
};
"""

    imports = parser.extract_imports(code)

    functions = parser.extract_functions(code)
    calls = parser.extract_function_calls(code)

    print("\n" + "=" * 70)
    print("TREE-SITTER AST TEST")
    print("=" * 70)

    print("\nIMPORTS:")

    for item in imports:
        print(f"→ {item}\n")

    print("\nFUNCTIONS:")

    for function in functions:

        print(
            f"→ {function['name']} "
            f"({function['start_line']}-"
            f"{function['end_line']})"
        )

    print("\nFUNCTION CALLS:")
    for call in calls:

        print(f"→ {call['name']}")


if __name__ == "__main__":
    main()