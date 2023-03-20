"""
Generate report.
"""
import os
from jinja2 import Environment, FileSystemLoader

current_directory = os.path.dirname(os.path.abspath(__file__))

def render_template(data: dict, template: str="./template/report.html"):
    """
    Fill parsed data into report.html .
    """
    env = Environment(loader=FileSystemLoader(current_directory))
    return env.get_template(template).render(**data)
