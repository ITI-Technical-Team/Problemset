import check50
import re
import os


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _html():
    return _read("index.html").lower()


def _get_css():
    """Retrieve all CSS content from index.html style tags and style.css (if it exists)"""
    css_content = ""
    html = _read("index.html")
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
    for block in style_blocks:
        css_content += "\n" + block
    
    if os.path.exists("style.css"):
        css_content += "\n" + _read("style.css")
        
    return css_content.lower()


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_navbar():
    """index.html has a <nav> element with class 'navbar'"""
    html = _html()
    if "<nav" not in html:
        raise check50.Failure(
            "Missing <nav> element",
            help="Add a `<nav>` tag to wrap your navigation links"
        )
    if 'class="navbar"' not in html and "class='navbar'" not in html and 'class=navbar' not in html:
        raise check50.Failure(
            "The <nav> element must have class='navbar'",
            help="Update your nav tag to: <nav class=\"navbar\">"
        )


@check50.check(has_navbar)
def has_three_links():
    """the navigation bar has at least 3 anchor links (Home, About, Contact)"""
    html = _html()
    nav_block_match = re.search(r'<nav[^>]*>(.*?)</nav>', html, re.DOTALL)
    if not nav_block_match:
        raise check50.Failure("Could not parse the <nav> block")
        
    nav_content = nav_block_match.group(1)
    a_tags = re.findall(r'<a[^>]*>(.*?)</a>', nav_content, re.DOTALL)
    
    if len(a_tags) < 3:
        raise check50.Failure(
            f"Found {len(a_tags)} link(s) inside <nav>, expected at least 3",
            help="Add at least 3 anchor links: Home, About, and Contact"
        )
        
    # Check for labels (case-insensitive)
    labels = [tag.strip().lower() for tag in a_tags]
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
    css = _get_css()
    
    # 1. Dark Background on navbar
    # Find background-color inside .navbar rule
    navbar_match = re.search(r'\.navbar\s*\{([^}]+)\}', css, re.DOTALL)
    if not navbar_match:
        raise check50.Failure("Could not find CSS rules for class '.navbar'")
    navbar_rules = navbar_match.group(1)
    if "background" not in navbar_rules:
        raise check50.Failure(
            "class '.navbar' is missing a background or background-color property",
            help="Add a dark background color: 'background-color: #222;'"
        )
    # Check if they used #222, #333, #000, black, rgb, etc.
    # We will pass any background-color configuration
    
    # 2. navbar a styles
    link_match = re.search(r'\.navbar\s+a\s*\{([^}]+)\}', css, re.DOTALL)
    if not link_match:
        # Fallback to general nav a
        link_match = re.search(r'nav\s+a\s*\{([^}]+)\}', css, re.DOTALL)
        
    if not link_match:
        raise check50.Failure(
            "Missing CSS rules for links in the navbar (e.g. '.navbar a')",
            help="Define styling for links inside the navbar: .navbar a { ... }"
        )
        
    link_rules = link_match.group(1)
    
    # 2a. Color: white
    if "color" not in link_rules:
        raise check50.Failure(
            "Navbar links are missing a color property",
            help="Add 'color: white;' to your navbar links style"
        )
        
    # 2b. text-decoration: none
    if "text-decoration" not in link_rules or "none" not in link_rules:
        raise check50.Failure(
            "Navbar links must remove the default underline",
            help="Add 'text-decoration: none;' to your navbar links style"
        )
        
    # 2c. spacing (margin-right or padding)
    if "margin-right" not in link_rules and "margin" not in link_rules and "padding" not in link_rules:
        raise check50.Failure(
            "Navbar links should have spacing between them",
            help="Add spacing using 'margin-right: 20px;' to separate the links"
        )
        
    # 3. Hover state: underline
    hover_match = re.search(r'\.navbar\s+a\s*:\s*hover\s*\{([^}]+)\}', css, re.DOTALL)
    if not hover_match:
        hover_match = re.search(r'nav\s+a\s*:\s*hover\s*\{([^}]+)\}', css, re.DOTALL)
        
    if not hover_match:
        raise check50.Failure(
            "Missing hover style for navbar links (e.g. '.navbar a:hover')",
            help="Define hover effects: .navbar a:hover { ... }"
        )
        
    hover_rules = hover_match.group(1)
    if "text-decoration" not in hover_rules or "underline" not in hover_rules:
        raise check50.Failure(
            "Hover state must underline the link",
            help="Add 'text-decoration: underline;' inside the :hover style rule"
        )
