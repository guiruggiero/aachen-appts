import time
import schedule # https://schedule.readthedocs.io/en/stable/installation.html

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

from email.message import EmailMessage
import smtplib
import sys
sys.path.insert(1, "../secrets")
import gmail

def check_for_appt():
    try:
        check_start_time = time.strftime("%H:%M", time.localtime())
        print("Starting Auslaenderamt check - " + check_start_time)

        # Initialize Selenium browser
        options = webdriver.ChromeOptions() # https://github.com/GoogleChrome/chrome-launcher/blob/main/docs/chrome-flags-for-tools.md
        # options.add_argument("--headless=new")
        # options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        browser = webdriver.Chrome(options=options)

        # Start page, direct link of https://termine.staedteregion-aachen.de/auslaenderamt/ + Aufenthaltsangelegenheiten (first option)
        browser.get("https://termine.staedteregion-aachen.de/auslaenderamt/select2?md=1")
        # print("Page opened")
        time.sleep(3)

        # Click "+" in the right category (Erteilung/Verlängerung Aufenthalt - Nachname: A - Z (Team 3))
        accordion = browser.find_element(By.ID, "header_concerns_accordion-340").click()
        # print("Clicked accordion")
        time.sleep(2)
        ActionChains(browser).scroll_by_amount(0, 300).perform() # Scrolls to put button into view
        button_plus = browser.find_element(By.ID, "button-plus-268").click()
        # print("Clicked plus button")
        time.sleep(1)
        button_plus = browser.find_element(By.ID, "button-plus-268").click()
        # print("Clicked plus button")
        time.sleep(1)
        
        # Exception tests
        # raise KeyboardInterrupt
        # raise Exception

        # Move to the next page
        button_next = browser.find_element(By.ID, "WeiterButton")
        ActionChains(browser).scroll_by_amount(0, 1000).perform() # Scrolls all the way down
        # print("Scrolled down")
        time.sleep(2)
        button_next.click()
        # print("Clicked next button")
        time.sleep(2)
        button_ok_overlay = browser.find_element(By.ID, "OKButton").click()
        # print("Clicked OK button")
        time.sleep(3)

        # # Save HTML before selecting the office to see if "Kein freier Termin" is already there
        # source_before_office = browser.page_source
        # html_before_office = open("before_office.html", "w")
        # html_before_office.write(source_before_office)
        # html_before_office.close()
        # print("Saved HTML before office selection\n")

        # # Search the HTML to test the .find() method without "Kein freier Termin" there
        # source_before_office = browser.page_source
        # search_before = source_before_office.find("Kein freier Termin")
        # print(search_before)

        # Select the office
        ActionChains(browser).scroll_by_amount(0, 1000).perform() # Scrolls all the way down
        # print("Scrolled down")
        time.sleep(2)
        office_buttons = browser.find_elements(By.NAME, "select_location")
        # Find the right button to press
        for button in office_buttons:
            # print(button.accessible_name)
            # print(button.aria_role)
            # print(button.parent)
            # print(button.tag_name)
            # print(button.id)

            if button.aria_role == "button":
                button.click()
                # print("Clicked office button")
                time.sleep(3)

        # # Save HTML after selecting the office to compare with before
        # source_after_office = browser.page_source
        # html_after_office = open("after_office.html", "w")
        # html_after_office.write(source_after_office)
        # html_after_office.close()
        # print("Saved HTML after office selection\n")

        # Check if "Kein freier Termin" is in the page
        source = browser.page_source
        search = source.find("Kein freier Termin")
        # print(search)
        if search != -1: # Found string somewhere, no appointments available
            print("No appointments available :-(\n")

        else: # Appointment(s) available
            print("Appointment(s) available!")

            # Create mail
            email = EmailMessage()
            email["From"] = "Gui's bot <" + gmail.SENDER + ">"
            email["To"] = [gmail.GUI, gmail.GEORGIA]
            email["Subject"] = "Urgent - EU Blue Card appointment(s) available - "
            email.set_content("It looks like there are appointments available!<br><br>"
                "Go to https://termine.staedteregion-aachen.de/auslaenderamt/select2?md=1 and grab one ASAP.", subtype="html")

            # Start the connection
            smtpserver = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtpserver.ehlo()
            smtpserver.login(gmail.SENDER, gmail.GMAIL_APP_PASSWORD)

            # Send email
            smtpserver.send_message(email)

            # Close the connection
            smtpserver.quit()
            print("Email sent\n")

        # Close the browser
        browser.close()

    # Ctrl+C interruption error
    except KeyboardInterrupt:
        print("\n\nAlright, done for now")
        exit()

    # All other errors
    except:
        # Create email
        email = EmailMessage()
        email["From"] = "Gui's bot <" + gmail.SENDER + ">"
        email["To"] = [gmail.GUI]
        email["Subject"] = "Script error"
        email.set_content("Check up on the instance, the script is having problems.", subtype="html")

        # Start the connection
        smtpserver = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtpserver.ehlo()
        smtpserver.login(gmail.SENDER, gmail.GMAIL_APP_PASSWORD)

        # Send email
        smtpserver.send_message(email)

        # Close the connection
        smtpserver.quit()
        print("\nError warning email sent\n")
        exit()

# check_for_appt()

# # Timed run
# print("Program started\n")
# check_for_appt()
# schedule.every(5).minutes.do(check_for_appt)
# while True:
#     schedule.run_pending()
#     time.sleep(1)