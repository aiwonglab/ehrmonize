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
    'sphinx_rtd_theme',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

autoapi_dirs = ['../ehrmonize']
autoapi_generate_api_docs = True
autoapi_options = ['members', 'special-members','show-inheritance','undoc-members',  ]

# -- Options for HTML output

html_theme = 'furo'

# -- Options for EPUB output
epub_show_urls = 'footnote'
