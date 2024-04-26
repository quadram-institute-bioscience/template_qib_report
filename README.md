__Leonardo de Oliveira Martins<sup>1</sup>__
<br>
<sub>1. Quadram Institute Bioscience, Norwich Research Park, NR4 7UQ, UK</sub>

Template for PDF (and HTML) generation from a markdown file using pandoc.

Short description on how to install the software:

```bash
conda env update -f environment.yml # update conda evironment after changing dependencies
pip install -e . # installs in development mode (modifications to python files are live)
```

There is a system package which might need to be installed outside conda, `texlive`:
```
apt-get install texlive-full
```
This is for the PDF report generation. `texlive-full` is huge (6GB of disk), but you won't need to worry about missing fonts again.
If you want something smaller you can try, from smaller to larger: `texlive-latex-base`, `texlive-latex-recommended`, 
`texlive-fonts-recommended`, and `texlive-latex-extra`, until `pandoc` compiles the PDF without errors.

The PDF report generation relies on the [Eisvogel latex template for pandoc](https://github.com/Wandmalfarbe/pandoc-latex-template), 
released under a BSD 3-clause.
For the HTML report, the template is based on the [markdown-css](https://github.com/otsaloma/markdown-css) template,
released under an MIT licence. 
Both are included in this repository, in the [assets folder](./assets).
The complete list of dependencies is described in the file [environment.yml](./environment.yml).
Please let me know if there are missing dependencies (or feel free to modify it yourself).

These templates are based on the report generation from https://github.com/quadram-institute-bioscience/peroba . 

## How to run
The markdown files are a bit different between the HTML and PDF versions: the headers and the figures (the PDF assumes PDF figures while HTML
assume an image format). 
The YAML header is translated into latex by pandoc, and we have to tell pandoc they're already translated (thus the
`\`file.pdf\` {=latex}` syntax).


```
pandoc template_for_pdf.md -o result.pdf --from markdown --template assets/eisvogel --listings

pandoc -s template_for_html.md -o result.html --toc"
```

## License 
SPDX-License-Identifier: GPL-3.0-or-later

Copyright (C) 2024-today  [Leonardo de Oliveira Martins](https://github.com/leomrtns)

This is free software; you can redistribute it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later
version (http://www.gnu.org/copyleft/gpl.html).
