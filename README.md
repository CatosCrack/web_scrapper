# Web Scrapper
This is a simple web scrapper that uses Python's urllib and smtplib to send an email containing the available campsites in a very popular campgound in Bergeronne, Québec. The scrapper for a 2-night stay in a target month starting either on Friday or Saturday and sends a csv file containing the nightly rate per campground for each of the dates checked.

![csv_file](https://github.com/CatosCrack/web_scrapper/blob/main/images/csv_screenshot.png)

## Target Website

![website screenshot](https://github.com/CatosCrack/web_scrapper/blob/main/images/website_screenshot.png)

The website uses utm parameters to communicate to the server the check-in and check-out dates along with other options. 

A standard query looks like this:

  https://vacancesessipit.com/en/search/?start_date=05%2F15%2F2024&end_date=05%2F16%2F2024&tabs=terrain-de-camping&sortby=price&emplacement%5B%5D=mer-et-monde&equipment_type=0&longueur_type=0&equipment_services=0&equipment_damperage=0

In this query, the check-in date is set by the parameter **start_date** and the check_out date is given by **end_date**. Since the objective is to find a campsite with a view of the St. Lawrence River, the parameter **services%5B%5D=vue-sur-le-fleuve** must also be present.

In the website itself, we are looking for very specific elements to obtain the name of the campground as well as the nightly rate. These lines of HTML look like these:

```html
<h2 class="std_card--title">MER 1</h2> <!-- Campsite Name -->

<div class="std_card--price-p">50$</div> <!-- Nightly Rate -->
```

## scrapper.py
The scrapper uses a target month and a target duration as arguments of the function *scrapper*

```python
scrapper(target_month, duration)
```
Using the **target_month** parameter, the script will create a Python Calendar using the Calendar library. Using **datetime.timedelta()**, the script will create a timedelta object that will be used to find the desired ranges in the calendar. Using **timedelta()** allows us to handle the start and end of the month with ease since the **Calendar()** object operates based on weeks. The script will then set the start and end dates as follows:

```python
# Check-in date
start_day = date.day
start_month = date.month

# Check-out date
end_date = date + duration
end_day = end_date.day
end_month = end_date.month

# Set UTM parameters for search
url = f"https://vacancesessipit.com/en/search/?start_date={start_month}%2F{start_day}%2F{current_year}&end_date={end_month}%2F{end_day}%2F{current_year}&tabs=terrain-de-camping&sortby=price&emplacement%5B%5D=mer-et-monde&equipment_type=0&longueur_type=0&equipment_services=0&equipment_damperage=0&services%5B%5D=vue-sur-le-fleuve"
```
Then we use **urllib.request.urlopen()** to get the HTML code from the website

```python
# urlopen will get an encoded HTTP response
page = urlopen(url)

# The urlopen method will get a sequence of bytes that represents the source code of the website
# The decode method will decode the response using utf-8 encoding 
html = page.read().decode("utf-8")
```
In order to find in the code the HTML tags containing the campsite name and rate, we will use RegEx and python's re library.

```python
name_pattern = '<h2 class="std_card--title">.*</h2>'
price_pattern = '<div class="std_card--price-p">.*</div>'

campsite_names = re.findall(name_pattern, html)
campsite_prices = re.findall(price_pattern, html)
```
All the data is then stored to the **data_dict** dictionary which will then be used as the content for another dictionary called **results**. 

After gathering the results for all the dates in the target month, we turn **results** into a pandas dataframe and create a csv file from it. Once the csv file is saved in the root directory, the script calls the **send_email** function from email_sender.py to share the document via email.

## email_sender.py
The **send_email** function requires a file path for the attachement that will be added to the email address.

Using the email library, we create a multipart email that contains a body (MIMEText) and an attachment (MIMEBase).

```python
message = MIMEMultipart()
message["From"] = address
message["To"] = address
message["Subject"] = "Camping - Search Results"

message.attach(MIMEText(body, "plain"))

# Encode attachement
filename = attachment
with open(filename, "rb") as file:
part = MIMEBase("application", "octet-stream")
part.set_payload(file.read())

# Encode attachment using ASCII characters
encoders.encode_base64(part)
part.add_header("Content-Disposition", f"attachment; filename= {filename}")

# Add attachment to multipart email
message.attach(part)
```
Finally, we create a SMTP context to send the email using the gmail servers.

```python
 with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(address, password)
        server.sendmail(address, address, message)
```
