import check50
import re
import os
from bs4 import BeautifulSoup


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _check_tag_closed(filename, tag):
    raw_html = _read(filename)
    clean_html = re.sub(r"<!--.*?-->", "", raw_html, flags=re.DOTALL)
    open_count = len(re.findall(rf"<{tag}\b", clean_html, re.IGNORECASE))
    close_count = len(re.findall(rf"</{tag}\s*>", clean_html, re.IGNORECASE))
    if open_count > close_count:
        raise check50.Failure(
            f"Unclosed <{tag}> tag in {filename}",
            help=f"Make sure you close every <{tag}> tag with a matching </{tag}> tag"
        )


def _html():
    html = _read("index.html")
    clean_html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    return clean_html


def _get_css():
    """Retrieve all CSS content from index.html style tags and style.css (if it exists)"""
    css_content = ""
    html = _html()
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
    for block in style_blocks:
        css_content += "\n" + block
    
    if os.path.exists("style.css"):
        # Verify that index.html contains a link tag to style.css
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("link", rel=lambda r: r and r.lower() == "stylesheet")
        has_correct_link = False
        for link in links:
            href = link.get("href", "").strip().lower()
            if href in ["style.css", "./style.css"]:
                has_correct_link = True
                break
        if not has_correct_link:
            raise check50.Failure(
                "style.css is not correctly linked in index.html",
                help="Make sure to include `<link rel=\"stylesheet\" href=\"style.css\">` inside the <head> of index.html"
            )
        css_content += "\n" + _read("style.css")
        
    return css_content


def _normalize_selector(sel):
    return re.sub(r'\s+', ' ', sel.strip().lower())


def _parse_css(css_text):
    """Parse CSS into a dict: {selector: {property: value}}"""
    # Strip comments first
    css_clean = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)
    
    rules = {}
    matches = re.findall(r'([^{]+)\{([^}]+)\}', css_clean)
    for selector, body in matches:
        selectors = [_normalize_selector(s) for s in selector.split(",")]
        props = {}
        for decl in body.split(";"):
            if ":" in decl:
                p, v = decl.split(":", 1)
                props[p.strip().lower()] = v.strip().lower()
        for sel in selectors:
            if sel in rules:
                rules[sel].update(props)
            else:
                rules[sel] = props
    return rules


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_navbar():
    """index.html has a <nav> element with class 'navbar'"""
    _check_tag_closed("index.html", "html")
    _check_tag_closed("index.html", "head")
    _check_tag_closed("index.html", "body")
    _check_tag_closed("index.html", "nav")
    html = _html()
    soup = BeautifulSoup(html, "html.parser")
    nav = soup.find("nav")
    if not nav:
        raise check50.Failure(
            "Missing <nav> element",
            help="Add a `<nav>` tag to wrap your navigation links"
        )
    # Support class checks case-insensitively or via split classes
    classes = nav.get("class", [])
    if "navbar" not in [c.lower() for c in classes]:
        raise check50.Failure(
            "The <nav> element must have class='navbar'",
            help="Update your nav tag to: <nav class=\"navbar\">"
        )


@check50.check(has_navbar)
def has_three_links():
    """the navigation bar has at least 3 anchor links (Home, About, Contact)"""
    _check_tag_closed("index.html", "a")
    html = _html()
    soup = BeautifulSoup(html, "html.parser")
    nav = soup.find("nav")
    if not nav:
        raise check50.Failure("Could not find <nav> element")
        
    a_tags = nav.find_all("a")
    if len(a_tags) < 3:
        raise check50.Failure(
            f"Found {len(a_tags)} link(s) inside <nav>, expected at least 3",
            help="Add at least 3 anchor links: Home, About, and Contact"
        )
        
    labels = [tag.get_text().strip().lower() for tag in a_tags]
    expected = ["home", "about", "contact"]
    for exp in expected:
        if not any(exp in lbl for lbl in labels):
            raise check50.Failure(
                f"Missing link for '{exp.capitalize()}'",
                help=f"Add an anchor link with text '{exp.capitalize()}' inside the navbar"
            )


# ─── CSS style checks ─────────────────────────────────────────────────────────

@check50.check(has_navbar)
def checks_navbar_css():
    """CSS sets dark background, white text links, no default underline, spacing, and hover underline"""
    css_text = _get_css()
    rules = _parse_css(css_text)
    
    # 1. Container selector (normally .navbar or nav.navbar or nav)
    container_sel = None
    for sel in [".navbar", "nav.navbar", "nav"]:
        if sel in rules:
            container_sel = sel
            break
            
    if not container_sel:
        raise check50.Failure(
            "Could not find CSS rules for class '.navbar' or tag 'nav'",
            help="Define styling for your navbar: .navbar { ... }"
        )
        
    container_props = rules[container_sel]
    # Check background or background-color
    bg_val = container_props.get("background-color", container_props.get("background", ""))
    if not bg_val:
        raise check50.Failure(
            "Navbar container (.navbar) is missing a background or background-color property",
            help="Add a dark background color, e.g., 'background-color: #222;' inside your .navbar rule"
        )
    # Check that background color is dark
    def parse_color_to_rgb(color_str):
        color_str = color_str.strip().lower()
        hex_match = re.match(r'^#([0-9a-f]{3}|[0-9a-f]{6})$', color_str)
        if hex_match:
            val = hex_match.group(1)
            if len(val) == 3:
                r = int(val[0] * 2, 16)
                g = int(val[1] * 2, 16)
                b = int(val[2] * 2, 16)
            else:
                r = int(val[0:2], 16)
                g = int(val[2:4], 16)
                b = int(val[4:6], 16)
            return r, g, b
            
        rgb_match = re.match(r'^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*[\d\.]+\s*)?\)$', color_str)
        if rgb_match:
            r, g, b = map(int, rgb_match.groups())
            return r, g, b
            
        light_names = {
            "white", "wheat", "lightgray", "lightgrey", "yellow", "lightyellow", "lemonchiffon", 
            "lightgoldenrodyellow", "papayawhip", "moccasin", "peachpuff", "lavender", "thistle", 
            "pink", "lightpink", "lightcyan", "powderblue", "lightblue", "skyblue", "paleturquoise", 
            "aquamarine", "lightgreen", "palegreen", "lime", "springgreen", "lawngreen", "chartreuse", 
            "yellowgreen", "beige", "bisque", "blanchedalmond", "cornsilk", "gold", "khaki", 
            "aliceblue", "azure", "floralwhite", "ghostwhite", "honeydew", "ivory", "lavenderblush", 
            "mintcream", "mistyrose", "oldlace", "seashell", "snow", "whitesmoke", "gainsboro", 
            "silver", "tan", "plum", "orchid", "violet", "fuchsia", "magenta", "salmon", 
            "lightsalmon", "tomato", "coral", "orange", "sand", "transparent"
        }
        if color_str in light_names:
            return 255, 255, 255
            
        hsl_match = re.match(r'^hsla?\(\s*\d+\s*,\s*([\d\.]+)%?\s*,\s*([\d\.]+)%?\s*(?:,\s*[\d\.]+\s*)?\)$', color_str)
        if hsl_match:
            s, l = map(float, hsl_match.groups())
            if l < 45:
                return 0, 0, 0
            else:
                return 255, 255, 255
                
        dark_names = {
            "black", "navy", "darkblue", "mediumblue", "blue", "darkgreen", "green", "teal", 
            "darkcyan", "maroon", "purple", "indigo", "darkmagenta", "darkviolet", "darkorange", 
            "saddlebrown", "dimgray", "dimgrey", "slategray", "slategrey", "darkslategray", 
            "darkslategrey", "brown", "olive", "grey", "gray"
        }
        if color_str in dark_names:
            return 0, 0, 0
            
        return 255, 255, 255

    def extract_color_from_bg(bg_value):
        bg_value = bg_value.strip().lower()
        func_match = re.search(r'(?:rgba?|hsla?)\([^\)]+\)', bg_value)
        if func_match:
            return func_match.group(0)
        hex_match = re.search(r'#[0-9a-f]{3,6}\b', bg_value)
        if hex_match:
            return hex_match.group(0)
        words = re.findall(r'\b[a-zA-Z]+\b', bg_value)
        non_color_words = {
            "url", "linear", "gradient", "repeat", "no", "scroll", "cover", "contain", "center", 
            "left", "right", "top", "bottom", "fixed", "local", "inherit", "initial", "revert", "unset"
        }
        colors = [w for w in words if w not in non_color_words]
        if colors:
            return colors[0]
        return ""

    color_token = extract_color_from_bg(bg_val)
    if not color_token:
        raise check50.Failure(
            "Could not parse background color from your .navbar styles",
            help="Specify a background color clearly, e.g. background-color: #222;"
        )
        
    r, g, b = parse_color_to_rgb(color_token)
    y = 0.299 * r + 0.587 * g + 0.114 * b
    if y >= 120:
        raise check50.Failure(
            f"Navbar background color '{color_token}' is not a dark color",
            help="Set the background-color of your .navbar to a dark color (e.g. #222 or black)"
        )
        
    # 2. navbar a styles
    link_sel = None
    for sel in [".navbar a", "nav.navbar a", "nav a", ".navbar > a"]:
        if sel in rules:
            link_sel = sel
            break
            
    if not link_sel:
        raise check50.Failure(
            "Missing CSS rules for links in the navbar (e.g. '.navbar a')",
            help="Define styling for links inside the navbar: .navbar a { ... }"
        )
        
    link_props = rules[link_sel]
    
    # 2a. Color: white/light
    color_val = link_props.get("color", "")
    if not color_val:
        raise check50.Failure(
            "Navbar links are missing a color property",
            help="Add 'color: white;' to your navbar links style"
        )
    if not any(x in color_val for x in ["white", "#fff", "#ffffff", "255,255,255", "yellow", "cyan", "lightblue"]):
        raise check50.Failure(
            "Navbar links color must be white (or a light color)",
            help="Set the text color of navbar links to white using `color: white;`"
        )
        
    # 2b. text-decoration: none
    if link_props.get("text-decoration") != "none":
        raise check50.Failure(
            "Navbar links must remove the default underline",
            help="Add 'text-decoration: none;' to your navbar links style"
        )
        
    # 2c. spacing (margin or padding)
    has_spacing = any(k in link_props for k in ["margin", "margin-right", "margin-left", "padding", "padding-right", "padding-left"])
    if not has_spacing:
        raise check50.Failure(
            "Navbar links should have spacing between them",
            help="Add spacing using 'margin-right: 20px;' or padding inside your links rule"
        )
        
    # 3. Hover state: underline
    hover_sel = None
    for sel in [".navbar a:hover", "nav.navbar a:hover", "nav a:hover", ".navbar > a:hover"]:
        if sel in rules:
            hover_sel = sel
            break
            
    if not hover_sel:
        raise check50.Failure(
            "Missing hover style for navbar links (e.g. '.navbar a:hover')",
            help="Define hover effects: .navbar a:hover { ... }"
        )
        
    hover_props = rules[hover_sel]
    if "underline" not in hover_props.get("text-decoration", ""):
        raise check50.Failure(
            "Hover state must underline the link",
            help="Add 'text-decoration: underline;' inside the :hover style rule"
        )
