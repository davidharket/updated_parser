import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import subprocess
import os



def write_to_file(file_path, content):
    """Writes content to a file."""
    with open(file_path, 'w') as file:
        file.write(content)



def read_from_file(file_path):
    """Reads content from a file."""
    with open(file_path, 'r') as file:
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
        response = requests.get(f'http://{domain}/', timeout=8)
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



def process_resource(url, soup, tag, n):
    """Process a resource and update the tag accordingly."""
    try:
        response = session.get(url, timeout=3)
        content_type = response.headers.get('Content-Type')
        if response.text == "":
            # Wait for a few seconds before fetching the resource
            time.sleep(5)  # Adjust the number of seconds as needed
            response = session.get(url)
        if 'text' in content_type and response.text:
            # Create a new tag based on content type
            external_css = soup.new_tag("style" if 'css' in content_type else None)
            try:
                tag.replace_with("")
                print(f"Wrote CSS from: {url}")
                return external_css
            
            except ValueError:
                print(f"Error while inlining resource from: {url}")
                pass
        else:
            print(f"Skipping non-text resource or empty response: {url}")
            return None
            

    except requests.exceptions.RequestException as e:
        print(f"Error while fetching {url}: {e}")

    except Exception as e:
        print(f"General error in inline_resource for {url}: {e}")



def combined_purified_files(html, css):
    """Combine purified HTML and CSS into one file."""
    html = read_from_file(html)
    BeautifulSoup(html, 'html.parser')
    css = read_from_file(css)
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
    for n, link_tag in enumerate(original_html.find_all('link', rel='stylesheet')):
        href = link_tag.get('href')
        if href:
            full_url = urljoin(f"https://{domain}", href)
            css.append(f"\n{process_resource(full_url, original_html, link_tag, n)}")

    remove_script_tags(original_html)

    write_to_file("processed.html", original_html.prettify())

    write_to_file("styles.css", css)

    run_purify_css("processed.html", "styles.css")

    purified_html = combined_purified_files("processed.html", "purified.css")

    return(BeautifulSoup(purified_html).prettify()) 