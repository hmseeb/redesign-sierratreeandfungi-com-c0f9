# Sierra Tree and Fungi — website

Conversion-focused static site for Sierra Tree and Fungi, the independent consulting
arborist practice of Christopher Hodge (ISA Board Certified Master Arborist WE-14385B,
TRAQ qualified) in Placerville, California.

## Stack

Vanilla HTML, CSS and JavaScript. No build step is required to serve the site: every
page is a committed `index.html`.

```
index.html                       home page (hero quote form, services, reviews, areas, contact)
<service-path>/index.html        one directory per service page, 25 in total
assets/css/site.css              design system (single stylesheet)
assets/js/site.js                navigation, form submission, confirmation handling
images/source/                   photography carried over from the previous site
favicon.svg                      favicon
build.py                         generator used to produce the HTML pages
```

## Regenerating the pages

`build.py` renders the committed HTML from the page content stored outside the published
site, so header, footer, navigation, forms and CTA bands stay identical across all 26
pages:

```sh
python3 build.py
```

## Forms

Every form POSTs to LeadrVision:

* `action="https://vision.leadrai.com/api/forms/246b1deb67270022258874839c48348b"`
* hidden `_form` (form name), `_page` (set to `window.location.href` on load), `_gotcha` honeypot
* human readable field names, with `name`, `email` and `phone` used verbatim
* JavaScript submits the same payload as JSON to the same endpoint and shows an inline
  confirmation on `{"ok": true}`; without JavaScript the plain POST works and the
  `?submitted=1` return shows the same confirmation

## Local preview

```sh
python3 -m http.server 8000
```

Then open <http://localhost:8000/>.
