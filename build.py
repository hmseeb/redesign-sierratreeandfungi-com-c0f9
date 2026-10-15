#!/usr/bin/env python3
"""Static site generator for the Sierra Tree & Fungi redesign.

Reads the scraped page content (kept outside the published site, in
.git/gsb-source-pages/) and renders it into the new design: one directory with
an index.html per source path, plus the hand-built home page.

Run:  python3 build.py
"""

import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, ".git", "gsb-source-pages")

PHONE_DISPLAY = "(530) 391-6100"
PHONE_TEL = "tel:+15303916100"
PHONE_SMS = "sms:+15303916100"
EMAIL = "Christopher@SierraTreeandFungi.com"
FORM_ACTION = "https://vision.leadrai.com/api/forms/246b1deb67270022258874839c48348b"
BRAND = "Sierra Tree &amp; Fungi"

# --------------------------------------------------------------------------
# pages that exist in this site
# --------------------------------------------------------------------------
# source file -> (path, nav label)
PAGES = [
    ("01.md", "/services", "All Services"),
    ("02.md", "/consulting-arborist-services", "Consulting Arborist Services"),
    ("03.md", "/arborist-reports", "Arborist Reports"),
    ("04.md", "/ceqa-arborist-reports-sacramento", "CEQA Arborist Reports"),
    ("05.md", "/tree-inventory", "Tree Inventory and Survey"),
    ("06.md", "/oak-resource-management-plan-el-dorado-county", "Oak Technical Report"),
    ("07.md", "/oak-tree-removal-permit-el-dorado-county", "Oak Tree Removal Permit"),
    ("08.md", "/protected-trees-in-california", "Protected Trees in California"),
    ("09.md", "/tree-risk-assessment", "Tree Risk Assessment"),
    ("10.md", "/tree-health-assessment", "Tree Health Assessment"),
    ("11.md", "/how-to-tell-if-a-tree-is-dead-or-dying", "Dead or Dying Tree"),
    ("12.md", "/tree-fungus-treatment", "Treating Fungi on Trees"),
    ("13.md", "/fungal-pathology-reports", "Fungal Pathology Reports"),
    ("14.md", "/armillaria-root-rot", "Armillaria Root Rot"),
    ("15.md", "/oak-disease-sacramento", "Oak Disease, Sacramento Area"),
    ("16.md", "/oak-galls", "Oak Galls and Gall Wasps"),
    ("17.md", "/mediterranean-oak-borer", "Mediterranean Oak Borer"),
    ("18.md", "/mistletoe-in-trees", "Mistletoe in Trees"),
    ("19.md", "/redwood-tree-care", "Redwood Tree Care"),
    ("20.md", "/tree-bark-and-sap-symptoms", "Bark and Sap Symptoms"),
    ("21.md", "/plant-health-care", "Plant Health Care"),
    ("22.md", "/root-collar-excavation", "Root Collar Excavation"),
    ("23.md", "/defensible-space-el-dorado-county", "Wildfire Defensible Space"),
    ("24.md", "/tree-roots-damaging-foundation", "Tree Roots and Property Damage"),
    ("25.md", "/new-homeowner-tree-assessment", "New Homeowner Tree Assessment"),
]

EXISTING = {p for _, p, _ in PAGES}
EXISTING.add("/")

# internal paths that have no page here but have a sensible destination
ALIAS = {
    "/consultation": "#consult",
    "/contact": "#consult",
    "/about": "/#about",
    "/credentials": "/#about",
    "/service-areas": "/#areas",
    "/el-dorado-county": "/#areas",
    "/sacramento-county": "/#areas",
    "/placer-county": "/#areas",
    "/amador-county": "/#areas",
}

# images copied into this repo from the original site
IMAGE_MAP = [
    ("Sugar", ("/images/source/06-image.webp", 1200, 1600)),
    ("BCMA", ("/images/source/16-image.webp", 257, 450)),
    ("Laetiporus", ("/images/source/28-image.webp", 1080, 1440)),
]

HERO_IMG = "/images/source/06-image.webp"
HERO_SRCSET = ("/images/source/02-image.webp 750w, "
               "/images/source/04-image.webp 1080w, "
               "/images/source/06-image.webp 1200w")
BADGE_IMG = "/images/source/16-image.webp"
FUNGI_IMG = "/images/source/28-image.webp"

NAV_GROUPS = [
    ("Consulting &amp; assessments", [
        ("/consulting-arborist-services", "Consulting Arborist Services"),
        ("/new-homeowner-tree-assessment", "New Homeowner Tree Assessment"),
        ("/tree-risk-assessment", "Tree Risk Assessment"),
        ("/tree-health-assessment", "Tree Health Assessment"),
        ("/how-to-tell-if-a-tree-is-dead-or-dying", "Dead or Dying Tree"),
        ("/tree-inventory", "Tree Inventory and Survey"),
    ]),
    ("Reports &amp; permitting", [
        ("/arborist-reports", "Arborist Reports"),
        ("/ceqa-arborist-reports-sacramento", "CEQA Arborist Reports"),
        ("/oak-resource-management-plan-el-dorado-county", "Oak Technical Report"),
        ("/oak-tree-removal-permit-el-dorado-county", "Oak Tree Removal Permit"),
        ("/protected-trees-in-california", "Protected Trees in California"),
    ]),
    ("Diagnosis &amp; tree health", [
        ("/fungal-pathology-reports", "Fungal Pathology Reports"),
        ("/tree-fungus-treatment", "Treating Fungi on Trees"),
        ("/armillaria-root-rot", "Armillaria Root Rot"),
        ("/oak-disease-sacramento", "Oak Disease, Sacramento Area"),
        ("/mediterranean-oak-borer", "Mediterranean Oak Borer"),
        ("/oak-galls", "Oak Galls and Gall Wasps"),
        ("/mistletoe-in-trees", "Mistletoe in Trees"),
    ]),
    ("Care, property &amp; wildfire", [
        ("/plant-health-care", "Plant Health Care"),
        ("/root-collar-excavation", "Root Collar Excavation"),
        ("/tree-bark-and-sap-symptoms", "Bark and Sap Symptoms"),
        ("/redwood-tree-care", "Redwood Tree Care"),
        ("/tree-roots-damaging-foundation", "Tree Roots and Property Damage"),
        ("/defensible-space-el-dorado-county", "Wildfire Defensible Space"),
    ]),
]

SERVICE_OPTIONS = [
    "Arborist report",
    "Tree risk assessment",
    "Tree health assessment",
    "Oak Technical Report (El Dorado County)",
    "Oak tree removal permit support",
    "CEQA report or development project",
    "Fungal pathology or lab diagnostics",
    "Plant health care",
    "Root collar excavation",
    "Tree inventory or survey",
    "Wildfire defensible space",
    "New homeowner tree assessment",
    "Expert witness or dispute",
    "Not sure yet, I have a question",
]

ICONS = {
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/></svg>',
    "sms": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9.6 9.6 0 0 1-2.8-.4L3 21l1.6-4.2A8.2 8.2 0 0 1 3.6 11 8.4 8.4 0 0 1 12 3h.5a8.4 8.4 0 0 1 8 8.5Z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/><path d="m3 7 9 6 9-6"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
    "form": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15.5 3.5h-7A2.5 2.5 0 0 0 6 6v12a2.5 2.5 0 0 0 2.5 2.5h7A2.5 2.5 0 0 0 18 18V6a2.5 2.5 0 0 0-2.5-2.5Z"/><path d="M9 8h6M9 12h6M9 16h3"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9.2"/><path d="m8 12.4 2.8 2.8L16.4 9.6"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "caret": '<svg class="caret" viewBox="0 0 12 8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m1 1.6 5 5 5-5"/></svg>',
    "logo": '<svg viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="14" fill="#0f2e22"/><path d="M32 9 44 27H20L32 9Z" fill="#3f8c63"/><path d="M32 19 47 40H17L32 19Z" fill="#2d6a4b"/><path d="M29.5 38h5v13h-5z" fill="#8a6a3c"/><path d="M22 48c0-4.4 4-8 9-8s9 3.6 9 8H22Z" fill="#c9811f"/><rect x="29" y="47" width="6" height="8" rx="2.5" fill="#efe6d4"/></svg>',
}


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def esc(text):
    return html.escape(text, quote=True)


def resolve(href):
    """Return a usable href, or None when the target does not exist here."""
    href = href.strip()
    if href.startswith(("http://", "https://")):
        if "sierratreeandfungi.com" in href:
            return None
        return href
    if href.startswith(("tel:", "sms:", "mailto:", "#")):
        return href
    if not href.startswith("/"):
        return None
    base = href.split("#")[0].split("?")[0].rstrip("/") or "/"
    frag = href[len(base):] if href.startswith(base) else ""
    if base == "/":
        return "/" + frag.lstrip("/") if frag.startswith("#") else "/"
    if base in EXISTING:
        return base + "/" + (frag if frag.startswith("#") else "")
    if base in ALIAS:
        return ALIAS[base]
    return None


LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
IMG_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)$")


def map_image(url):
    for needle, data in IMAGE_MAP:
        if needle.lower() in url.lower():
            return data
    return None


def inline(text):
    """Render inline markdown (links only; the source uses no other inline markup)."""
    out = []
    pos = 0
    for match in LINK_RE.finditer(text):
        out.append(esc(text[pos:match.start()]))
        label, href = match.group(1), match.group(2)
        label = label.strip()
        target = resolve(href)
        if not label:
            pos = match.end()
            continue
        if target is None:
            out.append(esc(label))
        elif target.startswith(("http://", "https://")):
            out.append('<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (esc(target), esc(label)))
        else:
            out.append('<a href="%s">%s</a>' % (esc(target), esc(label)))
        pos = match.end()
    out.append(esc(text[pos:]))
    return "".join(out).strip()


def plain(text):
    """Strip markdown links down to their label text."""
    return LINK_RE.sub(lambda m: m.group(1), text).strip()


def link_tokens(line):
    """Parse a line that is nothing but [label](href) tokens."""
    items = []
    for match in LINK_RE.finditer(line):
        label = match.group(1).strip()
        target = resolve(match.group(2))
        if label and target:
            items.append((label, target))
    return items


def is_link_row(line):
    stripped = LINK_RE.sub("", line).strip()
    return line.startswith("[") and stripped == "" and "](" in line


def slug(text, used=None):
    base = re.sub(r"[^a-z0-9]+", "-", plain(text).lower()).strip("-")[:60] or "section"
    if used is None:
        return base
    candidate, n = base, 2
    while candidate in used:
        candidate = "%s-%d" % (base, n)
        n += 1
    used.add(candidate)
    return candidate


# --------------------------------------------------------------------------
# shared chrome
# --------------------------------------------------------------------------
def head(title, description, path):
    desc = esc(description)
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta name="author" content="Christopher Hodge, ISA Board Certified Master Arborist">
<meta name="theme-color" content="#0f2e22">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Sierra Tree and Fungi">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:image" content="%(hero)s">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%(title)s">
<meta name="twitter:description" content="%(desc)s">
<meta name="twitter:image" content="%(hero)s">
<meta name="geo.region" content="US-CA">
<meta name="geo.placename" content="Placerville, California">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/favicon.svg">
<link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
""" % {"title": esc(title), "desc": desc, "hero": HERO_IMG}


def mega_menu():
    cols = []
    for heading, links in NAV_GROUPS:
        items = "".join(
            '<li><a href="%s/">%s</a></li>' % (path, esc(label)) for path, label in links
        )
        cols.append('<div><h3>%s</h3><ul>%s</ul></div>' % (heading, items))
    return """      <div class="mega" id="mega-services">
        <div class="mega-grid">%s</div>
        <div class="mega-foot">
          <p>Not sure which you need? Ask a tree or mushroom question free, fifteen minutes, no obligation.</p>
          <div class="btn-row">
            <a class="btn btn--ghost" href="/services/">Browse all services</a>
            <a class="btn btn--amber" href="#consult">Request a consultation</a>
          </div>
        </div>
      </div>""" % "".join(cols)


def header(current):
    services_class = "has-mega is-current" if current not in ("/", None) else "has-mega"
    return """<header class="site-header">
  <div class="wrap header-bar">
    <a class="brand" href="/">
      %(logo)s
      <span>
        <span class="brand-name">Sierra Tree &amp; Fungi</span>
        <span class="brand-sub">Consulting Arborist &middot; Placerville, CA</span>
      </span>
    </a>
    <nav class="nav" id="primary-nav" aria-label="Primary">
      <ul>
        <li class="%(sc)s">
          <button class="navtop" type="button" aria-expanded="false" aria-controls="mega-services">Services %(caret)s</button>
%(mega)s
        </li>
        <li><a href="/#areas">Service areas</a></li>
        <li><a href="/#reviews">Reviews</a></li>
        <li><a href="/#about">About</a></li>
        <li><a href="#consult">Contact</a></li>
      </ul>
    </nav>
    <div class="header-cta">
      <a class="tel" href="%(tel)s">%(phone_icon)s %(phone)s</a>
      <a class="btn btn--amber" href="#consult">Get a quote</a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-nav">
        %(menu)s<span class="nav-toggle-label">Menu</span>
      </button>
    </div>
  </div>
</header>
""" % {
        "logo": ICONS["logo"], "caret": ICONS["caret"], "mega": mega_menu(),
        "tel": PHONE_TEL, "phone": PHONE_DISPLAY, "phone_icon": ICONS["phone"],
        "menu": ICONS["menu"], "sc": services_class,
    }


def footer():
    service_links = [
        ("/services", "All Services"),
        ("/arborist-reports", "Arborist Reports"),
        ("/tree-risk-assessment", "Tree Risk Assessment"),
        ("/tree-health-assessment", "Tree Health Assessment"),
        ("/how-to-tell-if-a-tree-is-dead-or-dying", "Dead or Dying Tree"),
        ("/oak-resource-management-plan-el-dorado-county", "Oak Technical Report"),
        ("/ceqa-arborist-reports-sacramento", "CEQA Arborist Reports"),
        ("/tree-inventory", "Tree Inventory and Survey"),
        ("/plant-health-care", "Plant Health Care"),
        ("/root-collar-excavation", "Root Collar Excavation"),
        ("/tree-fungus-treatment", "Treating Fungi on Trees"),
        ("/fungal-pathology-reports", "Fungal Pathology Reports"),
        ("/armillaria-root-rot", "Armillaria Root Rot"),
        ("/new-homeowner-tree-assessment", "New Homeowner Tree Assessment"),
        ("/oak-tree-removal-permit-el-dorado-county", "Oak Tree Removal Permit"),
        ("/protected-trees-in-california", "Protected Trees in California"),
        ("/oak-disease-sacramento", "Oak Disease, Sacramento Area"),
        ("/oak-galls", "Oak Galls and Gall Wasps"),
        ("/mediterranean-oak-borer", "Mediterranean Oak Borer"),
        ("/mistletoe-in-trees", "Mistletoe in Trees"),
        ("/redwood-tree-care", "Redwood Tree Care"),
        ("/tree-bark-and-sap-symptoms", "Bark and Sap Symptoms"),
        ("/defensible-space-el-dorado-county", "Wildfire Defensible Space"),
        ("/tree-roots-damaging-foundation", "Tree Roots and Property Damage"),
        ("/consulting-arborist-services", "Consulting Arborist Services"),
    ]
    areas = [
        "El Dorado County", "Sacramento County", "Placer County", "Amador County",
        "Placerville", "El Dorado Hills", "Cameron Park", "Shingle Springs",
        "Folsom", "Roseville", "Rocklin", "Auburn", "Granite Bay",
    ]
    company = [
        ("/#about", "About Christopher Hodge"),
        ("/#about", "Credentials"),
        ("/services/", "Consulting Arborist Services"),
        ("/#reviews", "Client reviews"),
        ("/#areas", "Service areas"),
        ("#consult", "Contact"),
        ("#consult", "Request a consultation"),
    ]
    return """<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <div>
        <a class="brand" href="/">%(logo)s<span><span class="brand-name">Sierra Tree &amp; Fungi</span><span class="brand-sub">Board Certified Master Arborist</span></span></a>
        <p>Consulting Arborist Serving El Dorado, Sacramento, Placer and Amador Counties, California</p>
        <ul class="footer-contact">
          <li>%(pin)s<span>Placerville, CA</span></li>
          <li>%(phone_icon)s<a href="%(tel)s">%(phone)s</a></li>
          <li>%(mail)s<a href="mailto:%(email)s">%(email)s</a></li>
        </ul>
        <div class="btn-row" style="margin-top:1.25rem">
          <a class="btn btn--amber" href="%(tel)s">Call now</a>
          <a class="btn btn--light" href="%(sms)s">Text a photo</a>
        </div>
      </div>
      <div>
        <h2>Services</h2>
        <ul>%(services)s</ul>
      </div>
      <div>
        <h2>Service areas</h2>
        <ul>%(areas)s</ul>
      </div>
      <div>
        <h2>Company</h2>
        <ul>%(company)s</ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>Disclosure: I also own <a href="https://www.norcaltreeconnect.com" target="_blank" rel="noopener noreferrer">www.norcaltreeconnect.com</a>, a regional tree service directory. It is a separate business and takes no part in my assessments or reports.</p>
      <p>&copy; <span data-year>2026</span> Sierra Tree and Fungi</p>
    </div>
  </div>
</footer>
<div class="action-bar">
  <a class="primary" href="%(tel)s">%(phone_icon)s Call</a>
  <a href="%(sms)s">%(sms_icon)s Text</a>
  <a href="#consult">%(form_icon)s Quote</a>
</div>
<script src="/assets/js/site.js" defer></script>
</body>
</html>
""" % {
        "logo": ICONS["logo"], "pin": ICONS["pin"], "phone_icon": ICONS["phone"],
        "mail": ICONS["mail"], "sms_icon": ICONS["sms"], "form_icon": ICONS["form"],
        "tel": PHONE_TEL, "sms": PHONE_SMS, "phone": PHONE_DISPLAY, "email": EMAIL,
        "services": "".join('<li><a href="%s/">%s</a></li>' % (p, esc(l)) for p, l in service_links),
        "areas": "".join("<li>%s</li>" % esc(a) for a in areas),
        "company": "".join('<li><a href="%s">%s</a></li>' % (p, esc(l)) for p, l in company),
    }


# --------------------------------------------------------------------------
# forms
# --------------------------------------------------------------------------
def form_block(form_name, form_id, heading, intro, include_date=True, button="Request my consultation"):
    options = "".join('<option value="%s">%s</option>' % (esc(o), esc(o)) for o in SERVICE_OPTIONS)
    date_field = ""
    if include_date:
        date_field = """          <div class="field">
            <label for="%(id)s-date">Preferred date <span class="hint">optional</span></label>
            <input type="date" id="%(id)s-date" name="Preferred date">
          </div>
""" % {"id": form_id}
    return """<div class="form-shell form-card" id="%(id)s-shell">
  <div class="form-success" role="status" aria-live="polite">
    %(check)s
    <div>
      <strong>Thanks, your message was sent</strong>
      <p>Christopher reads every enquiry himself and replies personally, usually the same day. Need an answer now? Call or text %(phone)s.</p>
    </div>
  </div>
  <h2>%(heading)s</h2>
  <p class="form-intro">%(intro)s</p>
  <form class="leadr-form" method="POST" action="%(action)s">
    <input type="hidden" name="_form" value="%(form_name)s">
    <input type="hidden" name="_page" value="">
    <input type="text" name="_gotcha" tabindex="-1" autocomplete="off" style="display:none">
    <div class="field-grid">
      <div class="field">
        <label for="%(id)s-name">Your name</label>
        <input type="text" id="%(id)s-name" name="name" autocomplete="name" required>
      </div>
      <div class="field">
        <label for="%(id)s-phone">Phone</label>
        <input type="tel" id="%(id)s-phone" name="phone" autocomplete="tel" required>
      </div>
      <div class="field field--full">
        <label for="%(id)s-email">Email</label>
        <input type="email" id="%(id)s-email" name="email" autocomplete="email" required>
      </div>
      <div class="field">
        <label for="%(id)s-city">Property city or address</label>
        <input type="text" id="%(id)s-city" name="Property location" autocomplete="address-level2" placeholder="Placerville, CA">
      </div>
      <div class="field">
        <label for="%(id)s-service">Service needed</label>
        <select id="%(id)s-service" name="Service needed">
          <option value="">Select a service</option>
          %(options)s
        </select>
      </div>
%(date)s      <div class="field field--full">
        <label for="%(id)s-detail">What are you seeing on the tree? <span class="hint">species, symptoms, deadlines</span></label>
        <textarea id="%(id)s-detail" name="Tree concern" rows="4" placeholder="Example: a valley oak near the house with conks at the base, and the county has asked for a report."></textarea>
      </div>
    </div>
    <button class="btn btn--amber btn--block btn--lg" type="submit">%(button)s</button>
    <p class="form-status" role="status" aria-live="polite"></p>
    <p class="tiny">A site assessment with a written report starts at $500. The site visit on its own is $250 for up to one hour on site. You can also text a photo of your tree to <a href="%(sms)s">%(phone)s</a>.</p>
  </form>
</div>""" % {
        "id": form_id, "heading": heading, "intro": intro, "action": FORM_ACTION,
        "form_name": esc(form_name), "options": options, "date": date_field,
        "button": button, "check": ICONS["check"], "phone": PHONE_DISPLAY, "sms": PHONE_SMS,
    }


def cta_section(heading, paragraphs, form_name="Consultation request", form_id="consult"):
    body = "".join("<p>%s</p>" % p for p in paragraphs)
    return """<section class="cta-band" id="consult">
  <div class="wrap">
    <div class="cta-grid contact-grid">
      <div>
        <p class="eyebrow">Free fifteen minutes</p>
        <h2>%(heading)s</h2>
        %(body)s
        <ul class="contact-list">
          <li>%(phone_icon)s<div><b>Call or text</b><a href="%(tel)s">%(phone)s</a></div></li>
          <li>%(sms_icon)s<div><b>Text a photo of your tree</b><a href="%(sms)s">%(phone)s</a></div></li>
          <li>%(mail_icon)s<div><b>Email</b><a href="mailto:%(email)s">%(email)s</a></div></li>
          <li>%(pin_icon)s<div><b>Based in</b><span>Placerville, California</span></div></li>
        </ul>
        <p class="price-note"><b>Pricing:</b> a full site assessment with a written report starts at $500. The site visit on its own is $250 for up to one hour on site. Serving El Dorado, Sacramento, Placer and Amador Counties, California.</p>
        <div class="btn-row">
          <a class="btn btn--amber btn--lg" href="%(tel)s">%(phone_icon)s Call %(phone)s</a>
          <a class="btn btn--light btn--lg" href="%(sms)s">%(sms_icon)s Text a photo</a>
        </div>
      </div>
      %(form)s
    </div>
  </div>
</section>
""" % {
        "heading": esc(heading) if "<" not in heading else heading,
        "body": body, "tel": PHONE_TEL, "sms": PHONE_SMS, "phone": PHONE_DISPLAY,
        "email": EMAIL, "phone_icon": ICONS["phone"], "sms_icon": ICONS["sms"],
        "mail_icon": ICONS["mail"], "pin_icon": ICONS["pin"],
        "form": form_block(form_name, form_id,
                           "Request a consultation",
                           "Tell me about the tree and I will come back to you personally, usually the same day."),
    }


# --------------------------------------------------------------------------
# markdown parsing
# --------------------------------------------------------------------------
def parse_source(filename):
    raw = open(os.path.join(SRC, filename), encoding="utf-8").read().split("\n")
    title = ""
    for line in raw[:5]:
        if line.startswith("Title:"):
            title = line[len("Title:"):].strip()
    nav_end = next(i for i, l in enumerate(raw) if l.startswith("[Book Consultation]"))
    try:
        foot = next(i for i, l in enumerate(raw) if l.startswith("![Sierra Tree and Fungi logo]"))
    except StopIteration:
        foot = len(raw)
    body = [l.rstrip() for l in raw[nav_end + 1:foot]]
    return title, body


def tokenize(body):
    """Turn the scraped body lines into a list of blocks."""
    blocks = []
    i = 0
    n = len(body)
    while i < n:
        line = body[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("# "):
            blocks.append(("h1", stripped[2:].strip()))
            i += 1
            continue
        if stripped.startswith("### "):
            blocks.append(("h3", stripped[4:].strip()))
            i += 1
            continue
        if stripped.startswith("## "):
            blocks.append(("h2", stripped[3:].strip()))
            i += 1
            continue
        m = IMG_RE.match(stripped)
        if m:
            blocks.append(("img", (m.group(1), m.group(2))))
            i += 1
            continue
        if stripped.startswith("> "):
            quote = [stripped[2:].strip()]
            i += 1
            while i < n and body[i].strip().startswith("> "):
                quote.append(body[i].strip()[2:].strip())
                i += 1
            blocks.append(("quote", quote))
            continue
        if re.match(r"^\*\s+|^\* ", stripped) or stripped.startswith("* "):
            items = []
            while i < n and body[i].strip().startswith("* "):
                items.append(body[i].strip()[2:].strip())
                i += 1
            blocks.append(("ul", items))
            continue
        if re.match(r"^\d+\.\s", stripped):
            items = []
            while i < n and re.match(r"^\d+\.\s", body[i].strip()):
                items.append(re.sub(r"^\d+\.\s*", "", body[i].strip()))
                i += 1
            blocks.append(("ol", items))
            continue
        if stripped == "Related":
            if i + 1 < n and is_link_row(body[i + 1].strip()):
                blocks.append(("related", body[i + 1].strip()))
                i += 2
                continue
            i += 1
            continue
        if is_link_row(stripped):
            blocks.append(("links", stripped))
            i += 1
            continue
        blocks.append(("p", stripped))
        i += 1
    return blocks


def is_breadcrumb(items):
    return bool(items) and "[Home](/)" in items[0]


def render_breadcrumbs(items):
    out = []
    for idx, item in enumerate(items):
        text = item.rstrip("/").strip()
        match = LINK_RE.match(text)
        last = idx == len(items) - 1
        if match and not last:
            target = resolve(match.group(2))
            label = esc(match.group(1).strip())
            if target:
                out.append('<li><a href="%s">%s</a></li>' % (esc(target), label))
            else:
                out.append("<li>%s</li>" % label)
        else:
            out.append('<li><span aria-current="page">%s</span></li>' % esc(plain(text)))
    return '<ol class="crumbs">%s</ol>' % "".join(out)


def render_list_item(item):
    """A list item is often '[link](url)trailing description' (source lists)."""
    match = LINK_RE.match(item.strip())
    if match and match.end() < len(item.strip()):
        trailing = item.strip()[match.end():].strip()
        if trailing and not trailing.startswith((",", ".", ";", ":", ")")):
            return "%s<span class=\"li-note\">%s</span>" % (inline(match.group(0)), inline(trailing))
    return inline(item)


def render_ul(items):
    return "<ul>%s</ul>" % "".join("<li>%s</li>" % render_list_item(x) for x in items)


def render_ol(items):
    return "<ol>%s</ol>" % "".join("<li>%s</li>" % render_list_item(x) for x in items)


def render_links(line, label=None):
    items = link_tokens(line)
    if not items:
        return ""
    chips = "".join(
        '<li><a href="%s"%s>%s</a></li>' % (
            esc(href),
            ' target="_blank" rel="noopener noreferrer"' if href.startswith("http") else "",
            esc(text),
        )
        for text, href in items
    )
    heading = '<h2>%s</h2>' % esc(label) if label else ""
    return '<aside class="related-block">%s<ul class="linkgrid">%s</ul></aside>' % (heading, chips)


def render_image(alt, url):
    data = map_image(url)
    if not data:
        return ""
    src, w, h = data
    return ('<figure><img src="%s" width="%d" height="%d" loading="lazy" decoding="async" alt="%s">'
            '<figcaption>%s</figcaption></figure>' % (src, w, h, esc(alt), esc(alt)))


# --------------------------------------------------------------------------
# interior page rendering
# --------------------------------------------------------------------------
def build_interior(filename, path, nav_label):
    title, body = parse_source(filename)
    blocks = tokenize(body)

    eyebrow = ""
    h1 = nav_label
    crumbs_html = ""
    lede = ""
    idx = 0

    if blocks and blocks[0][0] == "p" and len(blocks) > 1 and blocks[1][0] == "h1":
        eyebrow = plain(blocks[0][1])
        idx = 1
    if idx < len(blocks) and blocks[idx][0] == "h1":
        h1 = plain(blocks[idx][1])
        idx += 1
    if idx < len(blocks) and blocks[idx][0] == "ol" and is_breadcrumb(blocks[idx][1]):
        crumbs_html = render_breadcrumbs(blocks[idx][1])
        idx += 1

    rest = blocks[idx:]

    # the leading paragraph becomes the hero lede (first image, if any, follows it)
    hero_extra = ""
    while rest and rest[0][0] in ("img", "p"):
        kind, value = rest[0]
        if kind == "img":
            hero_extra += render_image(value[0], value[1])
            rest = rest[1:]
            continue
        lede = inline(value)
        rest = rest[1:]
        break

    # split out the trailing "Ask a Tree or Mushroom Question" block
    cta_heading = "Ask a Tree or Mushroom Question"
    cta_paragraphs = []
    for pos, (kind, value) in enumerate(rest):
        if kind == "h2" and plain(value).lower().startswith("ask a tree"):
            cta_heading = plain(value)
            for k2, v2 in rest[pos + 1:]:
                if k2 == "p":
                    cta_paragraphs.append(inline(v2))
            rest = rest[:pos]
            break
    if not cta_paragraphs:
        cta_paragraphs = ["Not sure what your tree needs? Ask me a tree or mushroom question free, fifteen minutes, no obligation."]

    # ---------------- render the main flow ----------------
    used_ids = set()
    out = []
    toc = []
    faq_mode = False
    faq_open = False
    first_h2_done = False
    lead_class = ' class="lead"'

    def close_faq():
        nonlocal faq_mode, faq_open
        if faq_open:
            out.append("</div></details>")
            faq_open = False
        if faq_mode:
            out.append("</div>")
            faq_mode = False

    for pos, (kind, value) in enumerate(rest):
        if kind == "h2":
            text = plain(value)
            close_faq()
            sid = slug(text, used_ids)
            toc.append((sid, text))
            out.append('<h2 id="%s">%s</h2>' % (sid, inline(value)))
            if "frequently asked questions" in text.lower():
                faq_mode = True
                out.append('<div class="faq">')
            first_h2_done = True
            continue
        if kind == "h3":
            if faq_mode:
                if faq_open:
                    out.append("</div></details>")
                out.append('<details><summary>%s</summary><div class="faq-body">' % inline(value))
                faq_open = True
            else:
                sid = slug(plain(value), used_ids)
                out.append('<h3 id="%s">%s</h3>' % (sid, inline(value)))
            continue
        if kind == "p":
            cls = "" if first_h2_done else lead_class
            out.append("<p%s>%s</p>" % (cls, inline(value)))
            continue
        if kind == "ul":
            out.append(render_ul(value))
            continue
        if kind == "ol":
            out.append(render_ol(value))
            continue
        if kind == "quote":
            out.append("<blockquote>%s</blockquote>" % "".join("<p>%s</p>" % inline(q) for q in value))
            continue
        if kind == "img":
            out.append(render_image(value[0], value[1]))
            continue
        if kind == "related":
            close_faq()
            out.append(render_links(value, "Related reading"))
            continue
        if kind == "links":
            close_faq()
            out.append(render_links(value, "Related"))
            continue
    close_faq()

    prose = "\n".join(x for x in out if x)

    # ---------------- sidebar ----------------
    toc_html = ""
    visible_toc = [(sid, text) for sid, text in toc][:12]
    if len(visible_toc) >= 4:
        items = "".join('<li><a href="#%s">%s</a></li>' % (sid, esc(text)) for sid, text in visible_toc)
        toc_html = """      <div class="side-card toc">
        <h2>On this page</h2>
        <ol>%s</ol>
      </div>
""" % items

    related_nav = [l for l in NAV_GROUPS]
    siblings = []
    for _, links in related_nav:
        for p, label in links:
            if p != path:
                siblings.append((p, label))
    # keep the sidebar list short and relevant: same nav group first
    group_links = []
    for _, links in related_nav:
        paths = [p for p, _ in links]
        if path in paths:
            group_links = [(p, l) for p, l in links if p != path][:5]
            break
    if not group_links:
        group_links = siblings[:5]

    sidebar = """    <aside class="sidebar">
      <div class="side-card side-card--pine">
        <h2>Talk to a Master Arborist</h2>
        <p>Documented, conflict free advice. No removal crews, no financial incentive to recommend work your tree does not need.</p>
        <a class="btn btn--amber" href="%(tel)s">%(phone_icon)s Call %(phone)s</a>
        <a class="btn btn--light" href="%(sms)s">%(sms_icon)s Text a photo</a>
        <a class="btn btn--light" href="#consult">Request a consultation</a>
        <p class="side-meta">Site assessment with a written report from $500. Site visit alone $250, up to one hour on site.</p>
      </div>
%(toc)s      <div class="side-card">
        <div class="badge-credential">
          <img src="%(badge)s" width="257" height="450" loading="lazy" decoding="async" alt="ISA Board Certified Master Arborist badge held by Christopher Hodge of Sierra Tree and Fungi">
          <p><strong>ISA Board Certified Master Arborist</strong> WE-14385B, and TRAQ qualified tree risk assessor.</p>
        </div>
      </div>
      <div class="side-card">
        <h2>Related services</h2>
        <ul>%(related)s</ul>
      </div>
    </aside>
""" % {
        "tel": PHONE_TEL, "sms": PHONE_SMS, "phone": PHONE_DISPLAY,
        "phone_icon": ICONS["phone"], "sms_icon": ICONS["sms"], "toc": toc_html,
        "badge": BADGE_IMG,
        "related": "".join('<li><a href="%s/">%s</a></li>' % (p, esc(l)) for p, l in group_links),
    }

    description = re.sub(r"<[^>]+>", "", lede) or title
    description = html.unescape(description)
    if len(description) > 185:
        description = description[:182].rsplit(" ", 1)[0] + "…"

    doc = [head(title, description, path), header(path)]
    doc.append("""<main id="main">
<section class="page-hero">
  <div class="wrap">
    %(crumbs)s
    %(eyebrow)s<h1>%(h1)s</h1>
    %(lede)s
    <div class="btn-row">
      <a class="btn btn--amber" href="%(tel)s">%(phone_icon)s Call %(phone)s</a>
      <a class="btn btn--light" href="%(sms)s">%(sms_icon)s Text a photo of your tree</a>
      <a class="btn btn--light" href="#consult">Request a consultation</a>
    </div>
  </div>
</section>
<div class="wrap page-layout">
  <article class="prose">
%(hero_extra)s%(prose)s
  </article>
%(sidebar)s</div>
""" % {
        "crumbs": crumbs_html,
        "eyebrow": '<p class="eyebrow">%s</p>' % esc(eyebrow) if eyebrow else "",
        "h1": esc(h1),
        "lede": '<p class="lede">%s</p>' % lede if lede else "",
        "tel": PHONE_TEL, "sms": PHONE_SMS, "phone": PHONE_DISPLAY,
        "phone_icon": ICONS["phone"], "sms_icon": ICONS["sms"],
        "hero_extra": hero_extra, "prose": prose, "sidebar": sidebar,
    })
    doc.append(cta_section(cta_heading, cta_paragraphs))
    doc.append("</main>\n")
    doc.append(footer())

    target_dir = os.path.join(ROOT, path.strip("/"))
    os.makedirs(target_dir, exist_ok=True)
    with open(os.path.join(target_dir, "index.html"), "w", encoding="utf-8") as fh:
        fh.write("".join(doc))
    return len(prose)


# --------------------------------------------------------------------------
# home page
# --------------------------------------------------------------------------
HOME_SERVICES = [
    ("Phase 01, Documentation", "Arborist Reports",
     "Permit ready arborist reports written to ISA best management practices: what a county reviewer, an HOA, an insurer, or a buyer needs in order to rely on the finding.",
     "/arborist-reports/", "Learn more about Arborist Reports"),
    ("Phase 02, Risk", "Tree Risk Assessments",
     "TRAQ qualified tree risk assessments with a documented rating, for a tree near people or structures where somebody needs a defensible answer rather than an impression.",
     "/tree-risk-assessment/", "Learn more about Tree Risk Assessments"),
    ("Phase 03, Diagnosis", "Tree Health Assessments",
     "Diagnosis of a declining tree from the roots up: what is wrong, why, and what to do about it, with a written finding and a plant health care plan you can act on.",
     "/tree-health-assessment/", "Learn more about Tree Health Assessments"),
    ("Phase 04, Permits", "Oak Technical Reports",
     "Need an Oak Technical Report for an El Dorado County building permit that affects native oaks? I prepare the permit ready report the county requires, and I know what its reviewers look for.",
     "/oak-resource-management-plan-el-dorado-county/", "Learn more about Oak Technical Reports"),
    ("Phase 05, Laboratory", "Fungal Pathology Reports",
     "Identification and assessment of wood decay fungi and pathogens affecting tree structure and health. Lab informed fungal pathology reports document the organism, the risk it poses, and management options.",
     "/fungal-pathology-reports/", "Learn more about Fungal Pathology Reports"),
    ("Phase 06, Stewardship", "Plant Health Care",
     "Ongoing care after the diagnosis: fixing the water, soil, and root collar problems behind most decline first, and treating only where a treatment fits what I found. No removal crews, and no work sold that the tree does not need.",
     "/plant-health-care/", "Learn more about Plant Health Care"),
]

REVIEWS = [
    ("“Arborist Christopher Hodge responded to my initial text promptly. He requested photos of the pine tree we were concerned about, made a preliminary analysis, and came to our property the same day to do a visual check and take measurements. His insights were helpful and encouraging, and the report he sent us was very professional and clear. I'm glad I found his website and consulted him.”",
     "L Joyce", "Google review"),
    ("“Christopher was amazing! We are trying to save a valley oak tree in our neighbors yard and we needed an ISA certified arborist to write a report. Christopher is not just an ISA board certified arborist, but a Master ISA certified arborist at that. I think I read that there’s only about 2% of all ISA arborist that achieve this level. His knowledge really showed and even though he was not able to go onto the neighbors property to do a full tree assessment, he did everything he could from my side and spent quite a lot of time with me in my yard taking photos and going over the entire tree to evaluate its health and what needs to be done to save the tree. The report that he wrote was very detailed and thorough. Thank you Christopher!”",
     "John Brace", "Google review"),
]

COUNTIES = [
    ("El Dorado County", "Placerville, El Dorado Hills, Cameron Park and Shingle Springs, plus the foothill parcels in between."),
    ("Sacramento County", "Folsom and the Sacramento area, including CEQA and development review work."),
    ("Placer County", "Roseville, Rocklin, Auburn and Granite Bay."),
    ("Amador County", "Oak woodland and foothill properties across the county."),
]

CITIES = [
    "Placerville arborist", "El Dorado Hills arborist", "Cameron Park arborist",
    "Shingle Springs arborist", "Folsom arborist", "Roseville arborist",
    "Rocklin arborist", "Auburn arborist", "Granite Bay arborist",
]


def build_home():
    title = "Consulting Arborist in Placerville, CA | Sierra Tree and Fungi"
    description = ("Board Certified Master Arborist Christopher Hodge provides arborist reports, tree risk "
                   "assessments, fungal pathology reports, Oak Technical Reports and plant health care across "
                   "El Dorado, Sacramento, Placer and Amador Counties. Call or text (530) 391-6100.")

    cards = "".join(
        """      <article class="card">
        <span class="phase">%s</span>
        <h3>%s</h3>
        <p>%s</p>
        <a class="card-link" href="%s">%s</a>
      </article>
""" % (esc(phase), esc(name), esc(copy), href, esc(link_label))
        for phase, name, copy, href, link_label in HOME_SERVICES
    )

    reviews = "".join(
        """      <article class="review">
        <div class="stars" aria-label="Five star review">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <blockquote><p>%s</p></blockquote>
        <cite>%s<span>%s</span></cite>
      </article>
""" % (esc(quote), esc(who), esc(src)) for quote, who, src in REVIEWS
    )

    counties = "".join(
        '      <article class="area-card"><h3>%s</h3><p>%s</p></article>\n' % (esc(name), esc(copy))
        for name, copy in COUNTIES
    )

    doc = [head(title, description, "/"), header("/")]

    doc.append("""<main id="main">

<section class="hero">
  <img class="hero-bg" src="%(hero)s" srcset="%(hero_srcset)s" sizes="100vw" width="1200" height="1600" alt="Sugar pine in the Sierra Nevada forest above El Dorado County, California" fetchpriority="high" decoding="async">
  <div class="wrap hero-inner">
    <div>
      <p class="eyebrow">Board Certified Master Arborist &middot; Placerville, CA</p>
      <h1>Consulting arborist for El Dorado, Sacramento, Placer and Amador Counties</h1>
      <p class="lede">Board Certified Master Arborist providing arborist reports, tree risk assessments, fungal pathology reports, Oak Technical Reports, and plant health care. A consulting arborist diagnoses and documents trees but does no removal work, so the advice is conflict free.</p>
      <ul class="hero-badges">
        <li>ISA Board Certified Master Arborist WE-14385B</li>
        <li>TRAQ qualified risk assessor</li>
        <li>15+ years of field observation</li>
        <li>No removal crews, no upsell</li>
      </ul>
      <div class="btn-row">
        <a class="btn btn--amber btn--lg" href="%(tel)s">%(phone_icon)s Call %(phone)s</a>
        <a class="btn btn--light btn--lg" href="%(sms)s">%(sms_icon)s Text a photo of your tree</a>
      </div>
      <p class="hero-note">Or text a photo of your tree to <a href="%(sms)s">%(phone)s</a>. Same day replies are the norm.</p>
      <div class="hero-credential">
        <img src="%(badge)s" width="257" height="450" loading="lazy" decoding="async" alt="ISA Board Certified Master Arborist badge, the highest credential the International Society of Arboriculture offers">
        <p>The highest credential the International Society of Arboriculture offers, held by fewer than two percent of ISA certified arborists.</p>
      </div>
    </div>
    %(form)s
  </div>
</section>

<section class="section section--sand" id="services">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">Scientific services</p>
      <h2>Master level tree care, documented in writing</h2>
      <p>I work with large landowners managing landscape health, property owners evaluating tree failure risk, and tree care professionals who need help diagnosing fungal diseases. Every engagement ends in a written, science based assessment you can act on.</p>
    </div>
    <div class="cards">
%(cards)s    </div>
    <div class="btn-row" style="margin-top:2rem">
      <a class="btn" href="/services/">Browse all services</a>
      <a class="btn btn--ghost" href="/consulting-arborist-services/">What a consulting arborist does</a>
    </div>
  </div>
</section>

<section class="section" id="about">
  <div class="wrap">
    <div class="split split--narrow-img">
      <div>
        <p class="eyebrow">Unbiased, science first stewardship</p>
        <h2>Conflict free advice from a Master Arborist</h2>
        <p>Sierra Tree and Fungi is the independent consulting practice of Christopher Hodge, an ISA Board Certified Master Arborist (WE-14385B), the highest credential the International Society of Arboriculture offers, and a TRAQ qualified tree risk assessor serving El Dorado, Sacramento, Placer, and Amador counties, California.</p>
        <p>I have no removal crews and no financial incentive to recommend unnecessary work, just documented, conflict free advice from an ISA Board Certified Master Arborist with TRAQ qualification. I provide tree risk assessments, arborist reports, plant health care, and Oak Technical Reports, and I help property owners make informed decisions, preserve the trees they value, and steward their land.</p>
        <p>The trees I work on are the ones that grow here: valley oak, blue oak, interior live oak, and California black oak through the foothills, and ponderosa pine, gray pine, sugar pine, incense cedar, and Douglas fir above them.</p>
        <div class="stats stats--light">
          <div class="stat"><b>15+</b><span>Years of field observation</span></div>
          <div class="stat"><b>$500</b><span>Site assessment with a written report, from</span></div>
          <div class="stat"><b>$250</b><span>Site visit alone, up to one hour on site</span></div>
        </div>
        <div class="btn-row" style="margin-top:1.75rem">
          <a class="btn" href="/tree-risk-assessment/">Tree risk assessments</a>
          <a class="btn btn--ghost" href="/arborist-reports/">Arborist reports</a>
        </div>
      </div>
      <figure>
        <img src="%(fungi)s" width="1080" height="1440" loading="lazy" decoding="async" alt="Laetiporus shelf fungi fruiting on a tree, a sign of internal wood decay that a fungal pathology report documents">
        <figcaption>Laetiporus shelf fungi, one of the wood decay fungi documented in a fungal pathology report.</figcaption>
      </figure>
    </div>
  </div>
</section>

<section class="section section--pine" id="fungi">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">The underground network</p>
      <h2>Why &ldquo;and Fungi&rdquo;?</h2>
    </div>
    <div class="split">
      <div>
        <blockquote class="pullquote">&ldquo;Fungi are the drivers of so many positive and negative outcomes in tree health and viability.&rdquo;</blockquote>
        <p>Why have fungi in my business name? Fungi are the drivers of so many positive and negative outcomes in tree health and viability. I have spent over fifteen years exploring forests studying fungal diversity and working as a consultant for an agricultural amendments company on mycorrhizal species.</p>
        <p>Being a consultant arborist who has spent almost all my life in El Dorado County, California, I have been able to monitor individual trees for decades and watch how they respond to different wood decay fungi, weather patterns, shifts in land use, and fire. I have spent countless hours searching for spores with a microscope, reading research papers, and talking to a wide variety of experts who have spent their lives in the forest to grasp how we can keep our trees, forests, and ecosystems healthy.</p>
        <div class="btn-row">
          <a class="btn btn--amber" href="/fungal-pathology-reports/">See fungal pathology reports</a>
          <a class="btn btn--light" href="/oak-disease-sacramento/">Oak tree disease identification</a>
        </div>
      </div>
      <div>
        <div class="stats">
          <div class="stat"><b>Sustainable</b><span>Stewardship through scientific observation</span></div>
          <div class="stat"><b>Lab informed</b><span>Microscopy and culture work behind the findings</span></div>
          <div class="stat"><b>Written</b><span>Every engagement ends in a report you can act on</span></div>
          <div class="stat"><b>Independent</b><span>No crews, no removal work, no conflict</span></div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section--sand" id="reviews">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">From clients</p>
      <h2>What the report was like</h2>
    </div>
    <div class="reviews">
%(reviews)s    </div>
    <div class="btn-row" style="margin-top:2rem">
      <a class="btn btn--ghost" href="https://maps.app.goo.gl/3TdDXWFtDpuNy1Bm7" target="_blank" rel="noopener noreferrer">Read reviews on Google</a>
      <a class="btn btn--amber" href="#consult">Request a consultation</a>
    </div>
  </div>
</section>

<section class="section" id="areas">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">Service area</p>
      <h2>Counties I serve</h2>
      <p>Consulting arborist services across the Sierra foothills and the Sacramento region, from Placerville out to Roseville, Folsom and Auburn.</p>
    </div>
    <div class="area-grid">
%(counties)s    </div>
    <h3 style="margin-top:2.5rem;font-size:1.1rem">Cities and towns</h3>
    <ul class="chips">
%(cities)s    </ul>
  </div>
</section>

<section class="section section--sand" id="pricing">
  <div class="wrap">
    <div class="section-head center">
      <p class="eyebrow">What it costs</p>
      <h2>Clear pricing, before you commit to tree work</h2>
      <p>A full site assessment with a written report starts at $500, and the site visit on its own is $250 for up to one hour on site. Not sure which you need? Ask me a tree or mushroom question free, fifteen minutes, no obligation.</p>
    </div>
    <div class="cards">
      <article class="card card--flat">
        <span class="phase">From $500</span>
        <h3>Site assessment and written report</h3>
        <p>A documented finding you can hand to a county reviewer, an HOA, an insurer, an attorney, or a buyer, prepared to recognized professional standards.</p>
        <a class="card-link" href="/arborist-reports/">What goes into a report</a>
      </article>
      <article class="card card--flat">
        <span class="phase">$250</span>
        <h3>Site visit alone</h3>
        <p>Up to one hour on site with a Board Certified Master Arborist, for when you need eyes on the tree and a verbal opinion rather than a document.</p>
        <a class="card-link" href="/consulting-arborist-services/">How a consultation works</a>
      </article>
      <article class="card card--flat">
        <span class="phase">Free, fifteen minutes</span>
        <h3>Ask a tree or mushroom question</h3>
        <p>No obligation. Text a photo of your tree to %(phone)s and I will tell you which service you need, including no service at all.</p>
        <a class="card-link" href="%(sms)s">Text a photo of your tree</a>
      </article>
    </div>
  </div>
</section>
""" % {
        "hero": HERO_IMG, "hero_srcset": HERO_SRCSET, "badge": BADGE_IMG, "fungi": FUNGI_IMG,
        "tel": PHONE_TEL, "sms": PHONE_SMS, "phone": PHONE_DISPLAY,
        "phone_icon": ICONS["phone"], "sms_icon": ICONS["sms"],
        "cards": cards, "reviews": reviews, "counties": counties,
        "cities": "".join("      <li>%s</li>\n" % esc(c) for c in CITIES),
        "form": form_block(
            "Quote request", "quote",
            "Get a quote on a written assessment",
            "Tell me about the tree and I will reply personally, usually the same day. Site assessment with a report from $500.",
            include_date=False, button="Request my quote",
        ),
    })

    doc.append(cta_section(
        "Ask a Tree or Mushroom Question",
        ["A full site assessment with a written report starts at $500, and the site visit on its own is $250 for up to one hour on site. Not sure which you need? Ask me a tree or mushroom question free, fifteen minutes, no obligation.",
         "Or text a photo of your tree to <a href=\"%s\" style=\"color:#fff\">%s</a>." % (PHONE_SMS, PHONE_DISPLAY)],
    ))
    doc.append("</main>\n")

    doc.append("""<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "name": "Sierra Tree and Fungi",
  "description": "Independent consulting arborist practice of Christopher Hodge, ISA Board Certified Master Arborist (WE-14385B) and TRAQ qualified tree risk assessor.",
  "telephone": "+1-530-391-6100",
  "email": "Christopher@SierraTreeandFungi.com",
  "image": "%s",
  "address": {"@type": "PostalAddress", "addressLocality": "Placerville", "addressRegion": "CA", "addressCountry": "US"},
  "areaServed": [
    {"@type": "AdministrativeArea", "name": "El Dorado County, California"},
    {"@type": "AdministrativeArea", "name": "Sacramento County, California"},
    {"@type": "AdministrativeArea", "name": "Placer County, California"},
    {"@type": "AdministrativeArea", "name": "Amador County, California"}
  ],
  "priceRange": "$250 - $500+",
  "knowsAbout": ["Arborist reports", "Tree risk assessment", "Tree health assessment", "Fungal pathology", "Oak Technical Reports", "Plant health care"]
}
</script>
""" % HERO_IMG)
    doc.append(footer())

    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write("".join(doc))


# --------------------------------------------------------------------------
def main():
    if not os.path.isdir(SRC):
        sys.exit("source pages not found: %s" % SRC)
    build_home()
    for filename, path, label in PAGES:
        size = build_interior(filename, path, label)
        print("built %-48s %6d chars" % (path, size))
    print("built /")


if __name__ == "__main__":
    main()
