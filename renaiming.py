from pathlib import Path
from typing import List, Union, Dict


def list_contents(directory: Union[str, Path]) -> List[str]:
    """Lists all files and folders in the given directory, including subdirectories.

    This function iterates over the contents of the directory and its subdirectories,
    returning a list of their relative path names.

    Args:
        directory: The directory path from which to list contents. It can be a string or a Path object.

    Returns:
        A list of relative path names of files and directories within the given directory.
    """
    directory = Path(directory) if isinstance(directory, str) else directory
    items = []
    for item in directory.rglob('*'):
        if item.is_file() or item.is_dir():
            items.append(str(item.relative_to(directory)))
    return items

def generate_prompt(items: List[str], custom_instructions: str = "") -> str:
    """Generates a prompt for LLMs based on a list of item names.

    Args:
        items: A list of item names for which to generate a naming prompt.
        custom_instructions: Additional instructions to include in the prompt.

    Returns:
        A formatted prompt string for LLMs.
    """
    prompt = (
        "Please suggest clean names for the following items. The output should be in a codeblock in a python dict where you have the key as the old name and the value with the new name:\n"
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


def rename_items(directory: Path, renaming_map: Dict[str, str]) -> None:
    """Renames items within the specified directory, including subdirectories.

    Args:
        directory: The base directory containing the items to be renamed.
        renaming_map: A dictionary mapping from original relative paths to new relative paths.
    """
    # Sort items by depth, deeper paths first
    sorted_items = sorted(renaming_map.items(), key=lambda item: len(Path(item[0]).parts), reverse=True)
    print(sorted_items)
    for original_rel_path, new_rel_path in sorted_items:
        try:
            old_path = directory / original_rel_path
            new_path = directory / new_rel_path

            if not old_path.exists():
                print(f"Item not found: {old_path}")
                continue

            elif new_path.exists():
                if old_path.is_dir():
                    # Handle existing directory (skip or merge logic here)
                    print(f"Skipping directory as it already exists: {new_path}")
                    continue
                else:
                    print(f"Skipping: {new_path} already exists.")
                    continue

            new_path.parent.mkdir(parents=True, exist_ok=True)

            # Handling directory renaming
            if old_path.is_dir():
                # Creating new directory structure if it doesn't exist
                new_path.mkdir(parents=True, exist_ok=True)
                # todo check if directory is empty, if it is the case possibility to remove the old one

            old_path.rename(new_path)
            print(f"Renamed '{old_path}' to '{new_path}'")
        except OSError as error:
            print(f"Error renaming '{old_path}': {error}")


def rename_items_with_checks(directory: Union[str, Path], renaming_map: Dict[str, str]) -> None:
    """Coordinates the entire renaming process, including validation and user confirmation.

    Args:
        directory: The directory containing the items to be renamed.
        renaming_map: A dictionary mapping original names to new, clean names.
    """
    directory = Path(directory) if isinstance(directory, str) else directory

    try:
        # Updated validation to work with the dictionary
        validate_renaming_inputs_with_map(directory, renaming_map)
        if confirm_renaming():
            rename_items(directory, renaming_map)
        else:
            print("Renaming operation cancelled.")
    except ValueError as error:
        print(f"Input validation error: {error}")

def validate_renaming_inputs_with_map(directory: Path, renaming_map: Dict[str, str]) -> None:
    """Validates the renaming map against the contents of the directory.

    Args:
        directory: The directory with items to be renamed.
        renaming_map: A mapping of original to new names.

    Raises:
        ValueError: If there's a mismatch between directory contents and the renaming map.
    """

    if not renaming_map:
        raise ValueError("No renaming map provided.")
