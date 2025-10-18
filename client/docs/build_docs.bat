REM Build the docs for the sub-modules.
uv run sphinx-apidoc -o docs/common_types_module_docs --implicit-namespaces --module-first common_types
uv run sphinx-apidoc -o docs/games_module_docs --implicit-namespaces --module-first games
uv run sphinx-apidoc -o docs/networking_module_docs --implicit-namespaces --module-first networking
uv run sphinx-apidoc -o docs/ui_module_docs --implicit-namespaces --module-first ui

REM Build the documentation.
uv run sphinx-build -M html docs docs/_build/html