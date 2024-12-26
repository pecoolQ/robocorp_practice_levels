from time import sleep
from robocorp.tasks import task
from robocorp import browser


from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.Browser import Selenium
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(browser_engine="chrome",slowmo=100)
    open_robot_order_website()
    orders = get_orders()
    
    for index, order in enumerate(orders):
        close_annoying_modal()
        fill_the_form(index,order)

        pdfFile = store_receipt_as_pdf(order['Order number'])
        screenshotFile = screenshot_robot(order['Order number'])
        embed_screenshot_to_receipt(screenshotFile,pdfFile)
        reset_after_confirm_order()
    archive_receipts()

def open_robot_order_website():
    """Open robot and navigate to website"""
    # TODO: Implement your function here
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """Getting orders from csv"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

    library = Tables()
    orders = library.read_table_from_csv("orders.csv")
    return orders

def close_annoying_modal():
    """Close popup that show up at beginning"""
    page = browser.page()
    #role dialog is one of parents(like 5th parent role)
    selector = "[role='dialog'] p:text('By using this order form, I give up all my constitutional rights for the benefit of RobotSpareBin Industries Inc.')"

    if page.query_selector(selector)  is not None:
        page.click("button:text('Yep')")


def fill_the_form(index,row):
    """Fill in form with different options"""
    print(f"Fill inn order:{index}")
    page = browser.page()
    page.select_option("#head",row["Head"])
    page.click(f"input[name='body'][value='{row['Body']}']")
    #input[placeholder="Enter the part number for the legs"]' is another example
    page.fill("input[placeholder='Enter the part number for the legs']",row['Legs'])
    page.fill("#address",row['Address'])
    page.click("button:text('Preview')")

    page.click("button:text('ORDER')")
    
    Click_Confirm_To_Order()

    print(f"Finish filling in for the order:{index}")

def Click_Confirm_To_Order():
    page = browser.page()
    for i in range(10):
        if page.query_selector("h3:text('Receipt')") is not None:
            break
        else:
            page.click("button:text('ORDER')")
            sleep(0.2)

def store_receipt_as_pdf(order_number):
    """Store robot images as pdf"""
    pdf_filePath = "output/receipts/order_"+ order_number+".pdf"
    page = browser.page()

    sales_results_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    print(sales_results_html)
    pdf.html_to_pdf(sales_results_html, pdf_filePath)
    
    return pdf_filePath
    
def screenshot_robot(order_number):
    """Takes screenshot of the ordered bot image"""
    page = browser.page()
    screenshot_path = "output/screenshots/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path
    
def reset_after_confirm_order():
    page = browser.page()
    page.click("text=Order another robot")

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embed screenshot to reciept"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(
        image_path=screenshot,
    source_path=pdf_file,
    output_path=pdf_file
    )

def archive_receipts():
    """Archive receipts after embeding screentshot"""
    folderPath = "./output/receipts/"
    lib = Archive()
    lib.archive_folder_with_zip(folderPath, 'receipts.zip')