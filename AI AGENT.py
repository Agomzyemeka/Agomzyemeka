import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import tkinter as tk
from tkinter import messagebox

def scrape_google_form(form_url):
    # Send a request to the Google Form page and get the HTML content
    response = requests.get(form_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all the input fields and options for each question
    input_fields = soup.find_all('input', {'type': 'text'})
    select_options = soup.find_all('div', {'role': 'listbox'})
    
    # Extract the question names and corresponding options
    questions = [field['aria-label'] for field in input_fields]
    options = [options.find_all('div', {'role': 'option'}) for options in select_options]
    
    return questions, options

def fill_google_form(form_url, user_inputs):
    driver = webdriver.Chrome()  # You'll need to have ChromeDriver installed: https://sites.google.com/a/chromium.org/chromedriver/downloads
    driver.get(form_url)

    # Wait for the form to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@role='listbox']")))

    input_fields = driver.find_elements(By.XPATH, "//input[@type='text']")
    select_options = driver.find_elements(By.XPATH, "//div[@role='listbox']")

    for i, input_value in enumerate(user_inputs):
        if i < len(input_fields):
            input_fields[i].send_keys(input_value)
        elif i - len(input_fields) < len(select_options):
            select_options[i - len(input_fields)][-1].click()  # Click on the last option in each question dropdown

    # Submit the form
    submit_button = driver.find_element(By.XPATH, "//span[text()='Submit']")
    submit_button.click()

    # Wait for submission confirmation
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='freebirdFormviewerViewResponseConfirmationMessage']")))
    print("Form submitted successfully!")

    driver.quit()

def on_submit():
    google_form_url = entry_google_form.get()
    number_of_responses = entry_responses.get()

    try:
        number_of_responses = int(number_of_responses)
    except ValueError:
        messagebox.showerror("Error", "Number of responses must be a valid integer.")
        return

    user_inputs = [google_form_url, str(number_of_responses)]
    # Step 1: Scrape the Google Form to get questions and options
    questions, options = scrape_google_form(google_form_url)

    # Step 2: Fill and submit the Google Form with user inputs
    for _ in range(number_of_responses):
        random_inputs = [q + " Response " + str(_+1) for q in questions]
        fill_google_form(google_form_url, random_inputs)

    messagebox.showinfo("Success", "Google Form filled and submitted successfully for the specified number of responses!")

# Create the main UI window
root = tk.Tk()
root.title("Google Form AI Agent")

# Create input fields and labels
label_google_form = tk.Label(root, text="Enter Google Form URL:")
label_google_form.pack()
entry_google_form = tk.Entry(root, width=50)
entry_google_form.pack()

label_responses = tk.Label(root, text="Enter the number of responses:")
label_responses.pack()
entry_responses = tk.Entry(root, width=20)
entry_responses.pack()

# Create the submit button
btn_submit = tk.Button(root, text="Submit", command=on_submit)
btn_submit.pack()

root.mainloop()
