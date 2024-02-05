# 🗂️ `renAIming`

`renaiming` is a versatile Python utility designed to enhance your digital workspace. It offers the flexibility to streamline the renaming of files and directories and, if desired, can also update their structure. This adaptability is powered by Language Learning Models (LLMs), which, through custom prompts, can intelligently generate intuitive, clean names or suggest organizational improvements to suit your specific needs.

## Usage

1. **Directory Setup:** Begin by specifying the directory that contains the files or directories you wish to rename. 
2. **Prompt Generation:** The script automatically generates prompts based on the existing names of your files. Use these prompts with ChatGPT to obtain suggestions for more descriptive and cleaner names. 
3. **Execute Renaming:** After compiling a list of the suggested names, input them into the script. It will then proceed to rename the items in your directory, post your confirmation.

With `renaiming`, managing and organizing your digital files becomes a streamlined and user-friendly process.

## Requirements

- Python 3.6 or higher.
- Access to ChatGPT or similar service for generating name suggestions.

## Installation

```
pip install git+https://github.com/thomashirtz/renaiming#egg=renaiming
```

## Examples

### Streamlining a Movie Collection

<details open>
  <summary><b>Details</b></summary>

This example demonstrates how `renaiming` can be utilized to simplify a cluttered movie collection. The goal is to flatten the directory structure and standardize the naming convention for a more organized movie library.

#### Original Directory Structure

Consider the following complex and inconsistently named movie files nested in various folders:

```
/movies
    /Unsorted Movies
        - 'The.Matrix[1999]1080p.mkv'
        - 'Inception.2010.HD.mp4'
    /New Folder
        /Sci-Fi
            - 'Arrival_Film_2016.avi'
    /Classics
        - 'The_Godfather(1972).mp4'
```

#### Desired Outcome

We aim to move all movies to the `/movies` directory with a neater and more uniform naming format:

```
/movies
    - 'The Matrix (1999).mkv'
    - 'Inception (2010).mp4'
    - 'Arrival (2016).avi'
    - 'The Godfather (1972).mp4'
```

#### Script part 1

`renAIming` includes functionalities for both renaming and relocating files.

Here is the script overview :

```python
from renaiming import generate_llm_prompt

directory = r"\movies"

instructions = """
Keep year in parenthesis. Examples:
- 'Movie.Title.2020.mkv' => 'Movie Title (2020)'
- 'Document_2021.pdf' => 'Document (2021)'
"""

# Generate a prompt for LLM to suggest new names for the items
prompt = generate_llm_prompt(
    directory_path=directory,
    depth=-1,
    include_folders=True,
    include_files=True,
    copy_prompt_to_clipboard=True,
    custom_instruction=instructions,
)

print(prompt)
```

#### Prompt & LLM Answer

This gives the following LLM prompt :
```
Please suggest clean names for the following items. The output should be in a codeblock in a python dict where you have 
the keys as the old names and the values as the new names:


- 'Classics\The_Godfather(1972).mp4.txt'
- 'New Folder\Sci-Fi\Arrival_Film_2016.avi.txt'
- 'Unsorted Movies\Inception.2010.HD.mp4.txt'
- 'Unsorted Movies\The.Matrix[1999]1080p.mkv.txt'


Keep year in parenthesis. Remove folder nesting. Examples:
- 'Folder/Movie.Title.2020.mkv' => 'Movie Title (2020).mkv'
- 'Serie_2021.pdf' => 'Serie (2021).pdf'
```

When giving that to ChatGPT, we get the following answer:
```python
renaming_map = {
    'Classics\\The_Godfather(1972).mp4': 'The Godfather (1972).mp4',
    'New Folder\\Sci-Fi\\Arrival_Film_2016.avi': 'Arrival (2016).avi',
    'Unsorted Movies\\Inception.2010.HD.mp4': 'Inception (2010).mp4',
    'Unsorted Movies\\The.Matrix[1999]1080p.mkv': 'The Matrix (1999).mkv'
}
```

#### Script part 2

Finally, after checking that everything seems good, we do that:

```python
from renaiming import rename_items_with_checks

directory = r"\movies"
renaming_map = {
    'Classics\\The_Godfather(1972).mp4': 'The Godfather (1972).mp4',
    'New Folder\\Sci-Fi\\Arrival_Film_2016.avi': 'Arrival (2016).avi',
    'Unsorted Movies\\Inception.2010.HD.mp4': 'Inception (2010).mp4',
    'Unsorted Movies\\The.Matrix[1999]1080p.mkv': 'The Matrix (1999).mkv'
}

# Execute the renaming process using the specified renaming map
rename_items_with_checks(directory_path=directory, renaming_map=renaming_map)
```

This enhanced script functionality not only renames the files but also relocates them to a specified target directory, in this case, flattening the structure to have all movies directly under `/movies`.

</details>

## Caution

Always ensure that you have backups of your data before running this script. Renaming files and directories can be a destructive operation if not handled carefully.

## License

     Copyright 2024 Thomas Hirtz

     Licensed under the Apache License, Version 2.0 (the "License");
     you may not use this file except in compliance with the License.
     You may obtain a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

     Unless required by applicable law or agreed to in writing, software
     distributed under the License is distributed on an "AS IS" BASIS,
     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
     See the License for the specific language governing permissions and
     limitations under the License.

