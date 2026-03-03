import json
import argparse


def extract_analysis(file_paths):
    for file in file_paths:
        with open(file, "r") as f:
            data = json.load(f)

        all_functions = []
        failures = 0

        for entry in data:
            page = entry["page"]
            response = entry["response"]

            try:
                if "```" in response:
                    response = response.split("```")[1]
                    if response.startswith("json"):
                        response = response[4:]

                analysis = json.loads(response.strip())

                if "analyses" in analysis:
                    for func in analysis["analyses"]:
                        all_functions.append(
                            {
                                "page": page,
                                "function": func.get("function", "unknown"),
                                "return_pointer_alias": func.get(
                                    "return_pointer_alias"
                                ),
                                "ownership": func.get("ownership"),
                                "explanation": func.get("explanation"),
                                "pointer_alias_parameters": func.get(
                                    "pointer_alias_parameters", []
                                ),
                            }
                        )
                else:
                    all_functions.append(
                        {
                            "page": page,
                            "function": analysis.get("function", "unknown"),
                            "return_pointer_alias": analysis.get(
                                "return_pointer_alias"
                            ),
                            "ownership": analysis.get("ownership"),
                            "explanation": analysis.get("explanation"),
                            "pointer_alias_parameters": analysis.get(
                                "pointer_alias_parameters", []
                            ),
                        }
                    )
            except:
                failures += 1
                print(f"Failed to parse page {page}")
        print("*" * 25)
        print(f"Total Failures: {failures}")
        print("*" * 25)

        with open(file.split(".")[0] + "_cleaned" + ".json", "w") as f2:
            json.dump(all_functions, f2, indent=2)

        print("*" * 25)
        print(f"Total functions found: {len(all_functions)}")
        print("*" * 25)
        print("\n\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Helper to normalize llm analysis from pyvl.py"
    )

    parser.add_argument("files", help="Files to process", nargs="+")
    args = parser.parse_args()

    extract_analysis(args.files)
