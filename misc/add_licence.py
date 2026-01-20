import os
import gzip
import json
import tempfile
import argparse
from pathlib import Path
from typing import Any

LICENSE_TEMPLATES = {
    "apache": """This file is part of QOBLIB - Quantum Optimization Benchmarking Library
Licensed under the Apache License, Version 2.0 (the \"License\");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an \"AS IS\" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.""",

    "ccby": """This file is part of QOBLIB - Quantum Optimization Benchmarking Library
Licensed under the Creative Commons Attribution 4.0 International License.
You may obtain a copy of the License at

    https://creativecommons.org/licenses/by/4.0/

You are free to share and adapt the material for any purpose, even commercially,
as long as you give appropriate credit and indicate if changes were made.""",
}

# ------------------------------------------------------------------ #
# Helper functions                                                    #
# ------------------------------------------------------------------ #

def _comment_out(text: str, extension: str) -> str:
    """Return *text* wrapped in suitable comment delimiters for the given
    *extension*. Handles C‑style, XML, and hash comments."""
    c_style_block = {".rs", ".c", ".cpp", ".h", ".java", ".js"}

    if extension == ".xml":
        return f"<!--\n{text}\n-->"
    elif extension in c_style_block:
        return f"/*\n{text}\n*/"
    else:
        return "\n".join(f"# {line}" for line in text.splitlines())


# --------------------------- Text files --------------------------- #

def _prepend_notice_to_text_file(file_path: Path, notice: str) -> None:
    with file_path.open("r", encoding="utf-8") as f:
        content = f.read()

    if any(phrase in content for phrase in ("QOBLIB", "Apache License", "Creative Commons")):
        return  # Already licensed

    with file_path.open("w", encoding="utf-8") as f:
        f.write(notice + "\n\n" + content)


# --------------------------- JSON files --------------------------- #

def _prepend_notice_to_json(file_path: Path, license_text: str) -> None:
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data: Any = json.load(f)
    except json.JSONDecodeError:
        return  # Skip invalid JSON

    if isinstance(data, dict) and any(k in data for k in ("_license", "license", "__license__")):
        return

    new_data = {"_license": license_text, **data} if isinstance(data, dict) else {"_license": license_text, "data": data}

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
        f.write("\n")


# --------------------------- XML files --------------------------- #

def _prepend_notice_to_xml(file_path: Path, notice: str) -> None:
    with file_path.open("r", encoding="utf-8") as f:
        content = f.read()

    if any(phrase in content for phrase in ("QOBLIB", "Apache License", "Creative Commons")):
        return  # Already licensed

    stripped = content.lstrip()
    if stripped.startswith("<?xml"):
        decl_end = content.find("?>")
        if decl_end != -1:
            decl_end += 2  # Include '?>'
            new_content = content[:decl_end] + "\n" + notice + "\n" + content[decl_end:].lstrip("\n")
        else:
            new_content = notice + "\n\n" + content
    else:
        new_content = notice + "\n\n" + content

    with file_path.open("w", encoding="utf-8") as f:
        f.write(new_content)


# ------------------------- .gz containers ------------------------- #

def _process_gzip_file(file_path: Path, license_text: str) -> None:
    """Decompress *file_path* (.gz), add the license to the contained file, and
    recompress in‑place."""
    # Determine the underlying extension (filename without the final .gz)
    underlying_name = Path(file_path.stem)  # removes only the final suffix
    underlying_ext = underlying_name.suffix

    # Read the compressed content
    try:
        with gzip.open(file_path, "rt", encoding="utf-8") as gz:
            content = gz.read()
    except OSError:
        return  # Not text -> skip

    # Bail if license already present
    if any(phrase in content for phrase in ("QOBLIB", "Apache License", "Creative Commons")):
        return

    if underlying_ext == ".json":
        try:
            data: Any = json.loads(content)
        except json.JSONDecodeError:
            return
        if isinstance(data, dict) and any(k in data for k in ("_license", "license", "__license__")):
            return
        updated_data = {"_license": license_text, **data} if isinstance(data, dict) else {"_license": license_text, "data": data}
        new_content = json.dumps(updated_data, indent=2, ensure_ascii=False) + "\n"

    elif underlying_ext == ".xml":
        xml_notice = _comment_out(license_text, ".xml")
        stripped = content.lstrip()
        if stripped.startswith("<?xml"):
            decl_end = content.find("?>")
            if decl_end != -1:
                decl_end += 2
                new_content = content[:decl_end] + "\n" + xml_notice + "\n" + content[decl_end:].lstrip("\n")
            else:
                new_content = xml_notice + "\n\n" + content
        else:
            new_content = xml_notice + "\n\n" + content

    else:
        notice = _comment_out(license_text, underlying_ext or ".txt")
        new_content = notice + "\n\n" + content

    # Write back compressed
    with gzip.open(file_path, "wt", encoding="utf-8") as gz:
        gz.write(new_content)

    print(f"Processed {file_path}")


# ------------------------------------------------------------------ #
# Main CLI                                                            #
# ------------------------------------------------------------------ #

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add license notices to source, JSON, XML, or .gz‑compressed files.")
    parser.add_argument("directory", type=str, help="Parent directory to scan")
    parser.add_argument(
        "extension",
        type=str,
        help="File extension to target (e.g. .py, .rs, .json, .xml). Files ending in <ext>.gz are also handled.")
    parser.add_argument(
        "license",
        type=str,
        choices=["apache", "ccby"],
        help="License template to use",
    )

    args = parser.parse_args()

    # Ensure extension starts with a dot for consistency
    ext = args.extension if args.extension.startswith(".") else f".{args.extension}"
    license_text = LICENSE_TEMPLATES[args.license.lower()]

    # A pre‑built commented notice for non‑JSON/non‑XML text files with *this* ext
    pre_built_notice = _comment_out(license_text, ext) if ext not in {".json", ".xml"} else ""

    for root, _, files in os.walk(args.directory):
        for file in files:
            file_path = Path(root) / file

            # Handle plain files that exactly match the requested extension
            if file.endswith(ext):
                if ext == ".json":
                    _prepend_notice_to_json(file_path, license_text)
                elif ext == ".xml":
                    xml_notice = _comment_out(license_text, ".xml")
                    _prepend_notice_to_xml(file_path, xml_notice)
                else:
                    _prepend_notice_to_text_file(file_path, pre_built_notice)
                print(f"Processed {file_path}")

            # Handle files like *.py.gz, *.json.gz etc. or *everything* if ext==".gz"
            elif file.endswith(".gz") and (
                ext == ".gz" or file[:-3].endswith(ext)
            ):
                _process_gzip_file(file_path, license_text)


if __name__ == "__main__":
    main()
