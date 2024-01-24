from typing import Dict

from clipboard import copy

from renaiming import (
    generate_llm_prompt,
    list_directory_items,
    rename_items_with_checks,
)

if __name__ == "__main__":
    directory = r"D:\Thomas\Desktop\Avenir LT Std"

    # Generate a prompt for LLM to suggest new names for the items
    items = list_directory_items(
        directory=directory,
        depth=-1,
        include_folders=True,
        include_files=True,
    )

    renaming_instructions = """
    Keep year in parenthesis. Examples:
    - 'Movie.Title.2020.mkv' => 'Movie Title (2020)'
    - 'Document_2021.pdf' => 'Document (2021)'
    """

    llm_prompt = generate_llm_prompt(
        items=items,
        custom_instructions=renaming_instructions,
    )
    print(llm_prompt)
    copy(llm_prompt)  # Copy the prompt to the clipboard for easy use

    # Prepare the renaming map with provided clean names
    renaming_map: Dict[str, str] = {}

    # Execute the renaming process using the specified renaming map
    rename_items_with_checks(directory=directory, renaming_map=renaming_map)
