import os
import re
import sys

def process_icon(input_path, output_path, circle_color):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        with open(input_path, 'r') as f:
            raw_content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_path} not found.")
        return

    # 1. Extract ALL paths that aren't "fill=none"
    # This regex looks for path tags and captures the 'd' attribute
    path_entries = re.findall(r'<path[^>]+d="([^"]+)"', raw_content)
    
    # Filter out the "spacer" paths (Google often uses them for padding)
    # We keep paths only if the full tag doesn't contain fill="none"
    valid_paths = []
    all_path_tags = re.findall(r'(<path[^>]+>)', raw_content)
    for i, tag in enumerate(all_path_tags):
        if 'fill="none"' not in tag:
            # Get the 'd' attribute from this specific valid tag
            d_attr = re.search(r'd="([^"]+)"', tag)
            if d_attr:
                valid_paths.append(d_attr.group(1))

    if not valid_paths:
        print(f"No visible paths found in {input_path}")
        return

    # 2. Parse ViewBox
    vb_match = re.search(r'viewBox="([-0-9.]+) ([-0-9.]+) ([-0-9.]+) ([-0-9.]+)"', raw_content)
    if vb_match:
        min_x, min_y, vb_w, vb_h = map(float, vb_match.groups())
    else:
        min_x, min_y, vb_w, vb_h = 0, 0, 24, 24 # Default for this icon type

    # 3. Scaling & Centering
    canvas_size = 19
    target_icon_size = 13.0 
    scale = target_icon_size / max(vb_w, vb_h)
    
    offset_x = (canvas_size - (vb_w * scale)) / 2
    offset_y = (canvas_size - (vb_h * scale)) / 2
    translate_x = offset_x - (min_x * scale)
    translate_y = offset_y - (min_y * scale)

    # 4. Build SVG with all valid paths
    path_elements = "\n        ".join([f'<path d="{d}" fill="white" />' for d in valid_paths])
    
    center = canvas_size / 2
    template = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{canvas_size}" height="{canvas_size}" viewBox="0 0 {canvas_size} {canvas_size}" xmlns="http://www.w3.org/2000/svg">
    <circle cx="{center}" cy="{center}" r="{center}" fill="white" />
    <circle cx="{center}" cy="{center}" r="{center - 0.5}" fill="{circle_color}" />
    <g transform="translate({translate_x}, {translate_y}) scale({scale})">
        {path_elements}
    </g>
</svg>"""

    with open(output_path, 'w') as f:
        f.write(template)
    
    print(f"Success! Processed {len(valid_paths)} paths for {os.path.basename(input_path)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
        
    in_file = os.path.join("svgs/material_symbols", sys.argv[1] + ".svg")
    out_file = os.path.join("svgs/svgs_iconset", sys.argv[1] + ".svg")
    color = sys.argv[2] if len(sys.argv) > 2 else "#D31515"

    process_icon(in_file, out_file, color)