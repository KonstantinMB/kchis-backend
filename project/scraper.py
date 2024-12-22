import requests
from bs4 import BeautifulSoup
import openpyxl
from datetime import datetime

def scrape_properties():

        # Base URL
    base_url = "https://sales.bcpea.org/properties?perpage=12&court={court}&p={page}"

    # Court-to-City mapping
    court_to_city = {
        1: "Благоевград", 2: "Бургас", 3: "Варна", 4: "Велико Търново",
        5: "Видин", 6: "Враца", 7: "Габрово", 8: "Добрич", 9: "Кърджали",
        10: "Кюстендил", 11: "Ловеч", 12: "Монтана", 13: "Пазарджик",
        14: "Перник", 15: "Плевен", 16: "Пловдив", 17: "Разград",
        18: "Русе", 19: "Силистра", 20: "Сливен", 21: "Смолян",
        28: "София град", 27: "София окръг", 22: "Стара Загора",
        23: "Търговище", 24: "Хасково", 25: "Шумен", 26: "Ямбол"
    }

    # Create an Excel workbook
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Properties"

    # Add headers to the Excel sheet
    sheet.append([
        "City", "Court", "Date Published", "Property Title", "Square Meters",
        "Price", "Location", "Address", "Private Judicial Officer",
        "Term", "Announcement Date"
    ])

    # Function to scrape a single page
    def scrape_page(court, page):
        url = base_url.format(court=court, page=page)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        properties = soup.find_all("div", class_="item__group")
        
        # Extract data from the current page
        page_data = []
        for property_card in properties:
            # Extract city
            city = court_to_city.get(court, "Unknown")
            
            # Extract date published
            date_published = property_card.find("div", class_="date").get_text(strip=True) if property_card.find("div", class_="date") else "N/A"
            
            # Extract property title
            title = property_card.find("div", class_="title").get_text(strip=True) if property_card.find("div", class_="title") else "N/A"
            
            # Extract square meters
            category = property_card.find("div", class_="category")
            square_meters = (
                category.get_text(strip=True).replace(" кв.м", "")
                if category
                else "N/A"
            )
            
            # Extract price
            price = property_card.find("div", class_="price").get_text(strip=True) if property_card.find("div", class_="price") else "N/A"
            
            # Extract location (settlement)
            location_label = property_card.find("div", class_="label__group")
            location = (
                location_label.find("div", class_="info").get_text(strip=True)
                if location_label and location_label.find("div", class_="info")
                else "N/A"
            )
            
            # Extract address
            address_label = property_card.find("div", class_="label__group label__group--double")
            address = (
                address_label.find("div", class_="info").get_text(strip=True)
                if address_label and address_label.find("div", class_="info")
                else "N/A"
            )
            
            # Extract private judicial officer
            officer_label = property_card.find("div", class_="label", string="ЧАСТЕН СЪДЕБЕН ИЗПЪЛНИТЕЛ")
            judicial_officer = (
                officer_label.find_next_sibling("div", class_="info").get_text(strip=True)
                if officer_label and officer_label.find_next_sibling("div", class_="info")
                else "N/A"
            )
            
            # Extract term
            term_label = property_card.find("div", class_="label", string="СРОК")
            term = (
                term_label.find_next_sibling("div", class_="info").get_text(strip=True)
                if term_label and term_label.find_next_sibling("div", class_="info")
                else "N/A"
            )

            # Extract announcement date
            announcement_label = property_card.find("div", class_="label", string="ОБЯВЯВАНЕ НА")
            announcement_date = (
                announcement_label.find_next_sibling("div", class_="info").get_text(strip=True)
                if announcement_label and announcement_label.find_next_sibling("div", class_="info")
                else "N/A"
            )
                    
            # Append to the page data
            page_data.append([
                city, court, date_published, title, square_meters, price,
                location, address, judicial_officer, term, announcement_date
            ])
        return page_data

    # Iterate through all courts and their pages
    all_data = []

    for court in court_to_city.keys():
        page = 1
        while True:
            print(f"Scraping court {court} (city: {court_to_city[court]}), page {page}...")
            page_data = scrape_page(court, page)
            if not page_data:  # Stop if no data is found
                break
            all_data.extend(page_data)
            page += 1

    # Write data to Excel
    for row in all_data:
        sheet.append(row)

    # Save the Excel file with a timestamp
    filename = f"data/properties_{datetime.now().strftime('%Y%m%d')}.xlsx"
    workbook.save(filename)
    return filename
