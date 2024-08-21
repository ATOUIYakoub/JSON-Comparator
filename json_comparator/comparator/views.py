from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os


def compare_json_logic(json1_data, json2_data):
    result = {
        "added": {},
        "removed": {},
        "changed": {},
        "updated_json1": [],
        "highlighted_json2": []
    }

    for section in json1_data:
        matching_section = next((s for s in json2_data if s["Titre"] == section["Titre"]), None)

        if matching_section:
            if section["Text"] != matching_section["Text"]:
                result["changed"][section["Titre"]] = {
                    "original": section["Text"],
                    "new": matching_section["Text"]
                }
                matching_section["Text"] = f'<span style="background-color: lightgreen;">{matching_section["Text"]}</span>'
            section["sub_sections"] = compare_subsections(section["sub_sections"], matching_section["sub_sections"])
            result["updated_json1"].append(section)
            result["highlighted_json2"].append(matching_section)
        else:
            result["updated_json1"].append(section)

    for section in json2_data:
        if section["Titre"] not in [s["Titre"] for s in json1_data]:
            result["added"][section["Titre"]] = section
            result["updated_json1"].append({"Titre": " ", "Text": " ", "sub_sections": []})
            section["Titre"] = f'<span style="background-color: lightgreen;">{section["Titre"]}</span>'
            section["Text"] = f'<span style="background-color: lightgreen;">{section["Text"]}</span>'
            result["highlighted_json2"].append(section)

    return result

def compare_subsections(subsections1, subsections2):
    updated_subsections = []

    for subsection1 in subsections1:
        matched_subsection = next((subsec for subsec in subsections2 if subsec["Titre"] == subsection1["Titre"]), None)
        if matched_subsection:
            if subsection1["Text"] != matched_subsection["Text"]:
                subsection1["Text"] = f'<span style="background-color: lightgreen;">{matched_subsection["Text"]}</span>'
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
