# -- Project information

project = 'EHRmonize'
copyright = '2024, João Matos'
author = 'João Matos'

release = '0.1'
version = '0.1.0a4'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'autoapi.extension',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

autosummary_generate = True

autoapi_dirs = ['../ehrmonize']
autoapi_generate_api_docs = True
autoapi_options = ['members', 'undoc-members', 'special-members', ]

# -- Options for HTML output

# html_theme = 'furo'
html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/aiwonglab/ehrmonize",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
    ],
    "show_version_warning_banner": True,
    "navigation_depth": 5,
    "secondary_sidebar_items": ["page-toc"],
    "show_toc_level": 5,
    "show_prev_next": False,

}

html_context = {
    "github_user": "aiwonglab",
    "github_repo": "ehrmonize",
    "github_version": "main",
    "doc_path": "docs",
}

# -- Options for EPUB output
epub_show_urls = 'footnote'
