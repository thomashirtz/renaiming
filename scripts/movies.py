from typing import Dict

from renaiming import (
    generate_llm_prompt,
    rename_items_with_checks,
)

if __name__ == "__main__":
    directory_path = r"D:\Thomas\Movies"

    instructions = """
    Keep year in parenthesis. Examples:
    - 'Movie.Title.2020.mkv' => 'Movie Title (2020)'
    - 'Document_2021.pdf' => 'Document (2021)'
    """

    # Generate a prompt for LLM to suggest new names for the items
    prompt = generate_llm_prompt(
        directory_path=directory_path,
        depth=-1,
        include_folders=True,
        include_files=True,
        copy_prompt_to_clipboard=True,
        custom_instruction=instructions,
    )

    # Display the prompt
    print(prompt)

    # Prepare the renaming map with provided clean names
    renaming_map: Dict[str, str] = {}

    # Execute the renaming process using the specified renaming map
    rename_items_with_checks(directory_path=directory_path, renaming_map=renaming_map)
