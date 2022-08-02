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


def _modify_img(html_file, tree):
    img = tree.xpath("//img")
    for node in img:
        alt = pathlib.Path(node.get("alt")).name
        node.attrib["alt"] = alt
        src = pathlib.Path(node.get("src")).name
        path1 = html_file.parents[0]
        path2 = html_file.parents[2]
        path = str(path1.relative_to(path2))
        node.attrib["src"] = f"../../../_static/images/{path}/{src}"


def _save_sections(html_file, tree):
    sections = tree.xpath("//section")
    for i, section in enumerate(sections):
        section_name = html_file.parent / f"section-{i+1}-{html_file.name}"
        with open(section_name, "w") as output:
            output.write(lxml.html.tostring(section).decode("utf-8"))


def _save_style(html_file, tree):
    #style = tree.xpath("//main/div/style")[0]
    style = tree.xpath("//article/style")[0]
    style_name = html_file.with_suffix(".css")

    with open(style_name, "w") as output:
        output.write(style.text)


def extract_article(html_file):
    parser = etree.HTMLParser()
    tree = etree.parse(html_file, parser)
    #article = tree.xpath("//main/div")[0]
    article = tree.xpath("//article")[0]

    _modify_img(html_file, tree)
    _save_sections(html_file, tree)
    _save_style(html_file, tree)

    articles = []
    for node in article.iterchildren():
        if node.tag != "style":
            articles.append(lxml.html.tostring(node).decode("utf-8"))

    article_txt = "\n".join(articles)

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

    rst_output = html_file.with_suffix(".rst")
    with open(rst_output, "w") as output:
        output.write(rst_binder)


def main():
    files = find_html_files()
    for filei in files:
        print(f"Reading {filei.name}")
        extract_article(filei)


if __name__ == "__main__":
    main()
