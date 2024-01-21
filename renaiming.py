from pathlib import Path
from typing import List, Union


def list_contents(directory: Union[str, Path]) -> List[str]:
    """Lists all files and folders in the given directory.

    This function iterates over the contents of the directory, checking each item to determine
    if it is a file or a directory, and then returns a list of their names.

    Args:
        directory: The directory path from which to list contents. It can be a string or a Path object.

    Returns:
        A list of names of files and directories within the given directory.
    """
    directory = Path(directory) if isinstance(directory, str) else directory
    return [item.name for item in directory.iterdir() if item.is_file() or item.is_dir()]


def generate_prompt(items: List[str], custom_instructions: str = "") -> str:
    """Generates a prompt for LLMs based on a list of item names.

    Args:
        items: A list of item names for which to generate a naming prompt.
        custom_instructions: Additional instructions to include in the prompt.

    Returns:
        A formatted prompt string for LLMs.
    """
    prompt = (
        "Please suggest clean names for the following items. The output should be in a codeblock in a python list:\n"
    )
    prompt += "\n".join(f"- '{item}'" for item in items)
    prompt += f"\n\n{custom_instructions}" if custom_instructions else ""
    return prompt


def validate_renaming_inputs(original_names: List[str], clean_names: List[str]) -> None:
    """Validates the inputs for the renaming process.

    Args:
        original_names: The original names of the items to be renamed.
        clean_names: The proposed new clean names for the items.

    Raises:
        ValueError: If the number of original items does not match the number of clean names.
    """
    if not clean_names:
        raise ValueError("No clean names provided.")
    if len(original_names) != len(clean_names):
        raise ValueError("Mismatch in the number of original and clean names.")


def confirm_renaming() -> bool:
    """Asks the user for confirmation before proceeding with the renaming operation.

    Returns:
        True if the user confirms the operation, False otherwise.
    """
    confirmation = input("Confirm renaming (yes/y to confirm): ").strip().lower()
    return confirmation in ["y", "yes"]


def rename_items(directory: Path, original_names: List[str], clean_names: List[str]) -> None:
    """Renames items within the specified directory.

    Args:
        directory: The directory containing the items to be renamed.
        original_names: A list of the original names of the items.
        clean_names: A list of new names to apply to the items.
    """
    for original_name, clean_name in zip(original_names, clean_names):
        try:
            old_path = directory / original_name
            file_extension = old_path.suffix if old_path.is_file() else ""
            new_name_with_ext = clean_name + file_extension
            new_path = directory / new_name_with_ext

            if not old_path.exists():
                print(f"Item not found: {original_name}")
                continue

            if new_path.exists() and new_path != old_path:
                print(f"Skipping: {new_name_with_ext} already exists.")
                continue

            old_path.rename(new_path)
            print(f"Renamed '{original_name}' to '{new_name_with_ext}'")
        except OSError as error:
            print(f"Error renaming '{original_name}': {error}")


def rename_items_with_checks(directory: Union[str, Path], clean_names: List[str]) -> None:
    """Coordinates the entire renaming process, including validation and user confirmation.

    Args:
        directory: The directory containing the items to be renamed.
        clean_names: A list of new, clean names to be assigned to the items.
    """
    directory = Path(directory) if isinstance(directory, str) else directory
    original_names = list_contents(directory)

    try:
        validate_renaming_inputs(original_names, clean_names)
        if confirm_renaming():
            rename_items(directory, original_names, clean_names)
        else:
            print("Renaming operation cancelled.")
    except ValueError as error:
        print(f"Input validation error: {error}")
