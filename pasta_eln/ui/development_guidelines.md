# GUI Design

- Rely on standard PySide6 widgets and the active theme as much as possible.
  - Change stylesheets, colours, or sizes manually only when the standard style is not visible or readable enough.
  - In each area (sidebar, table, details), highlight at most one button (`default` property set to `True`).
- Recreate the Figma design where technically practical and not unnecessarily complicated.
  - Still reassess every element for necessity.
  - Use changes imposed by the PySide6 implementation as opportunities to adapt the design.
    - Example: Figma gives the sidebar an open/close button, while PySide6 provides a splitter. Use the button for another purpose instead, such as creating a new project.
- Show both icon and text where possible; icon-only controls create uncertainty.
  - Use `ri.iconname` icons.
  - An icon without text must have an obvious meaning.
- Colours:
  - Prefer not to change colours manually, although it is sometimes necessary.
  - Always use colours from the theme (see `palette.py`), even when this is more involved.
  - Icons usually need explicit colouring; see `project_sidebar` and `table_view`.
  - Test light and dark themes. The theme should keep all content readable.
- Create example projects with very long names in every field to check whether the layout breaks.
  - Also test empty and very short names.
  - Solve these problems through layout rather than hard-truncating strings, so the complete name remains accessible. For example, users can widen columns in `table_view`.
- Many actions available through buttons should also be available through a context menu.
  - Most context-menu actions should also be available through buttons.
  - Context menus for sidebar projects and table-view entries are the most important.
- The more important an action is, the more visible it should be and the fewer clicks should be needed to find it.
- It should always be clear what the user is editing or viewing: which project, table, or sample.

# Code Design

- `project_sidebar.py` is a good example.
- Follow pylint rules.
- Prefer more comments to fewer.
- In `__init__`, first define the variables needed by the class.
  - Then define and configure the individual widgets in their initial state.
  - Then create the layouts that contain each widget.
  - Change the widget's own style when needed.
  - Then create the main layout and add all sublayouts.
  - Then create and connect signals.
  - Finally write code that must run immediately, usually `signal.emit`.
  - Give every widget and layout its own commented block.
- Make runtime changes to widgets in the `paint` method.
- Prefer moving behaviour into functions or new classes/files when it improves readability.
  - Function and variable names may be long if they accurately describe their purpose.
- Keep files that concern the same widget or form part of the same widget together in one directory.
  - Create new classes or custom widgets when a subwidget becomes too large.
- Use type hints.
