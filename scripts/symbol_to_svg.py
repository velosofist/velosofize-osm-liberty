import os
import re
import sys

def process_icon(input_path, output_path, circle_color):
    # Ensure the directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    try:
        with open(input_path, 'r') as f:
            raw_content = f.read()
    except FileNotFoundError:
        print(f"Error: The file {input_path} was not found.")
        return

    # 1. Extract the path data
    path_match = re.search(r'<path[^>]*d="([^"]+)"[^>]*/>', raw_content)
    if not path_match:
        print(f"Could not find path data in {input_path}")
        return
    
    path_d = path_match.group(1)

    # 2. Calculate Scaling for 19x19
    # 960 * 0.018 = 17.28 units (leaving a small buffer in the 19x19 canvas)
    scale = 0.018
    canvas_size = 19
    center = canvas_size / 2 # 9.5
    
    # 3. Calculate Centering
    # Width at scale: 960 * 0.018 = 17.28
    # Offset: (19 - 17.28) / 2 = 0.86
    translate_x = (canvas_size - (960 * scale)) / 2
    # Compensate for the Y coordinate starting at -960
    translate_y = translate_x + (960 * scale) 

    # 4. Build the final SVG (19x19)
    template = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{canvas_size}" height="{canvas_size}" viewBox="0 0 {canvas_size} {canvas_size}" xmlns="http://www.w3.org/2000/svg">
    <circle cx="{center}" cy="{center}" r="{center}" fill="white" />
    
    <circle cx="{center}" cy="{center}" r="{center - 0.5}" fill="{circle_color}" />
    
    <g transform="translate({translate_x}, {translate_y}) scale({scale})">
        <path d="{path_d}" fill="white" />
    </g>
</svg>"""

    with open(output_path, 'w') as f:
        f.write(template)
    
    print(f"Success! Icon processed with color {circle_color} and saved to {output_path}")

if __name__ == "__main__":
    # Check if arguments are provided, otherwise use defaults
    # Usage: python3 scripts/symbol_to_svg.py <icon name in sprite> <fill colour>
    in_file = os.path.join("svgs/material_symbols", sys.argv[1] + ".svg")
    out_file = os.path.join("svgs/svgs_iconset", sys.argv[1] + ".svg")
    color = sys.argv[2] if len(sys.argv) > 2 else "#D31515"

    process_icon(in_file, out_file, color)