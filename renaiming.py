from pathlib import Path
from typing import List, Union, Dict


PROMPT = '''
Please suggest clean names for the following items. The output should be in a codeblock in a python dict where you have 
the keys as the old names and the values as the new names:\n
'''


def list_contents(directory: Union[str, Path], depth: int = -1, include_files: bool = True, include_folders: bool = True) -> List[str]:
    """
    Lists files and/or folders in the given directory with control over the depth and type of items listed.

    Args:
        directory: The directory path from which to list contents. Can be a string or a Path object.
        depth: The maximum depth of subdirectories to traverse. -1 for unlimited depth.
        include_files: Boolean to indicate whether to include files in the listing.
        include_folders: Boolean to indicate whether to include folders in the listing.

    Returns:
        A list of relative path names of files and/or directories within the given directory, up to the specified depth.
    """
    directory = Path(directory) if isinstance(directory, str) else directory
    items = []

    for item in directory.rglob('*'):
        if is_item_included(
                item=item,
                base_directory=directory,
                depth=depth,
                include_files=include_files,
                include_folders=include_folders,
        ):
            items.append(str(item.relative_to(directory)))

    return items


def is_item_included(item: Path, base_directory: Path, depth: int, include_files: bool, include_folders: bool) -> bool:
    """
    Helper function to determine if an item should be included based on depth and type (file/folder).

    Args:
        item: The Path object of the item to check.
        base_directory: The base directory from which depth is calculated.
        depth: The specified depth for inclusion.
        include_files: Flag to include files.
        include_folders: Flag to include folders.

    Returns:
        True if the item meets the depth and type criteria, False otherwise.
    """
    item_depth = len(item.relative_to(base_directory).parts)
    depth_condition = depth == -1 or item_depth <= depth

    file_condition = include_files and item.is_file()
    folder_condition = include_folders and item.is_dir()

    return depth_condition and (file_condition or folder_condition)


def generate_prompt(items: List[str], custom_instructions: str = "", base_prompt: str = PROMPT) -> str:
    """
    Generates a custom prompt for LLMs (Large Language Models) based on a list of file and directory names.
    The prompt requests suggestions for cleaner names, formatted as a Python dictionary.

    Args:
        items: A list of relative path names of files and/or directories.
        custom_instructions: Additional specific instructions or context to include in the prompt.
        base_prompt: The base prompt text to which items and custom instructions are appended.

    Returns:
        A formatted string prompt for LLMs, ready to be used for obtaining naming suggestions.
    """
    formatted_items = "\n".join(f"- '{item}'" for item in items)
    prompt_with_items = f"{base_prompt}\n{formatted_items}"

    if custom_instructions:
        prompt_with_items += f"\n\n{custom_instructions}"

    return prompt_with_items


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
        old_path = directory / original_rel_path
        new_path = directory / new_rel_path

        if old_path == new_path:
            print(f"Item does not need to be renamed: {old_path}")

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

        try:
            new_path.parent.mkdir(parents=True, exist_ok=True)

            # Handling directory renaming
            if old_path.is_dir():
                # Creating new directory structure if it doesn't exist
                new_path.mkdir(parents=True, exist_ok=True)

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

    if not renaming_map:
        raise ValueError("No renaming map provided.")

    if confirm_renaming():
        try:
            rename_items(directory, renaming_map)
        except OSError as error:
            print(f"Error during renaming: {error}")
    else:
        print("Renaming operation cancelled.")
