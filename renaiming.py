from pathlib import Path
from typing import Dict, List, Union

PROMPT = """
Please suggest clean names for the following items. The output should be in a codeblock in a python dict where you have 
the keys as the old names and the values as the new names:\n
"""


def list_directory_items(
    directory: Union[str, Path], depth: int = -1, include_files: bool = True, include_folders: bool = True
) -> List[str]:
    """
    List the contents of a given directory up to a specified depth, optionally including files and/or folders.

    Args:
        directory (Union[str, Path]): The path of the directory to list. Can be a string or a Path object.
        depth (int): Maximum depth for subdirectory traversal; use -1 for unlimited depth. Default is -1.
        include_files (bool): Flag to include files in the output. Default is True.
        include_folders (bool): Flag to include folders in the output. Default is True.

    Returns:
        List[str]: List of relative paths of the directory's contents, filtered based on the given parameters.
    """
    directory = Path(directory) if isinstance(directory, str) else directory
    items = []

    for item in directory.rglob("*"):  # Use rglob to recursively list all items
        if should_include_item(
            item=item,
            base_directory=directory,
            depth=depth,
            include_files=include_files,
            include_folders=include_folders,
        ):
            items.append(str(item.relative_to(directory)))

    return items


def should_include_item(
    item: Path, base_directory: Path, depth: int, include_files: bool, include_folders: bool
) -> bool:
    """
    Determine if an item should be included in the listing based on its type and depth relative to the base directory.

    Args:
        item (Path): The Path object of the item to check.
        base_directory (Path): The base directory for depth calculation.
        depth (int): Specified depth limit for inclusion.
        include_files (bool): Flag to consider files for inclusion.
        include_folders (bool): Flag to consider folders for inclusion.

    Returns:
        bool: True if the item meets the specified criteria, False otherwise.
    """
    # Calculate item's depth relative to the base directory
    item_depth = len(item.relative_to(base_directory).parts)
    # Check if item meets depth condition
    depth_condition = depth == -1 or item_depth <= depth

    # Check file and folder conditions based on flags
    file_condition = include_files and item.is_file()
    folder_condition = include_folders and item.is_dir()

    return depth_condition and (file_condition or folder_condition)


def generate_llm_prompt(items: List[str], custom_instructions: str = "", base_prompt: str = PROMPT) -> str:
    """
    Generate a custom LLM prompt for renaming suggestions based on a list of file and directory names.

    Args:
        items (List[str]): List of file and directory names for which renaming suggestions are sought.
        custom_instructions (str): Additional instructions to include in the prompt. Default is an empty string.
        base_prompt (str): Base text for the prompt. Default is a predefined prompt text.

    Returns:
        str: A fully formatted LLM prompt including the items and any custom instructions.
    """
    # Format each item for inclusion in the prompt
    formatted_items = "\n".join(f"- '{item}'" for item in items)
    prompt_with_items = f"{base_prompt}\n{formatted_items}"

    # Append custom instructions if provided
    if custom_instructions:
        prompt_with_items += f"\n\n{custom_instructions}"

    return prompt_with_items


def confirm_renaming() -> bool:
    """
    Prompt the user for confirmation before proceeding with renaming operations.

    Returns:
        bool: True if the user confirms, False otherwise.
    """
    confirmation = input("Confirm renaming (yes/y to confirm): ").strip().lower()
    return confirmation in ["y", "yes"]


def execute_bulk_renaming(directory: Path, renaming_map: Dict[str, str]) -> None:
    """
    Execute renaming of multiple files and directories based on the provided renaming map.

    Args:
        directory (Path): The base directory from which relative paths in the renaming map are calculated.
        renaming_map (Dict[str, str]): A dictionary mapping original names (relative paths) to new names.

    Note:
        The renaming process handles each item in descending order of path depth to ensure that parent
        directories are renamed after their contents.
    """
    # Sort items in reverse order of path depth to rename deeper items first
    sorted_items = sorted(renaming_map.items(), key=lambda item: len(Path(item[0]).parts), reverse=True)

    # Loop through each item and perform renaming
    for original_rel_path, new_rel_path in sorted_items:
        execute_item_renaming(directory, original_rel_path, new_rel_path)


def execute_item_renaming(directory: Path, original_rel_path: str, new_rel_path: str) -> None:
    """
    Perform the renaming of a single item within a directory.

    Args:
        directory (Path): The base directory for the renaming operation.
        original_rel_path (str): The original relative path of the item to be renamed.
        new_rel_path (str): The new relative path for the item.

    Note:
        This function handles individual rename operations, checking for conflicts and existence
        before attempting to rename.
    """
    old_path = directory / original_rel_path
    new_path = directory / new_rel_path

    # Check if renaming is necessary
    if old_path == new_path:
        print(f"Item does not need to be renamed: {old_path}")
        return

    # Check for the existence of the item
    if not old_path.exists():
        print(f"Item not found: {old_path}")
        return

    # Check if the target name already exists
    if new_path.exists():
        print(f"Skipping: {new_path} already exists.")
        return

    # Attempt to rename, handling exceptions
    try:
        new_path.parent.mkdir(parents=True, exist_ok=True)
        old_path.rename(new_path)
        print(f"Renamed '{old_path}' to '{new_path}'")
    except OSError as error:
        print(f"Error renaming '{old_path}': {error}")


def rename_items_with_checks(directory: Union[str, Path], renaming_map: Dict[str, str]) -> None:
    """
    Coordinate the renaming process of items in a directory, with validation and user confirmation.

    Args:
        directory (Union[str, Path]): The directory containing items to be renamed.
        renaming_map (Dict[str, str]): A mapping of original names to new, clean names.

    Raises:
        ValueError: If the renaming map is empty.

    Note:
        This function integrates user confirmation and error handling to provide a safe renaming operation.
    """
    directory = Path(directory) if isinstance(directory, str) else directory

    if not renaming_map:
        raise ValueError("No renaming map provided.")

    # Confirm with the user before proceeding with renaming
    if confirm_renaming():
        try:
            execute_bulk_renaming(directory, renaming_map)
        except OSError as error:
            print(f"Error during renaming: {error}")
    else:
        print("Renaming operation cancelled.")
