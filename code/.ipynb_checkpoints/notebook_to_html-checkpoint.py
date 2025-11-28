import sys
import nbformat
from nbconvert import HTMLExporter
 
def convert_to_html_simple(notebook_path):
    """Converts a Jupyter Notebook to an HTML file using nbconvert Python API."""

    #source: https://nbconvert.readthedocs.io/en/latest/api/exporters.html#nbconvert.exporters.export
    try:
        #Load the notebook content
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = nbformat.read(f, as_version=4)
 
        #Initialize and convert
        html_exporter = HTMLExporter()
        print("Starting conversion using the minimal HTMLExporter API...")
        (body, resources) = html_exporter.from_notebook_node(notebook_content)
 
        #Name new file after original notebook
        html_file = notebook_path.replace(".ipynb", ".html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(body)

        print(f"HTML file created: {html_file}")
 
    except FileNotFoundError:
        print(f"\nFile not found at '{notebook_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"\nFailed due to an API error: {e}")
        sys.exit(1)
 
 
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python notebook_to_html.py <notebook file path>")
        sys.exit(1)
    notebook_file = sys.argv[1]
    convert_to_html_simple(notebook_file)