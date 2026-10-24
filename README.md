# readme-assets

The README images and the social preview for
[artistic-color-palettes](https://github.com/youssef4laa/artistic-color-palettes). They live on this
branch, not on the release branch, so Anthropic's plugin directory doesn't scan marketing images as
part of the plugin. Its validator reads the printable text inside image files and flagged one of
these PNGs as a download-and-run command.

`.github/scripts/readme_assets.py` on the release branch regenerates them from the skill's own data.
The publishing checklist in the main README says how to update this branch.
