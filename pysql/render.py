"""
render.py
====================================
Rendering runctions
"""

import re


def formatTable(html, color):
    """
    Format html table.
    """
    html = re.sub(r"<td>False</td>", "<td bgcolor=\"" + color + "\">False</td>", html)

    return html


def styleButton(html):
    html = re.sub(r"<button name=\"df\">False", "<button name=\"df\" class=\"button-false\">False", html)
    
    return html