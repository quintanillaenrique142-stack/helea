#!/usr/bin/env python3
"""Builds the HELÉA catalog site from catalog.json into ../docs.

Usage:
  python3 src/build.py            # public build
  python3 src/build.py --draft    # shows yellow notes where product info is still missing
  python3 src/build.py --artifact # preview build (index.html without <html>/<head> wrapper)

To add or change a piece: edit src/catalog.json, put its photo in docs/assets/img/<slug>.jpg, run the build.
Optional product fields: "description", "material", "size", "care", "variants", "sold_out": true.
"""
import html
import json
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "docs"
DRAFT = "--draft" in sys.argv or "--artifact" in sys.argv
ARTIFACT = "--artifact" in sys.argv

data = json.loads((SRC / "catalog.json").read_text())
BRAND = data["brand"]
COLLS = {c["slug"]: c for c in data["collections"]}
PRODUCTS = data["products"]
BASE_URL = BRAND.get("base_url", "").rstrip("/")
CSS = (SRC / "styles.css").read_text()

COVERS = {slug: c["cover"] for slug, c in COLLS.items()}
LIVE = [c for c in COLLS.values() if not c.get("archived")]
SHOW_PAST = bool(BRAND.get("show_past", False))  # set "show_past": true in catalog.json to publish the past collection again
if not SHOW_PAST:
    COLLS = {k: v for k, v in COLLS.items() if not v.get("archived")}
    PRODUCTS = [p for p in PRODUCTS if p["collection"] in COLLS]
PAST = [c for c in COLLS.values() if c.get("archived")]
LIVE_PRODUCTS = [p for p in PRODUCTS if not COLLS[p["collection"]].get("archived")]
FIRST = LIVE[0]["slug"] + ".html"
PAST_NAME = "Summer Collection"


def archived(p):
    return bool(COLLS[p["collection"]].get("archived"))

E = html.escape

WA_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.3 2.2 2.2 0 0 0 .2-1.3c-.1-.1-.3-.2-.5-.3z"/></svg>'
IG_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>'


def price(p):
    return f"CA${p['price']}"


def wa_link(text):
    number = "".join(ch for ch in BRAND.get("whatsapp", "") if ch.isdigit())
    return f"https://wa.me/{number}?text={quote(text)}"


def ig_link():
    return f"https://ig.me/m/{BRAND['instagram']}"


def page_url(name):
    return f"{BASE_URL}/{name}" if BASE_URL else name


def header(active):
    links = [("shop.html", "Shop"), (FIRST, "Collections"), ("our-story.html", "Our Story"), ("how-to-order.html", "How to Order")]
    nav = "".join(
        f'<a href="{h}"{" aria-current=\"page\"" if active == h else ""}>{t}</a>' for h, t in links
    )
    banner = '<div class="draft-banner">Preview: yellow notes mark details still to come from Helena. They do not appear on the public site.</div>' if DRAFT else ""
    return f"""{banner}<header class="site-header"><div class="wrap">
<a class="logo caps" href="index.html" aria-label="HELÉA home">HELÉA</a>
<nav class="nav" aria-label="Main">{nav}</nav>
</div></header>"""


PAST_LINK_TMPL = '<li><a href="summer-collection.html">Past: {name}</a></li>'


def footer():
    PAST_LINK = PAST_LINK_TMPL.format(name=PAST_NAME) if SHOW_PAST else ""
    colls = "".join(f'<li><a href="{c["slug"]}.html">{E(c["name"])}</a></li>' for c in LIVE)
    return f"""<footer class="site-footer"><div class="wrap">
<div style="display:flex;flex-direction:column;gap:12px">
<a class="logo caps" href="index.html">HELÉA</a>
<p>{E(BRAND['tagline'])}.<br>Everyday jewelry inspired by the Pacific and the wild landscapes of British Columbia.</p>
</div>
<div><p class="eyebrow" style="color:inherit;opacity:.7;margin-bottom:10px">Collections</p><ul>{colls}<li><a href="shop.html">Shop all</a></li>{PAST_LINK}</ul></div>
<div><p class="eyebrow" style="color:inherit;opacity:.7;margin-bottom:10px">HELÉA</p><ul>
<li><a href="our-story.html">Our story</a></li>
<li><a href="how-to-order.html">How to order</a></li>
<li><a href="https://www.instagram.com/{BRAND['instagram']}/" target="_blank" rel="noopener">Instagram</a></li>
<li><a href="mailto:{BRAND['email']}">{BRAND['email']}</a></li>
</ul></div>
<p class="footer-base">© 2026 HELÉA · {E(BRAND['location'])}</p>
</div></footer>"""


def doc(filename, title, description, body, active="", extra_head="", body_class="", og_image="assets/img/hero.jpg"):
    fonts = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&family=Raleway:wght@300;400;500&display=swap">'
    full_title = f"{title} | HELÉA" if title != "HELÉA" else "HELÉA | The light you carry everywhere"
    canonical = f'<link rel="canonical" href="{page_url(filename)}">' if BASE_URL else ""
    head = f"""<title>{E(full_title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{E(description)}">
<meta property="og:title" content="{E(full_title)}">
<meta property="og:description" content="{E(description)}">
<meta property="og:image" content="{page_url(og_image)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#8a9a7b">
{canonical}
{fonts}
<style>{CSS}</style>
{extra_head}"""
    content = f'{header(active)}<main>{body}</main>{footer()}'
    if ARTIFACT and filename == "index.html":
        return f"{head}\n<div class=\"{body_class}\">{content}</div>\n"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head}
</head>
<body class="{body_class}">
{content}
</body>
</html>
"""


def card(p):
    variant = f" · {E(p['variants'])}" if p.get("variants") else ""
    return f"""<a class="card" href="{p['slug']}.html">
<div class="card-img"><img src="assets/img/{p['slug']}.jpg" alt="{E(p['name'])}" loading="lazy" width="560" height="560"></div>
<span class="card-name">{E(p['name'])}</span>
<span class="card-meta"><span>{E(COLLS[p['collection']]['name'])}{variant}</span><span>{"No longer available" if archived(p) else price(p)}</span></span>
</a>"""


def write(name, text):
    (OUT / name).write_text(text)


# ---------- Home ----------
def build_home():
    tiles = "".join(
        f"""<a class="tile" href="{c['slug']}.html">
<div class="tile-img"><img src="assets/img/{COVERS[c['slug']]}.jpg" alt="{E(c['name'])} collection" loading="lazy"></div>
<h3 class="caps">{E(c['name'])}</h3><p>{E(c['story'].split('.')[0])}.</p></a>"""
        for c in LIVE
    )
    featured = ["turquoise-aura-necklace", "pearl-sparkle-earrings", "gold-whale-tail-necklace", "silver-gold-whale-ring",
                "gold-emerald-squares", "orange-crystal-flower", "rainbow-necklace", "multiflower-hoops"]
    grid = "".join(card(next(p for p in PRODUCTS if p["slug"] == s)) for s in featured)
    body = f"""
<section class="hero"><div class="hero-grid">
<div class="hero-copy">
<p class="eyebrow">Vancouver, British Columbia</p>
<h1>The light you carry everywhere</h1>
<hr class="rule">
<p>Everyday jewelry inspired by the shimmer of the Pacific and the warmth breaking through the Vancouver clouds. Made for those who find beauty in the wild.</p>
<div class="hero-actions"><a class="btn btn-cream" href="shop.html">Shop the collections</a><a class="btn btn-line" href="how-to-order.html">How to order</a></div>
</div>
<div class="hero-img"><img src="assets/img/hero.jpg" alt="Two women wearing HELÉA jewelry on a Vancouver beach at sunset" fetchpriority="high"></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head center"><p class="eyebrow">Fall 2026</p><h2>The Collections</h2><p>Four collections inspired by the places we love in British Columbia.</p></div>
<div class="tiles">{tiles}</div>
</div></section>

<section class="section" style="padding-top:0"><div class="wrap">
<div class="section-head"><p class="eyebrow">Pieces to start with</p><h2>From every collection</h2></div>
<div class="grid">{grid}</div>
<p style="margin-top:32px"><a class="btn btn-ghost" style="width:auto" href="shop.html">See all {len(LIVE_PRODUCTS)} pieces</a></p>
</div></section>

<section class="section band"><div class="wrap">
<div class="section-head center"><p class="eyebrow">Built to endure</p><h2>Made for the life we lead here</h2></div>
<div class="pillars">
<div class="pillar"><svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M4 17c4-6 8-6 12 0s8 6 12 0"/></svg><h3>Waterproof</h3><p>Materials engineered to resist the elements and maintain their brilliance.</p></div>
<div class="pillar"><svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M16 4c6 5 6 19 0 24-6-5-6-19 0-24z"/><path d="M16 6v20"/></svg><h3>Outdoor Life</h3><p>Exactly the type of life we lead in Vancouver: active, wet, and stylish.</p></div>
<div class="pillar"><svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.3"><circle cx="16" cy="16" r="10"/></svg><h3>Everyday</h3><p>Designed for fashion lovers who embrace the outdoor spirit.</p></div>
</div>
</div></section>

<section class="section"><div class="wrap split">
<div class="split-img"><img src="assets/img/story.jpg" alt="HELÉA hoops and beaded ring worn at the beach" loading="lazy"></div>
<div class="split-copy">
<p class="eyebrow">The meaning</p>
<h2>Derived from the Greek word for “light”</h2>
<p>Heléa represents a glow that never flickers, no matter the wind or the rain. It was born from a deep love for nature and the wild landscapes of British Columbia, and built on the belief that beauty should never be fragile.</p>
<p><a class="btn btn-ghost" style="width:auto" href="our-story.html">Read our story</a></p>
</div>
</div></section>

<section class="section" style="padding-top:0"><div class="wrap">
<div class="section-head"><p class="eyebrow">How to order</p><h2>Ordering is a conversation</h2></div>
{steps_html()}
</div></section>
"""
    write("index.html", doc("index.html", "HELÉA",
        "HELÉA is everyday jewelry from Vancouver, BC. Explore the Fall 2026 collections and order directly on WhatsApp.",
        body, extra_head=org_schema()))


def steps_html():
    return """<ol class="steps">
<li><h3>Choose your piece</h3><p>Browse the collections and open any piece to see it up close.</p></li>
<li><h3>Tap “Order on WhatsApp”</h3><p>A message with the piece and price is ready to send. You can also write to us on Instagram.</p></li>
<li><h3>We confirm with you</h3><p>We reply personally to confirm availability, payment and how you'll receive it.</p></li>
</ol>"""


def org_schema():
    d = {"@context": "https://schema.org", "@type": "Organization", "name": "HELÉA", "email": BRAND["email"],
         "sameAs": [f"https://www.instagram.com/{BRAND['instagram']}/"], "slogan": BRAND["tagline"]}
    if BASE_URL:
        d["url"] = BASE_URL
    return f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False)}</script>'


# ---------- Shop & collections ----------
def build_shop():
    filters = '<a href="shop.html" aria-current="true">All</a>' + "".join(f'<a href="{c["slug"]}.html">{E(c["name"])}</a>' for c in LIVE)
    blocks = ""
    for c in LIVE:
        items = [p for p in PRODUCTS if p["collection"] == c["slug"]]
        blocks += f"""<div class="coll-block" id="{c['slug']}"><div class="section-head"><p class="eyebrow">{len(items)} pieces</p><h2>{E(c['name'])}</h2><p>{E(c['story'])}</p></div>
<div class="grid">{''.join(card(p) for p in items)}</div></div>"""
    if SHOW_PAST:
        blocks += f'<p style="margin-top:56px"><a class="btn btn-ghost" style="width:auto" href="summer-collection.html">See our past {PAST_NAME}</a></p>'
    body = f"""<section class="intro"><div class="wrap"><p class="eyebrow">The Collections · Fall 2026</p><h1>Shop all pieces</h1><p>Prices in Canadian dollars. Every piece is ordered directly with us on WhatsApp or Instagram.</p></div></section>
<section class="section"><div class="wrap"><nav class="filters" aria-label="Collections">{filters}</nav>{blocks}</div></section>"""
    write("shop.html", doc("shop.html", "Shop all", "All HELÉA pieces from the Fall 2026 collections: necklaces, earrings and rings from CA$25.", body, active="shop.html"))

    for c in COLLS.values():
        items = [p for p in PRODUCTS if p["collection"] == c["slug"]]
        old = c.get("archived")
        group = PAST if old else LIVE
        first = '<a href="summer-collection.html">All past pieces</a>' if old else '<a href="shop.html">All</a>'
        filters = first + "".join(
            f'<a href="{o["slug"]}.html"{" aria-current=\"true\"" if o["slug"] == c["slug"] else ""}>{E(o["name"])}</a>' for o in group)
        eyebrow = f"Past collection · {E(c['season'])} · No longer available" if old else f"{E(c['season'])} collection · {len(items)} pieces"
        extra = f"<p>{E(c['story2'])}</p>" if c.get("story2") else ""
        back = f'<p style="margin-top:48px"><a class="btn btn-ghost" style="width:auto" href="shop.html">Shop the Fall 2026 collections</a></p>' if old else ""
        body = f"""<section class="intro"><div class="wrap"><p class="eyebrow">{eyebrow}</p><h1 class="caps" style="letter-spacing:.18em">{E(c['name'])}</h1><hr class="rule"><p>{E(c['story'])}</p>{extra}</div></section>
<section class="section"><div class="wrap"><nav class="filters" aria-label="Collections">{filters}</nav><div class="grid">{''.join(card(p) for p in items)}</div>{back}</div></section>"""
        write(f"{c['slug']}.html", doc(f"{c['slug']}.html", f"{c['name']} Collection", c["story"], body, active="" if old else FIRST, og_image=f"assets/img/{COVERS[c['slug']]}.jpg"))

    if not SHOW_PAST:
        return
    blocks = ""
    for c in PAST:
        items = [p for p in PRODUCTS if p["collection"] == c["slug"]]
        blocks += f"""<div class="coll-block"><div class="section-head"><h2>{E(c['name'])}</h2><p>{E(c['story'])}</p></div>
<div class="grid">{''.join(card(p) for p in items)}</div></div>"""
    body = f"""<section class="intro"><div class="wrap"><p class="eyebrow">Past collection · No longer available</p><h1>{PAST_NAME}</h1><hr class="rule"><p>The pieces that started HELÉA. These are no longer available, but you can find our current pieces in the Fall 2026 collections.</p><p><a class="btn btn-cream" href="shop.html">Shop Fall 2026</a></p></div></section>
<section class="section"><div class="wrap">{blocks}</div></section>"""
    write("summer-collection.html", doc("summer-collection.html", PAST_NAME, "HELÉA's past Summer Collection: Lynn Mist, Cypress and Burrard. These pieces are no longer available.", body))


# ---------- Product pages ----------
def build_products():
    for p in PRODUCTS:
        c = COLLS[p["collection"]]
        msg = f"Hi HELÉA! I'd like to order the {p['name']}" + (f" ({p['variants']})" if p.get("variants") else "") + f", {price(p)}."
        if BASE_URL:
            msg += f" {page_url(p['slug'] + '.html')}"
        wa = wa_link(msg)
        variant = f'<p class="variant">Available in {E(p["variants"])}. Tell us which one you prefer in your message.</p>' if p.get("variants") else ""
        sold = p.get("sold_out")

        def field(key, label):
            if p.get(key):
                return f"<p><strong>{label}:</strong> {E(p[key])}</p>"
            return f'<p class="pending">Pending from Helena: {label.lower()}</p>' if DRAFT else ""

        desc = f"<p>{E(p['description'])}</p>" if p.get("description") else (
            '<p class="pending">Pending from Helena: a short description of this piece</p>' if DRAFT else "")
        details_body = desc + field("material", "Material") + field("size", "Size")
        if not details_body.strip():
            details_body = "<p>Ask us on WhatsApp for size and material details.</p>"
        care = f"<p>{E(p['care'])}</p>" if p.get("care") else (
            '<p class="pending">Pending from Helena: care instructions</p>' if DRAFT else "<p>Ask us how to care for this piece.</p>")
        related = [o for o in PRODUCTS if o["collection"] == p["collection"] and o["slug"] != p["slug"]][:4]
        order_btn = (f'<a class="btn btn-wa" href="{wa}" target="_blank" rel="noopener">{WA_ICON}Order on WhatsApp</a>' if not sold
                     else '<span class="btn btn-ghost" aria-disabled="true">Sold out</span>')
        old = archived(p)
        if old:
            actions = f"""<p class="variant">This piece is from our past {PAST_NAME} and is no longer available.</p>
<div class="actions"><a class="btn btn-ghost" href="shop.html">Shop the Fall 2026 collections</a></div>"""
            price_html = ""
            bar = ""
            crumb_root = f'<a href="summer-collection.html">{PAST_NAME}</a>'
        else:
            actions = f"""<div class="actions">
{order_btn}
<a class="btn btn-ghost" href="{ig_link()}" target="_blank" rel="noopener">{IG_ICON}Message us on Instagram</a>
</div>
<p class="note">Your message opens with this piece and its price already written. We'll reply to confirm availability, payment and delivery.</p>"""
            price_html = f'<p class="price">{price(p)}<small>CAD</small></p>'
            bar = f"""<div class="order-bar"><div class="ob-name"><strong>{E(p['name'])}</strong>{price(p)}</div>{order_btn.replace('btn btn-wa', 'btn btn-wa ob-btn')}</div>"""
            crumb_root = '<a href="shop.html">Shop</a>'
        body = f"""<div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb">{crumb_root}<span>/</span><a href="{c['slug']}.html">{E(c['name'])}</a><span>/</span><span>{E(p['name'])}</span></nav>
<article class="product">
<div class="product-img"><img src="assets/img/{p['slug']}.jpg" alt="{E(p['name'])}" width="560" height="560" fetchpriority="high"></div>
<div class="product-info">
<p class="eyebrow">{E(c['name'])} Collection · {E(p['type'])}</p>
<h1>{E(p['name'])}</h1>
{price_html}
{variant}
{actions}
<div class="details">
<details open><summary>Details</summary><div class="body">{details_body}</div></details>
<details><summary>About {E(c['name'])}</summary><div class="body"><p>{E(c['story'])}</p></div></details>
<details><summary>Care</summary><div class="body">{care}</div></details>
</div>
</div>
</article>
</div>
<section class="section" style="padding-top:0"><div class="wrap">
<div class="section-head"><p class="eyebrow">More from</p><h2>{E(c['name'])}</h2></div>
<div class="grid">{''.join(card(o) for o in related)}</div>
</div></section>
{bar}"""
        schema = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "brand": {"@type": "Brand", "name": "HELÉA"},
                  "image": page_url(f"assets/img/{p['slug']}.jpg"), "category": p["type"],
                  "offers": {"@type": "Offer", "price": str(p["price"]), "priceCurrency": BRAND["currency"],
                             "availability": "https://schema.org/Discontinued" if old else "https://schema.org/InStock"}}
        if p.get("description"):
            schema["description"] = p["description"]
        write(f"{p['slug']}.html", doc(f"{p['slug']}.html", p["name"],
            (f"{p['name']} from the HELÉA {c['name']} collection ({PAST_NAME}). No longer available." if old else f"{p['name']} from the HELÉA {c['name']} collection, {price(p)}. Order directly on WhatsApp."),
            body, extra_head=f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>',
            body_class="" if old else "has-order-bar", og_image=f"assets/img/{p['slug']}.jpg"))


# ---------- Story & order ----------
def build_story():
    body = """<section class="intro"><div class="wrap"><p class="eyebrow">Our story</p><h1>Welcome to Heléa</h1><hr class="rule"><p>The light you carry everywhere.</p></div></section>
<section class="section"><div class="wrap split">
<div class="split-img"><img src="assets/img/lifestyle-1.jpg" alt="Profile wearing HELÉA earrings and necklace in the sun" loading="lazy"></div>
<div class="split-copy prose">
<p class="eyebrow">The meaning</p>
<h2>A glow that never flickers</h2>
<p>Derived from the Greek word for “light,” Heléa represents a glow that never flickers, no matter the wind or the rain. It is the shimmer of the Pacific and the warmth breaking through the Vancouver clouds.</p>
<p>Our pieces are designed for those who find beauty in the wild: jewelry that balances high-end fashion with high-performance durability.</p>
</div></div></section>
<section class="section band"><div class="wrap" style="display:flex;flex-direction:column;align-items:center;gap:18px;text-align:center">
<p class="eyebrow">Born from nature</p>
<p class="quote" style="color:inherit">Beauty should never be fragile.</p>
<p style="opacity:.9">Heléa was born from a deep love for nature and the wild landscapes of British Columbia. Created for those who call the outdoors their home.</p>
</div></section>
<section class="section"><div class="wrap split">
<div class="split-copy prose">
<p class="eyebrow">Everyday wear</p>
<h2>From a morning hike in Lynn Canyon to a candlelit dinner downtown</h2>
<p>Every collection is named after a place we love in British Columbia: the forests of the West Coast, the Pacific, the Golden Ears mountains and the first light on Cypress.</p>
<p><a class="btn btn-ghost" style="width:auto" href="shop.html">Explore the collections</a></p>
</div>
<div class="split-img"><img src="assets/img/lifestyle-water.jpg" alt="Hands wearing HELÉA rings at the water's edge" loading="lazy"></div>
</div></section>"""
    write("our-story.html", doc("our-story.html", "Our Story",
        "Heléa comes from the Greek word for light. Jewelry from Vancouver, BC, inspired by the Pacific and built on the belief that beauty should never be fragile.",
        body, active="our-story.html", og_image="assets/img/lifestyle-1.jpg"))


def build_order():
    number = BRAND.get("whatsapp") or ""
    wa_display = E(number) if number else ('<span class="pending">Helena\'s WhatsApp number goes here</span>' if DRAFT else "WhatsApp")
    pending_ship = '<p class="pending">Pending: delivery areas, shipping costs to Canada and Mexico, and accepted payment methods</p>' if DRAFT else ""
    body = f"""<section class="intro"><div class="wrap"><p class="eyebrow">How to order</p><h1>Ordering is a conversation</h1><hr class="rule"><p>We're a small Vancouver brand, so every order is handled personally.</p></div></section>
<section class="section"><div class="wrap">{steps_html()}</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
<div class="section-head"><p class="eyebrow">Contact</p><h2>Write to us</h2></div>
<div class="contact-grid">
<div class="contact-card"><p class="eyebrow">WhatsApp</p><p class="val">{wa_display}</p><p><a class="btn btn-wa" style="width:auto" href="{wa_link("Hi HELÉA! I have a question about your jewelry.")}" target="_blank" rel="noopener">{WA_ICON}Open WhatsApp</a></p></div>
<div class="contact-card"><p class="eyebrow">Instagram</p><p class="val">@{BRAND['instagram']}</p><p><a class="btn btn-ghost" style="width:auto" href="{ig_link()}" target="_blank" rel="noopener">{IG_ICON}Send a DM</a></p></div>
<div class="contact-card"><p class="eyebrow">Email</p><p class="val">{BRAND['email']}</p><p class="note">We usually reply within a day.</p></div>
</div>
<div style="margin-top:40px;display:flex;flex-direction:column;gap:12px">{pending_ship}</div>
</div></section>"""
    write("how-to-order.html", doc("how-to-order.html", "How to Order",
        "Order HELÉA jewelry directly on WhatsApp or Instagram. We confirm availability, payment and delivery personally.", body, active="how-to-order.html"))


def build_meta():
    pages = ["index.html", "shop.html", "our-story.html", "how-to-order.html"] + (["summer-collection.html"] if SHOW_PAST else []) + [f"{c}.html" for c in COLLS] + [f"{p['slug']}.html" for p in PRODUCTS]
    if BASE_URL:
        urls = "".join(f"<url><loc>{page_url(p)}</loc></url>" for p in pages)
        write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
        write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
    else:
        write("robots.txt", "User-agent: *\nAllow: /\n")
    (OUT / ".nojekyll").write_text("")
    return pages


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for f in OUT.glob("*.html"):
        f.unlink()
    if SHOW_PAST:  # past-collection photos live in src/archive-img while hidden
        import shutil
        for f in (SRC / "archive-img").glob("*.jpg"):
            shutil.copy(f, OUT / "assets" / "img" / f.name)
    build_home(); build_shop(); build_products(); build_story(); build_order()
    pages = build_meta()
    print(f"Built {len(pages)} pages into {OUT} (draft={DRAFT}, artifact={ARTIFACT})")
