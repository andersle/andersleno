import pathlib
import urllib
from lxml import etree
import lxml.html


def find_html_files():
    html_files = []
    for filei in pathlib.Path(".").rglob("*.ipynb"):
        html = filei.with_suffix(".html")
        if html.is_file():
            html_files.append(html)
    return html_files


def extract_article(html_file):
    parser = etree.HTMLParser()
    tree = etree.parse(html_file, parser)
    article = tree.xpath("//article")[0]
    try:
        style = tree.xpath("//article/style")[0]
    except IndexError:
        style = None
    articles = []
    for node in article.iterchildren():
        if node.tag != "style":
            articles.append(lxml.html.tostring(node).decode("utf-8"))

    article_txt = "\n".join(articles)

    if style:
        style_output = html_file.parent / "style-nbsphinx.css"
        with open(style_output, "w") as output:
            output.write(style.text)

    article_name = f"article-{html_file.name}"

    html_output = html_file.parent / article_name

    with open(html_output, "w") as output:
        output.write(article_txt)

    notebook_path = urllib.parse.quote(
        str(html_file.relative_to("build/html/posts").with_suffix(".ipynb")),
        safe="",
    )

    rst_binder = f""".. image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/andersle/andersleno/main?urlpath=/tree/{notebook_path}"""

    rst_output = html_file.parent / "link.rst"
    with open(rst_output, "w") as output:
        output.write(rst_binder)


def main():
    files = find_html_files()
    for filei in files:
        extract_article(filei)


if __name__ == "__main__":
    main()
