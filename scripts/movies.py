from clipboard import copy

from renaiming import generate_prompt, list_contents, rename_items_with_checks

if __name__ == "__main__":
    directory = r""  # Replace with your directory path

    # For generating prompt
    items = list_contents(directory)
    custom_instructions = """
    Keep year in parenthesis. Examples:
    - 'Movie.Title.2020.mkv' => 'Movie Title (2020)'
    - 'Document_2021.pdf' => 'Document (2021)'
    """
    prompt = generate_prompt(items, custom_instructions)
    print(prompt)
    copy(prompt)

    # For renaming - this part is executed when clean names are provided
    clean_names = []

    rename_items_with_checks(directory, clean_names)
