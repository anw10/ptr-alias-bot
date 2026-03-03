import json
import pymupdf
import pymupdf4llm
from ollama import chat


def analyze_pdf_page_by_page():
    pdf_path = "zlib1.3.1.pdf"
    doc = pymupdf.open(pdf_path)
    chunks = pymupdf4llm.to_markdown(doc, page_chunks=True)

    system_prompt = """ /no_think You are an expert at analyzing API functions for pointer aliasing and memory ownership.

    POINTER ALIASING means a returned pointer points to the same memory as the first input parameter.

    EXAMPLES:
    char *strchr(const char *s, int c) - Returns pointer INTO input string → ALIASES input
    char *strdup(const char *s) - Returns NEW allocated copy → DOES NOT alias
    void *malloc(size_t size) - Returns NEW memory → DOES NOT alias

    Your job: Determine if the return pointer aliases an input parameter or is newly allocated."""

    results = []

    for i, chunk in enumerate(chunks):
        page_num = chunk["metadata"]["page"]
        print(f"\n{'='*60}")
        print(f"Processing Page {page_num + 1}")
        print(f"{'='*60}")

        prompt = f"""Analyze only the defined API functions on this page for pointer aliasing.

        Page {page_num + 1} content:
        {chunk['text']}

        QUESTIONS:
        1. Does the returned pointer alias (point to same memory as) the first input parameter to the API function?
        2. Who is responsible for freeing the memory?
        3. Which specific parameters does the return value alias (if any)?

        Return ONLY this JSON format:
        {{
        "functions_found": ["function_name1", "function_name2"],
        "analyses": [
            {{
            "function": "function_name",
            "function_signature": "full function signature",
            "return_pointer_alias": true|false|null,
            "ownership": "caller"|"callee"|"unclear",
            "explanation": "brief reasoning",
            "pointer_alias_parameters": ["param1"]
            }}
        ]
        }}
        """

        response = chat(
            model="qwen3:4b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            options={"num_ctx": 40960, "num_predict": 32768},
            stream=False,
        )

        print(response.message.content)
        results.append(
            {
                "page": page_num + 1,
                "file": chunk["metadata"]["file_path"],
                "response": response.message.content,
            }
        )

    with open(pdf_path.split(".")[0] + ".json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n\n All results saved to analysis_results.json")


if __name__ == "__main__":
    analyze_pdf_page_by_page()
