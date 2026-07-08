def clean_html(html_str: str) -> str:
    return "\n".join([line.strip() for line in html_str.split("\n")])

def parse_markdown_report(report_text: str):
    sections = {}
    current_section = None
    current_lines = []
    
    for line in report_text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(current_lines).strip()
            current_section = stripped[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
            
    if current_section:
        sections[current_section] = '\n'.join(current_lines).strip()
        
    return sections

def parse_interaction_cards(section_text: str):
    if not section_text or section_text.strip() == "None":
        return []
        
    cards = []
    current_card = None
    lines = section_text.split('\n')
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('### '):
            if current_card:
                cards.append(current_card)
            current_card = {
                "pair": stripped[4:].strip(),
                "severity": "",
                "source": "",
                "explanation": "",
                "reactions": [],
                "recommendation": ""
            }
        elif current_card:
            if stripped.startswith("**Severity:**"):
                current_card["severity"] = stripped.replace("**Severity:**", "").strip()
            elif stripped.startswith("**Source:**"):
                current_card["source"] = stripped.replace("**Source:**", "").strip()
            elif stripped.startswith("**Explanation:**"):
                current_card["explanation"] = stripped.replace("**Explanation:**", "").strip()
            elif stripped.startswith("- ") and not stripped.startswith("**"):
                current_card["reactions"].append(stripped[2:].strip())
            elif stripped.startswith("**Recommended Action:**"):
                current_card["recommendation"] = stripped.replace("**Recommended Action:**", "").strip()
                
    if current_card:
        cards.append(current_card)
        
    return cards

def parse_medications(meds_text: str):
    meds = []
    for line in meds_text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('- '):
            meds.append(stripped[2:].strip())
    return meds
