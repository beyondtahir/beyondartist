# Changelog

Public release numbers start at 1.0.0. Earlier numbers in old test reports, such as 1.3 or 1.8, are internal development builds from before the public release.

## 1.1.0 (unreleased)

### Added

- **Autopilot:** one video link becomes tested, finished designs with no brief.
- **Feed Test:** designs shown among real competitor thumbnails at phone, desktop and sidebar size.
- **Quality Gate:** measures exact copy, phone-size contrast and text height, overlay collisions, focal weight, clutter and repeats of past work.
- **Typesetter:** exact text in real fonts, including shaped Urdu, Arabic, Persian and Hindi, with an editable HTML file.
- **Delivery pack:** upload-ready export, master, phone preview and checksums.
- **Claude Code plugin** and marketplace manifests, with `/beyondartist:autopilot`, `/beyondartist:thumbnail`, `/beyondartist:carousel` and `/beyondartist:brand-setup`.
- A documented route for people with no image model.
- A real Autopilot run and demo in `docs/autopilot.md`.
- Issue forms for install problems and for sharing work.

### Changed

- Design Memory search now favors records that match more of the query, and reports how much of the query each result covers.
- Memory errors now name the accepted values and the command to run.
- The skill description now covers posters and Autopilot, so it triggers on more of what it can do.
- Showcase images are high-quality JPEGs, which makes installs much smaller. The original PNGs remain in the v1.0.1 repository ZIP.
- `LICENSE` is now the plain MIT text so GitHub can detect it. Asset terms remain in `ASSET-LICENSE.md`.

## 1.0.1 (2026-10-14)

- Native image model first, connected models next, with complete creation fallbacks.

## 1.0.0 (2026-10-14)

- First public release.
