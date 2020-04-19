#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wget

from argparse import ArgumentParser
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from cairosvg import svg2pdf
from PyPDF2 import PdfFileMerger


def download_pdf(out_pdf, url_pattern, out_tmp_dir):
    pdf_pages = []
    i = 1

    try:
        while True:
            pdf_page = download_pdf_page(out_tmp_dir, url_pattern, i)
            pdf_pages.append(pdf_page)
            i += 1
    except HTTPError:
        print(f"Impossible de télécharger la page {i}. " +
              "On suppose que la précédente était la dernière.")

    # Merges pages
    merger = PdfFileMerger()
    print("\nMerging all pages into one PDF\n")
    for pdf_page in pdf_pages:
        merger.append(pdf_page)
    merger.write(out_pdf)
    merger.close()


def download_pdf_page(out_dir, url_pattern, i):
    page_url = url_pattern.format(i)
    page_prefix = f"{out_dir}/{i}"
    page_svg = f"{page_prefix}.svg"
    page_pdf = f"{page_prefix}.pdf"

    # Download
    print(f"Downloading page {i}")
    wget.download(page_url, out=page_svg)

    # Convert SVG -> PDF
    print(f"\nConverting page {i} to PDF\n")
    svg2pdf(url=page_svg, write_to=page_pdf)

    return page_pdf


# CLI options
parser = ArgumentParser(description='Télécharger un livre')
parser.add_argument('output_file', help="""Fichier PDF de sortie""")
parser.add_argument('url_pattern', help="""URL exemple contenant les pages à
        récupérer. La chaîne de caractère doit contenir {} pour compléter le
        numéro de page. Exemple : https://www.site.com/page{}.svgz""")
args = parser.parse_args()

with TemporaryDirectory() as tmp_dir:
    download_pdf(args.output_file, args.url_pattern, tmp_dir)
