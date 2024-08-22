from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import difflib

def highlight_text(text, color="lightgreen"):
    return f'<span style="background-color: {color};">{text}</span>'

def add_empty_subsections(section):
    return {
        "Titre": "         ",
        "Text": "                                     ",
        "sub_sections": [add_empty_subsections(sub) for sub in section["sub_sections"]]
    }

def highlight_differences(text1, text2):
    differ = difflib.Differ()
    diff = list(differ.compare(text1.split(), text2.split()))
    highlighted_text = []
    for part in diff:
        if part.startswith('+ '):
            highlighted_text.append(highlight_text(part[2:]))
        elif part.startswith('  ') or part.startswith('- '):
            highlighted_text.append(part[2:])
    return ' '.join(highlighted_text)

def highlight_all_subsections(section):
    section["Titre"] = highlight_text(section["Titre"])
    section["Text"] = highlight_text(section["Text"])
    for sub in section["sub_sections"]:
        highlight_all_subsections(sub)
    return section

def compare_and_update_sections(sections1, sections2):
    updated_sections1 = []
    updated_sections2 = sections2.copy()

    for section1 in sections1:
        matched_section = next((sec for sec in sections2 if sec["Titre"] == section1["Titre"]), None)
        if matched_section:
            if section1["Text"] != matched_section["Text"]:
                matched_section["Text"] = highlight_differences(section1["Text"], matched_section["Text"])
            section1["sub_sections"], matched_section["sub_sections"] = compare_and_update_sections(section1["sub_sections"], matched_section["sub_sections"])
        else:
            empty_section = add_empty_subsections(section1)
            updated_sections2.append(empty_section)
            section1 = highlight_all_subsections(section1)
        updated_sections1.append(section1)

    for section2 in sections2:
        if not any(sec["Titre"] == section2["Titre"] for sec in sections1):
            empty_section = add_empty_subsections(section2)
            updated_sections1.append(empty_section)
            section2 = highlight_all_subsections(section2)
            updated_sections2.append(section2)

    return updated_sections1, updated_sections2

def compare_json_logic(json1_data, json2_data):
    updated_json1 = json1_data.copy()
    updated_json2 = json2_data.copy()

    updated_json1[0]["sub_sections"], updated_json2[0]["sub_sections"] = compare_and_update_sections(json1_data[0]["sub_sections"], json2_data[0]["sub_sections"])

    return updated_json1, updated_json2

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

        updated_json1, updated_json2 = compare_json_logic(json1_data, json2_data)

        with open('json1result.json', 'w', encoding='utf-8') as f:
            json.dump(updated_json1, f, ensure_ascii=False, indent=4)

        with open('json2result.json', 'w', encoding='utf-8') as f:
            json.dump(updated_json2, f, ensure_ascii=False, indent=4)

        return JsonResponse({'message': 'Comparison completed successfully, and files have been saved.'}, safe=False)

    return JsonResponse({'error': 'Invalid request method'}, status=405)