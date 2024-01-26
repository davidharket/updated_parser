from html_parser import main, delete_files
from db_manager import ManageDB

print("Imported modules")
db_path = 'new_html_files.db'

db = ManageDB(db_path)
domains = db._collect_data()
#print(domains)
list_of_no_html_domains = []


for category in domains:
    print("Starting to fetch HTML")
    for index, domain in enumerate(domains[category]):
        print(f"Fetching HTML for {domain}")
        html = main(domain)
        if html:
            print(f"HTML fetched for {domain}")
            db._insert_data(db_path, category, domain, html)
        else:
            list_of_no_html_domains.append(domain)
            print(f"Error fetching HTML for {domain}")
            continue
        delete_files("processed.html", "style.css", "purified.css")
db._close_database()