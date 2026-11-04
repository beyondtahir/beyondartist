# Use BeyondArtist with no image model

You can still get finished, usable designs with no paid image generator. BeyondArtist switches to work that depends on ideas, words and layout, using free local tools.

## What you get

- Type-led thumbnails, posters and carousel slides, set in real fonts.
- Designs built on your own photo or a permitted existing asset.
- The same research, concepts, Feed Test, Quality Gate and delivery files.
- Properly shaped Urdu, Arabic, Persian and Hindi text.

Generated illustration and photo-style scenes are the part you give up, and the agent will say so instead of passing off a layout as generated art.

## Try it

~~~text
Use BeyondArtist. I have no image generator. Make a type-led YouTube thumbnail for
my video about [topic]. Use my photo at [path] if it helps the idea.
~~~

Under the hood the agent writes a small spec and renders it:

~~~json
{"width": 1280, "height": 720, "background": "#101820", "blocks": [
  {"text": "Stop\nguessing", "x": 60, "y": 90, "width": 1100, "size": 210, "weight": 900, "color": "#F2AA4C", "line_height": 0.92}
]}
~~~

~~~sh
python3 skills/beyondartist/scripts/autopilot.py typeset --spec spec.json --out design.png
python3 skills/beyondartist/scripts/autopilot.py gate design.png --boxes-json design.boxes.json
~~~

`typeset` needs Chrome or Chromium and internet access to load the font the first time. `gate` needs Pillow. The HTML file written beside your design can be opened and edited in any text editor.
