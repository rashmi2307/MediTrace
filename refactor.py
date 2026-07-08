import sys
with open('frontend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if 'st.markdown(\'<div id="printable-area">\'' in line:
        start_idx = i
    if start_idx != -1 and 'st.markdown(\'</div>\'' in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_lines = []
    new_lines.extend(lines[:start_idx])
    
    indent = lines[start_idx][:len(lines[start_idx]) - len(lines[start_idx].lstrip())]
    new_lines.append(indent + '# Wrap the printable area in a container\n')
    new_lines.append(indent + 'report_container = st.container()\n')
    new_lines.append(indent + 'with report_container:\n')
    new_lines.append(indent + '    st.markdown(\'<span id="pdf-marker" style="display:none;"></span>\', unsafe_allow_html=True)\n')
    
    for i in range(start_idx + 1, end_idx):
        if lines[i].strip() == '':
            new_lines.append('\n')
        else:
            new_lines.append('    ' + lines[i])
            
    new_lines.extend(lines[end_idx + 1:])
    
    with open('frontend/app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print('Successfully updated the container block.')
else:
    print('Failed to find block boundaries.')
