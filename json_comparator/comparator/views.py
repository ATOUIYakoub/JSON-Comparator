from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from difflib import ndiff


def compare_json_logic(json1_data, json2_data):
    result = {
        "added": {},
        "removed": {},
        "changed": {},
        "updated_json1": [],
        "highlighted_json2": []
    }

    # Step 1: Add unique IDs and depth to both JSON structures
    add_ids_to_sections(json1_data)
    add_ids_to_sections(json2_data)

    # Step 2: Find equivalents and handle missing sections by adding empty ones
    correspondences = find_section_equivalents(json1_data, json2_data)

    for correspondence in correspondences:
        result["updated_json1"].append(correspondence["json1"])
        result["highlighted_json2"].append(correspondence["json2"])

    return result


def compare_subsections(subsections1, subsections2):
    updated_subsections = []

    for subsection1 in subsections1:
        matched_subsection = next((subsec for subsec in subsections2 if subsec["Titre"] == subsection1["Titre"]), None)
        if matched_subsection:
            if subsection1["Text"] != matched_subsection["Text"]:
                subsection1["Text"] = highlight_differences(subsection1["Text"], matched_subsection["Text"])
            subsection1["sub_sections"] = compare_subsections(subsection1["sub_sections"], matched_subsection["sub_sections"])
        updated_subsections.append(subsection1)

    for subsection2 in subsections2:
        if not any(subsec["Titre"] == subsection2["Titre"] for subsec in subsections1):
            highlighted_subsection = {
                "Titre": f'<span style="background-color: lightgreen;">{subsection2["Titre"]}</span>',
                "Text": f'<span style="background-color: lightgreen;">{subsection2["Text"]}</span>',
                "sub_sections": []
            }
            updated_subsections.append(highlighted_subsection)

    return updated_subsections


@csrf_exempt
def compare_json(request):
    if request.method == "POST":
        json1_file = request.FILES.get('json1')
        json2_file = request.FILES.get('json2')

        if not json1_file or not json2_file:
            return JsonResponse({'error': 'Both JSON files are required'}, status=400)

        try:
            json1_data = json.load(json1_file)
            json2_data = json.load(json2_file)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        result = compare_json_logic(json1_data, json2_data)

        with open('updated_json1.json', 'w', encoding='utf-8') as f:
            json.dump(result["updated_json1"], f, ensure_ascii=False, indent=4)

        with open('highlighted_json2.json', 'w', encoding='utf-8') as f:
            json.dump(result["highlighted_json2"], f, ensure_ascii=False, indent=4)

        return JsonResponse({'message': 'Comparison completed successfully, and files have been saved.'}, safe=False)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# Function to highlight differences between two strings at the character level
def highlight_differences(original, updated, color_removed="lightcoral", color_added="lightgreen"):
    diff = list(ndiff(original, updated))
    result_html = ""

    for char in diff:
        if char.startswith("-"):  # Removed in the updated version
            result_html += f'<span style="background-color: {color_removed};">{char[2:]}</span>'
        elif char.startswith("+"):  # Added in the updated version
            result_html += f'<span style="background-color: {color_added};">{char[2:]}</span>'
        else:  # Unchanged characters
            result_html += char[2:]

    return result_html


# Function to add unique IDs and depth to sections
def add_ids_to_sections(sections, prefix="", depth=0):
    for index, section in enumerate(sections):
        section_id = f"{prefix}{index + 1}"
        section["id"] = section_id
        section["depth"] = depth
        if "sub_sections" in section:
            add_ids_to_sections(section["sub_sections"], prefix=f"{section_id}.", depth=depth + 1)


# Function to generate an empty section with white spaces for missing sections
def generate_empty_section(section):
    empty_section = {}
    for key, value in section.items():
        if isinstance(value, str):
            empty_section[key] = " " * len(value)  # Replace strings with equivalent whitespace
        elif isinstance(value, list):
            empty_section[key] = [generate_empty_section(sub_section) for sub_section in value]
        else:
            empty_section[key] = value
    return empty_section


# Function to compare and highlight differences in sections
def highlight_differences_in_section(section1, section2):
    section1["Titre"] = highlight_differences(section1["Titre"], section2["Titre"])
    section1["Text"] = highlight_differences(section1["Text"], section2["Text"])


# Function to find equivalents and handle missing sections by adding empty ones
def find_section_equivalents(json1, json2):
    correspondences = []

    def find_equivalent_for_section(section, candidates):
        for candidate in candidates:
            if section["Titre"].strip() == candidate["Titre"].strip() and section["Text"].strip() == candidate["Text"].strip():
                return candidate
        return None

    def match_sections(sections1, sections2):
        for section in sections1:
            equivalent_section = find_equivalent_for_section(section, sections2)
            if equivalent_section:
                highlight_differences_in_section(section, equivalent_section)
            correspondences.append({
                "json1": section,
                "json2": equivalent_section if equivalent_section else generate_empty_section(section),
                "depth": section["depth"]
            })
            if equivalent_section:
                sections2.remove(equivalent_section)
            if "sub_sections" in section:
                match_sections(section["sub_sections"], equivalent_section["sub_sections"] if equivalent_section else [])

        for remaining_section in sections2:
            correspondences.append({
                "json1": generate_empty_section(remaining_section),
                "json2": remaining_section,
                "depth": remaining_section["depth"]
            })

    match_sections(json1, json2)
    return correspondences
