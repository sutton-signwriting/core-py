# sutton-signwriting-core
[![Source Code on GitHub](https://img.shields.io/badge/source-GitHub-lightgrey?logo=github)](https://github.com/sutton-signwriting/core-py)
[![Docs](https://img.shields.io/badge/docs-sutton--signwriting.io-blue)](https://www.sutton-signwriting.io/core-py)
[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sutton-signwriting/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[![Spec](https://img.shields.io/badge/spec-Formal%20SignWriting-blueviolet)](https://datatracker.ietf.org/doc/html/draft-slevinski-formal-signwriting)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17553763.svg)](https://doi.org/10.5281/zenodo.17553763)


[![PyPI](https://img.shields.io/pypi/v/sutton-signwriting-core)](https://pypi.org/project/sutton-signwriting-core/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/sutton-signwriting-core)](https://pypistats.org/packages/sutton-signwriting-core)
[![CI](https://github.com/sutton-signwriting/core-py/actions/workflows/ci.yml/badge.svg)](https://github.com/sutton-signwriting/core-py/actions)


`sutton-signwriting-core` is a Python library that supports general processing of SignWriting text

This library supports both Formal SignWriting in ASCII (FSW) and SignWriting in Unicode (SWU) character sets, , along with the associated query languages and style string.  See [draft-slevinski-formal-signwriting](https://www.ietf.org/archive/id/draft-slevinski-formal-signwriting-10.html) for detailed specification.

> **Author:** [Steve Slevinski](https://steveslevinski.me)  
**Channel:** [YouTube](https://www.youtube.com/channel/UCXu4AXlG0rXFtk_5SzumDow)  
**Support:** [Patreon](https://www.patreon.com/signwriting)  
**Donate:** [sutton-signwriting.io](https://donate.sutton-signwriting.io)

## Useful Links

- **Source:** [GitHub](https://github.com/sutton-signwriting/core-py)
- **PyPI:** [pypi.org/project/sutton-signwriting-core](https://pypi.org/project/sutton-signwriting-core/)
- **Documentation:** [sutton-signwriting.io/core-py](https://www.sutton-signwriting.io/core-py)
- **Issues:** [GitHub Issues](https://github.com/sutton-signwriting/core-py/issues)
- **Discussion:** [Gitter](https://gitter.im/sutton-signwriting/community)

---

## Installation

```bash
pip install sutton-signwriting-core
```

---

## Usage

```python
from sutton_signwriting_core import (
    fsw_is_type, fsw_parse_symbol,
    fsw_to_coord, key_to_id
)

# FSW is type
fsw_is_type('S10000', 'hand')
True

# FSW parse symbol
fsw_parse_symbol('S10000500x500-C')
{'symbol': 'S10000', 'coord': [500, 500], 'style': '-C'}

# FSW to coord
fsw_to_coord('500x500')
[500, 500]

# FSW symbol key to 16-bit ID
key_to_id('S10000')
1
```

All functions are **fully typed**, **validated**, and **documented** with Python-style docstrings (Google format). Run `help(swu_to_fsw)` for details.

---

## Development

### Development Steps

```bash
# 1. Clone the repo
git clone https://github.com/sutton-signwriting/core-py.git
cd core-py

# 2. Install Poetry (if you don’t have it)
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"

# 3. Create the virtual environment and install deps
poetry install

# 4. Activate the environment (Poetry 2+)
poetry env activate
#   (copy and execute the returned command)

# 5. Run the test suite
pytest -v

# 6. Code coverage and HTML report
pytest --cov
pytest -v --cov=sutton_signwriting_core --cov-report=html
pytest --cov=sutton_signwriting_core --cov-report=xml

# 7. Lint / format / type-check
black .
ruff check .
mypy src

# 8. Update Version string
pyproject.toml:version = "1.0.0"
src/sutton_signwriting_core/__init__.py:__version__ = "1.0.0"
sphinx-docs/source/conf.py:release = "1.0.0"
sphinx-docs/source/conf.py:version = "1.0"

# 9. Create HTML documentation
cd sphinx-docs
sphinx-build -b html -a -E source/ ../docs/

# 10. Build distributions
poetry build

# 11. Publish to pypi
poetry publish

# 12. Git commit, push, and tag
git commit -m "message"
git push origin main
git tag v1.0.0 && git push --tags
```

---

## License

MIT – see [`LICENSE`](LICENSE) for details.
> *Maintained by Steve Slevinski – <Slevinski@signwriting.org>*

---

## SignWriting Resources

- **Website:** [signwriting.org](https://signwriting.org/)
- **Resources:** [sutton-signwriting.io](https://www.sutton-signwriting.io/)
- **Wikipedia:** [SignWriting](https://en.wikipedia.org/wiki/SignWriting)
- **Grokipedia** [SignWriting](https://grokipedia.com/page/SignWriting)
- **Forum:** [swlist](https://www.signwriting.org/forums/swlist/)
- **Facebook:** [Sutton SignWriting Group](https://www.facebook.com/groups/SuttonSignWriting/)
