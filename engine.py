# engine.py
import os
import random
from PIL import Image, ImageDraw, ImageFont

# 1. Update your configuration to store explicit variant rules for individual fonts
TOOL_CONFIGS = {
    'pen': {
        'color': (12, 28, 94, 255),
        'variants': [
            {'path': 'assets/pen1.ttf', 'fontsize': 22, 'ybias': 22, 'stroke_width': 0},
            {'path': 'assets/pen2.ttf', 'fontsize': 22, 'ybias': 22, 'stroke_width': 0}
        ]
    },
    'marker': {
        'color': (40, 65, 135, 255),
        'variants': [
            {'path': 'assets/marker1.ttf', 'fontsize': 28, 'ybias': 27, 'stroke_width': 1},     # Normal marker
            {'path': 'assets/marker2.ttf', 'fontsize': 28, 'ybias': 27, 'stroke_width': 1}    # <--- Made this a bit bolder!
        ]
    }
}

MASTER_LINE_COORDINATES = [
    [(50, 186), (90, 186), (130, 186), (170, 186), (210, 186), (250, 186), (290, 187), (330, 187), (370, 188), (410, 188), (450, 188), (490, 188), (530, 188), (570, 187), (610, 187), (650, 186), (690, 186), (730, 186)],
    [(50, 234), (90, 235), (130, 235), (170, 235), (210, 235), (250, 235), (290, 235), (330, 236), (370, 236), (410, 237), (450, 237), (490, 237), (530, 236), (570, 236), (610, 236), (650, 235), (690, 234), (730, 234)],
    [(50, 283), (90, 283), (130, 284), (170, 284), (210, 284), (250, 284), (290, 284), (330, 284), (370, 285), (410, 285), (450, 285), (490, 285), (530, 285), (570, 285), (610, 284), (650, 284), (690, 283), (730, 282)],
    [(50, 332), (90, 332), (130, 332), (170, 332), (210, 332), (250, 333), (290, 333), (330, 333), (370, 334), (410, 334), (450, 334), (490, 334), (530, 333), (570, 333), (610, 333), (650, 332), (690, 331), (730, 330)],
    [(50, 381), (90, 381), (130, 381), (170, 381), (210, 381), (250, 381), (290, 382), (330, 382), (370, 382), (410, 382), (450, 382), (490, 382), (530, 382), (570, 381), (610, 381), (650, 380), (690, 379), (730, 379)],
    [(50, 429), (90, 429), (130, 429), (170, 429), (210, 429), (250, 429), (290, 430), (330, 430), (370, 429), (410, 430), (450, 429), (490, 430), (530, 429), (570, 429), (610, 428), (650, 427), (690, 427), (730, 427)],
    [(50, 478), (90, 477), (130, 477), (170, 477), (210, 477), (250, 477), (290, 477), (330, 477), (370, 478), (410, 477), (450, 477), (490, 477), (530, 477), (570, 476), (610, 476), (650, 476), (690, 475), (730, 474)],
    [(50, 527), (90, 527), (130, 526), (170, 526), (210, 526), (250, 526), (290, 526), (330, 525), (370, 526), (410, 525), (450, 525), (490, 525), (530, 525), (570, 524), (610, 524), (650, 524), (690, 524), (730, 523)],
    [(50, 575), (90, 575), (130, 575), (170, 575), (210, 574), (250, 574), (290, 574), (330, 574), (370, 573), (410, 573), (450, 573), (490, 573), (530, 573), (570, 572), (610, 572), (650, 572), (690, 571), (730, 572)],
    [(50, 625), (90, 624), (130, 623), (170, 623), (210, 623), (250, 622), (290, 622), (330, 622), (370, 622), (410, 621), (450, 621), (490, 621), (530, 621), (570, 621), (610, 620), (650, 620), (690, 620), (730, 620)],
    [(50, 674), (90, 673), (130, 673), (170, 672), (210, 671), (250, 671), (290, 671), (330, 670), (370, 670), (410, 670), (450, 670), (490, 669), (530, 669), (570, 669), (610, 669), (650, 669), (690, 669), (730, 669)],
    [(50, 723), (90, 723), (130, 722), (170, 721), (210, 720), (250, 720), (290, 719), (330, 719), (370, 719), (410, 718), (450, 718), (490, 718), (530, 718), (570, 718), (610, 718), (650, 718), (690, 718), (730, 718)],
    [(50, 773), (90, 772), (130, 771), (170, 770), (210, 770), (250, 769), (290, 769), (330, 768), (370, 768), (410, 768), (450, 768), (490, 768), (530, 768), (570, 768), (610, 767), (650, 767), (690, 767), (730, 767)],
    [(50, 822), (90, 822), (130, 820), (170, 820), (210, 819), (250, 819), (290, 818), (330, 818), (370, 818), (410, 818), (450, 818), (490, 817), (530, 817), (570, 817), (610, 817), (650, 817), (690, 817), (730, 817)],
    [(50, 871), (90, 871), (130, 870), (170, 869), (210, 868), (250, 868), (290, 868), (330, 868), (370, 868), (410, 868), (450, 867), (490, 867), (530, 867), (570, 867), (610, 867), (650, 866), (690, 866), (730, 866)],
    [(50, 921), (90, 920), (130, 919), (170, 919), (210, 918), (250, 918), (290, 918), (330, 918), (370, 918), (410, 918), (450, 918), (490, 918), (530, 917), (570, 917), (610, 917), (650, 916), (690, 916), (730, 916)],
    [(50, 971), (90, 970), (130, 969), (170, 969), (210, 968), (250, 968), (290, 968), (330, 968), (370, 968), (410, 968), (450, 968), (490, 967), (530, 967), (570, 967), (610, 967), (650, 966), (690, 965), (730, 965)],
    [(50, 1020), (90, 1020), (130, 1019), (170, 1019), (210, 1018), (250, 1018), (290, 1018), (330, 1018), (370, 1018), (410, 1018), (450, 1018), (490, 1018), (530, 1017), (570, 1017), (610, 1016), (650, 1015), (690, 1015), (730, 1014)],
    [(50, 1070), (90, 1069), (130, 1068), (170, 1068), (210, 1068), (250, 1068), (290, 1068), (330, 1068), (370, 1068), (410, 1068), (450, 1068), (490, 1067), (530, 1067), (570, 1066), (610, 1065), (650, 1065), (690, 1063), (730, 1063)],
    [(50, 1119), (90, 1119), (130, 1118), (170, 1118), (210, 1118), (250, 1118), (290, 1118), (330, 1118), (370, 1118), (410, 1118), (450, 1118), (490, 1118), (530, 1116), (570, 1116), (610, 1114), (650, 1113), (690, 1112), (730, 1111)],
    [(50, 1168), (90, 1168), (130, 1168), (170, 1168), (210, 1168), (250, 1167), (290, 1167), (330, 1167), (370, 1167), (410, 1167), (450, 1167), (490, 1166), (530, 1165), (570, 1164), (610, 1163), (650, 1162), (690, 1162), (730, 1161)],
]

MAX_X_BOUNDARY = 730 
MAX_LINES_PER_PAGE = len(MASTER_LINE_COORDINATES)
IMAGE_CACHE = {}

def get_base_image(bg_image_path: str):
    if bg_image_path not in IMAGE_CACHE:
        if not os.path.exists(bg_image_path):
            raise FileNotFoundError(f"Could not find background file: {bg_image_path}")
        IMAGE_CACHE[bg_image_path] = Image.open(bg_image_path)
    return IMAGE_CACHE[bg_image_path].copy()

def get_interpolated_y(current_x: float, line_coordinates: list) -> float:
    if current_x <= line_coordinates[0][0]: return line_coordinates[0][1]
    if current_x >= line_coordinates[-1][0]: return line_coordinates[-1][1]
    for i in range(len(line_coordinates) - 1):
        pt1, pt2 = line_coordinates[i], line_coordinates[i+1]
        if pt1[0] <= current_x <= pt2[0]:
            return pt1[1] + ((current_x - pt1[0]) / (pt2[0] - pt1[0])) * (pt2[1] - pt1[1])
    return line_coordinates[0][1]

FONTS_CACHE = {}
def get_cached_fonts():
    """Loads and caches actual font objects paired with their custom configuration profiles."""
    global FONTS_CACHE
    if not FONTS_CACHE:
        for tool, cfg in TOOL_CONFIGS.items():
            FONTS_CACHE[tool] = []
            for var in cfg['variants']:
                try:
                    font_obj = ImageFont.truetype(var['path'], size=var['fontsize'])
                    FONTS_CACHE[tool].append((font_obj, var))
                except IOError:
                    FONTS_CACHE[tool].append((ImageFont.load_default(), var))
    return FONTS_CACHE

def render_chars_to_pages(bg_image_path: str, structured_chars: list, paper_type: str = "register") -> tuple:
    fonts = get_cached_fonts()
    pages = []
    page_offsets = [0]
    
    def create_new_page():
        img = get_base_image(bg_image_path)
        return img, ImageDraw.Draw(img)

    current_img, current_draw = create_new_page()
    line_idx = 0
    current_x = MASTER_LINE_COORDINATES[line_idx][0][0]

    idx = 0
    while idx < len(structured_chars):
        char, is_bold = structured_chars[idx]
        tool_type = 'marker' if is_bold else 'pen'
        cfg = TOOL_CONFIGS[tool_type]

        available_variants = fonts[tool_type]
        chosen_font_obj, chosen_font_rules = random.choice(available_variants)

        # Handle explicit line break layout commands
        if char == '\n':
            line_idx += 1
            if line_idx >= MAX_LINES_PER_PAGE:
                pages.append(current_img)
                page_offsets.append(idx + 1)
                current_img, current_draw = create_new_page()
                line_idx = 0
            current_x = MASTER_LINE_COORDINATES[line_idx][0][0]
            idx += 1
            return_triggered = True
            continue

        # Lookahead boundary calculation for upcoming structural words
        word_width = 0
        is_word_start = char not in [' ', '\t'] and (idx == 0 or structured_chars[idx-1][0] in [' ', '\n', '\t'])
        
        if is_word_start:
            lookahead_idx = idx
            while lookahead_idx < len(structured_chars):
                l_char, l_bold = structured_chars[lookahead_idx]
                if l_char in [' ', '\n', '\t']: break
                
                l_tool = 'marker' if l_bold else 'pen'
                proxy_font = fonts[l_tool][0][0] 
                bbox = current_draw.textbbox((0, 0), l_char, font=proxy_font)
                word_width += (bbox[2] - bbox[0])
                lookahead_idx += 1

        # Check single-character width bounding logic to measure ahead accurately
        char_bbox = current_draw.textbbox((0, 0), char, font=chosen_font_obj)
        char_w = (char_bbox[2] - char_bbox[0]) if (char_bbox[2] - char_bbox[0]) > 0 else 8

        # --- RE-ENGINEERED WRAPPING CRITERIA ---
        # Trigger line break if word exceeds line limit OR if a single character breaks margin bounds
        should_wrap = (is_word_start and (current_x + word_width > MAX_X_BOUNDARY) and (word_width <= (MAX_X_BOUNDARY - MASTER_LINE_COORDINATES[line_idx][0][0]))) or (current_x + char_w > MAX_X_BOUNDARY)

        if should_wrap:
            line_idx += 1
            if line_idx >= MAX_LINES_PER_PAGE:
                pages.append(current_img)
                page_offsets.append(idx)
                current_img, current_draw = create_new_page()
                line_idx = 0
            current_x = MASTER_LINE_COORDINATES[line_idx][0][0]

        # Calculate dynamic text placement base coordinates
        dynamic_y = get_interpolated_y(current_x, MASTER_LINE_COORDINATES[line_idx])
        
        current_draw.text(
            (current_x, dynamic_y - chosen_font_rules['ybias']), 
            char, 
            font=chosen_font_obj, 
            fill=cfg['color'],
            stroke_width=chosen_font_rules['stroke_width'], 
            stroke_fill=cfg['color']
        )
        
        # Increment cursor coordinate positions
        current_x += char_w
        idx += 1

    pages.append(current_img)
    return pages, page_offsets