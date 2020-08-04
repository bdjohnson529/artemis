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
    html = re.sub(r"<button class=\"button-clickable\">False", "<button name=\"df\" class=\"button-clickable button-false\">False", html)
    html = re.sub(r"<button class=\"button-clickable\">Masked", "<button name=\"df\" class=\"button-masked\" data-toggle='modal' data-target='#edit-modal'>Masked", html)

    
    return html

