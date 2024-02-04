from pathlib import Path
from typing import Dict, List, Union

import clipboard

INSTRUCTION = """
Please suggest clean names for the following items. The output should be in a codeblock in a python dict where you have 
the keys as the old names and the values as the new names. Do not generate anything else.\n
"""


def list_directory_items(
    directory_path: Union[str, Path], depth: int = -1, include_files: bool = True, include_folders: bool = True
) -> List[str]:
    """
    List the contents of a given directory up to a specified depth, including files and/or folders as specified.

    This function traverses the directory specified by `directory_path` and lists its contents.
    The depth parameter controls how deep the function goes into subdirectories.
    A depth of -1 implies no limit on depth.

    Args:
        directory_path (Union[str, Path]): The path of the directory to list. Can be a string or a Path object.
        depth (int): Maximum depth for subdirectory traversal; -1 for unlimited depth. Default is -1.
        include_files (bool): If True, include files in the output. Default is True.
        include_folders (bool): If True, include folders in the output. Default is True.

    Returns:
        List[str]: A list of relative paths of the directory's contents, filtered based on the specified parameters.
    """
    directory_path = Path(directory_path) if isinstance(directory_path, str) else directory_path
    items = []

    for item in directory_path.rglob("*"):  # Use rglob to recursively list all items
        if should_include_item(
            item=item,
            directory_path=directory_path,
            depth=depth,
            include_files=include_files,
            include_folders=include_folders,
        ):
            items.append(str(item.relative_to(directory_path)))

    return items


def should_include_item(
    item: Path, directory_path: Path, depth: int, include_files: bool, include_folders: bool
) -> bool:
    """
    Determine if an item should be included in the listing based on its type and depth relative to the base directory.

    Args:
        item (Path): The Path object of the item to check.
        directory_path (Path): The base directory for depth calculation.
        depth (int): Specified depth limit for inclusion.
        include_files (bool): Flag to consider files for inclusion.
        include_folders (bool): Flag to consider folders for inclusion.

    Returns:
        bool: True if the item meets the specified criteria, False otherwise.
    """
    # Calculate item's depth relative to the base directory
    item_depth = len(item.relative_to(directory_path).parts)
    # Check if item meets depth condition
    depth_condition = depth == -1 or item_depth <= depth

    # Check file and folder conditions based on flags
    file_condition = include_files and item.is_file()
    folder_condition = include_folders and item.is_dir()

    return depth_condition and (file_condition or folder_condition)


def compose_llm_prompt(items: List[str], custom_instruction: str = "", initial_instruction: str = INSTRUCTION) -> str:
    """
    Composes a prompt for a Language Learning Model (LLM) to generate renaming suggestions.

    Constructs a structured prompt to be used with an LLM by including a list of current file and
    directory names (items) and any additional custom instructions for renaming.
    The initial_instruction sets the context for the LLM.

    Args:
        items (List[str]): Names of files and directories to be renamed.
        custom_instruction (str, optional): Additional guidelines or rules for renaming. Defaults to "".
        initial_instruction (str, optional): Base text of the prompt, establishing context for the LLM. Defaults to INSTRUCTION.

    Returns:
        str: The complete LLM prompt, combining base text, file/directory names, and custom instructions.

    """
    # Format each item for inclusion in the prompt
    formatted_items = "\n".join(f"- '{item}'" for item in items)
    prompt_with_items = f"{initial_instruction}\n{formatted_items}"

    # Append custom instructions if provided
    if custom_instruction:
        prompt_with_items += f"\n\n{custom_instruction}"

    return prompt_with_items


def generate_llm_prompt(
    directory_path: Union[str, Path],
    depth: int,
    include_files: bool,
    include_folders: bool,
    copy_prompt_to_clipboard: bool = False,
    print_prompt: bool = False,
    custom_instruction: str = "",
    initial_instruction: str = INSTRUCTION,
):
    """
    Create and optionally output a Language Learning Model (LLM) prompt for file and directory renaming suggestions.

    This function compiles a list of relevant items in the specified directory and composes a prompt
    for renaming suggestions using an LLM. The prompt can then be printed and/or copied to the clipboard based
    on user preference.

    Args:
        directory_path (Union[str, Path]): The path of the directory from which to list items.
        depth (int): Maximum depth for subdirectory traversal; -1 for unlimited depth.
        include_files (bool): Include files in the listing if True.
        include_folders (bool): Include directories in the listing if True.
        copy_prompt_to_clipboard (bool, optional): Copy the generated prompt to the clipboard if True. Defaults to False.
        print_prompt (bool, optional): Print the generated prompt to the console if True. Defaults to False.
        custom_instruction (str, optional): Additional instructions for the prompt. Defaults to an empty string.
        initial_instruction (str, optional): Base text for the prompt. Defaults to a predefined prompt text.

    Returns:
        str: The generated LLM prompt for renaming suggestions.
    """
    items = list_directory_items(
        directory_path=directory_path,
        depth=depth,
        include_files=include_files,
        include_folders=include_folders,
    )

    prompt = compose_llm_prompt(
        items=items,
        custom_instruction=custom_instruction,
        initial_instruction=initial_instruction,
    )

    if print_prompt:
        print(prompt)

    if copy_prompt_to_clipboard:
        clipboard.copy(prompt)

    return prompt


def confirm_renaming() -> bool:
    """
    Prompt the user for confirmation before proceeding with renaming operations.

    Returns:
        bool: True if the user confirms, False otherwise.
    """
    confirmation = input("Confirm renaming (yes/y to confirm): ").strip().lower()
    return confirmation in ["y", "yes"]


def execute_bulk_renaming(directory_path: Union[str, Path], renaming_map: Dict[str, str]) -> None:
    """
    Execute renaming of multiple files and directories based on the provided renaming map.

    Args:
        directory_path (Union[str, Path]): The base directory from which relative paths in the renaming map are calculated.
        renaming_map (Dict[str, str]): A dictionary mapping original names (relative paths) to new names.

    Note:
        The renaming process handles each item in descending order of path depth to ensure that parent
        directories are renamed after their contents.
    """
    directory_path = Path(directory_path) if isinstance(directory_path, str) else directory_path

    # Sort items in reverse order of path depth to rename deeper items first
    sorted_items = sorted(renaming_map.items(), key=lambda item: len(Path(item[0]).parts), reverse=True)

    # Loop through each item and perform renaming
    for original_rel_path, new_rel_path in sorted_items:
        execute_item_renaming(directory_path, original_rel_path, new_rel_path)


def execute_item_renaming(directory_path: Union[str, Path], original_rel_path: str, new_rel_path: str) -> None:
    """
    Perform the renaming of a single item within a directory.

    This function renames an individual file or directory from its original name to a new name.
    It ensures that the renaming process is safe by checking for conflicts and existence before
    attempting to rename.

    Args:
        directory_path (Union[str, Path]): The base directory for the renaming operation.
        original_rel_path (str): The original relative path of the item to be renamed.
        new_rel_path (str): The new relative path for the item.

    Note:
        Renaming is skipped if the old and new paths are identical or if the target name already exists.
        Errors during the renaming process are caught and reported.
    """
    directory_path = Path(directory_path) if isinstance(directory_path, str) else directory_path

    old_path = directory_path / original_rel_path
    new_path = directory_path / new_rel_path

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


def rename_items_with_checks(directory_path: Union[str, Path], renaming_map: Dict[str, str]) -> None:
    """
    Coordinate the renaming process of items in a directory, with validation and user confirmation.

    Args:
        directory_path (Union[str, Path]): The directory containing items to be renamed.
        renaming_map (Dict[str, str]): A mapping of original names to new, clean names.

    Raises:
        ValueError: If the renaming map is empty.

    Note:
        This function integrates user confirmation and error handling to provide a safe renaming operation.
    """
    directory_path = Path(directory_path) if isinstance(directory_path, str) else directory_path

    if not renaming_map:
        raise ValueError("No renaming map provided.")

    # Confirm with the user before proceeding with renaming
    if confirm_renaming():
        try:
            execute_bulk_renaming(directory_path, renaming_map)
        except OSError as error:
            print(f"Error during renaming: {error}")
    else:
        print("Renaming operation cancelled.")
