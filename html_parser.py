import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import subprocess
import os
import cssbeautifier


def prettify_css(css):
    options = cssbeautifier.default_options()
    options.indent_size = 2  # You can adjust this and other options as needed
    return cssbeautifier.beautify(css, options)

def write_to_file(file_path, content):
    """Writes content to a file."""
    with open(file_path, 'w', encoding="UTF-8") as file:
        file.write(content)



def read_from_file(file_path):
    """Reads content from a file."""
    with open(file_path, 'r', encoding="UTF-8") as file:
        return file.read()
    


def delete_files(file_path1, file_path2, file_path3):
    """Deletes a file."""    
    os.remove(file_path1)
    os.remove(file_path2)
    os.remove(file_path3)



def run_purify_css(html_file_path, css_file_pat):
    try:
        subprocess.run(['node', 'removeUnusedCss.js', html_file_path, css_file_pat], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred in purifyCSS: {e}")



def fetch_html(domain):
    try:
        response = requests.get(f'http://{domain}/', timeout=5)
        print("Response collected")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        print("Soup created")
        html = soup.prettify()
        print("HTML prettified")
        return html
    except requests.exceptions.RequestException as e:
        print(f"Error fetching HTML for {domain}: {e}")
        return None



# Create a session object
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})



def fetch_page(domain):
    """Fetch the content of the webpage."""
    try:
        response = session.get(f"http://{domain}")
        if response.text == '':
            response = session.get(f"http://{domain}", timeout=6)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching HTML for {domain}: {e}")
        return None
    return response.text


def process_resource(url, tag):
    """Process a resource and update the tag accordingly."""
    try:
        response = session.get(url, timeout=3)
        content_type = response.headers.get('Content-Type')

        # Check if the URL ends with .css and if the content type is CSS
        if url.endswith('.css') and 'text/css' in content_type:
            try:
                tag.replace_with("")  # Remove the original link tag
                return response.text  # Return the CSS text
            except ValueError:
                print(f"Error while inlining resource from: {url}")
                return ''  # Return empty string on error
        else:
            print(f"Skipping non-CSS resource: {url}")
            return ''  # Return empty string for non-CSS resources

    except requests.exceptions.RequestException as e:
        print(f"Error while fetching {url}: {e}")
        return ''  # Return empty string on fetch error

    except Exception as e:
        print(f"General error in inline_resource for {url}: {e}")
        return ''  # Return empty string on general error


def combined_purified_files(html, css):
    """Combine purified HTML and CSS into one file."""
    html = read_from_file(html)
    BeautifulSoup(html, 'html.parser')
    css = read_from_file(css)
    if css == "":
        return html
    else:
        html = html.replace("</head>", f"<style>{css}</style></head>")
        return html

def remove_script_tags(soup):
    """Remove all script tags from the BeautifulSoup object."""
    for script in soup.find_all("script"):
        script.decompose()



def main(domain):
    # Fetch and parse the original page content
    html_content = fetch_page(domain)
    if html_content is None:
        return None
    original_html = BeautifulSoup(html_content, 'html.parser')

    css = ""
    # Inline external CSS
    for link_tag in original_html.find_all('link', rel='stylesheet'):
        href = link_tag.get('href')
        if href:
            full_url = urljoin(f"https://{domain}", href)
            css += process_resource(full_url, link_tag)

    remove_script_tags(original_html)


    # Write the CSS to the file
    write_to_file("style.css", css)

    # Add a link tag to the head of the HTML for the CSS file
    try:
        new_link_tag = original_html.new_tag("link", rel="stylesheet", href="style.css")
        if original_html.head:
            original_html.head.append(new_link_tag)
        else:
            # Create a head tag and insert it at the beginning of the html body
            head_tag = original_html.new_tag("head")
            original_html.html.insert(0, head_tag)
            if head_tag != None:
                head_tag.append(new_link_tag)
            else:
                print("Error while adding link tag to HTML")
    except ValueError:
        print("Error while adding link tag to HTML")


    write_to_file("processed.html", original_html.prettify())

    # Run purify_css
    run_purify_css("processed.html", "style.css")

    purified_html = combined_purified_files("processed.html", "purified.css")

    return BeautifulSoup(purified_html, 'html.parser').prettify()
