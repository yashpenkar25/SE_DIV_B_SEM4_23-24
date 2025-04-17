import sqlite3
import pandas as pd
from tkinter import *
import webbrowser
from PIL import ImageTk, Image
import data_scrapi
import matplotlib.pyplot as plt

# Function to create a SQLite database and table
def create_table():
    conn = sqlite3.connect('product_details.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                (id INTEGER PRIMARY KEY, name TEXT, price TEXT, link TEXT)''')
    conn.commit()
    conn.close()

# Function to insert product details into the database
def insert_product(name, price, link):
    conn = sqlite3.connect('product_details.db')
    c = conn.cursor()
    c.execute('''INSERT INTO products (name, price, link) VALUES (?, ?, ?)''', (name, price, link))
    conn.commit()
    conn.close()

def start(root, item):
    dat = data_scrapi.start(item)
    for i in range(len(dat['Product Info'])):
        insert_product(dat['Product Info'][i], dat['Price'][i], dat['Link To Site'][i])
    print("Data inserted into database successfully!")
    root.destroy()
    ini(dat)

# Function to shorten the product name for display
def shorten(title):
    max_length = 35
    title_split = title.split()
    out = ""
    if len(title_split[0]) <= max_length:
        out += title_split[0]
    for word in title_split[1:]:
        if len(word) + len(out) + 1 <= max_length:
            out += ' ' + word
        else:
            break
    return out[0:]

# Main function to initialize GUI
def ini(dat):
    data = dat
    link = data['Link To Site']
    price = data['Price']
    name = data['Product Info']
    root = Tk()
    root.geometry("1140x480")
    root.config(bg="black")
    frame1 = Frame(root, highlightbackground="grey", highlightthickness=10, padx=60, pady=40)
    frame1.place(x=60, y=80)
    frame2 = Frame(root, highlightbackground="grey", highlightthickness=10, padx=60, pady=40)
    frame2.place(x=610, y=80)
    img1 = ImageTk.PhotoImage(Image.open("amazonlogo.png"))
    img2 = ImageTk.PhotoImage(Image.open("amazonlogo.png"))
    # Change the image path for Snapdeal logo
    label1 = Label(root, image=img1)
    label2 = Label(root, image=img2)
    label1.place(x=220, y=25)
    label2.place(x=800, y=25)
    Label(frame1, text="Product Name", font='Helvetica 10 bold').grid(row=0, column=0)
    Label(frame1, text="Price", font='Helvetica 10 bold').grid(row=0, column=1)
    Label(frame1, text="Link To Site", font='Helvetica 10 bold').grid(row=0, column=2)
    Label(frame2, text="Product Name", font='Helvetica 10 bold').grid(row=0, column=0)
    Label(frame2, text="Price", font='Helvetica 10 bold').grid(row=0, column=1)
    Label(frame2, text="Link To Site", font='Helvetica 10 bold').grid(row=0, column=2)

    def callback(url):
        webbrowser.open_new_tab(url)

    for i in range(min(len(price), 10)):
        if i < 5:
            Label(frame1, text="Rs " + price[i]).grid(row=i + 1, column=1, padx=10)
            Label(frame1, text=shorten(name[i])).grid(row=i + 1, column=0)
            link_label = Label(frame1, text="link", font=('Helvetica 15 underline'), fg="blue", cursor="hand2")
            link_label.grid(row=i + 1, column=2)
            link_label.bind("<Button-1>", lambda e, url=link[i]: callback(url))
        elif i < 10:
            Label(frame2, text="Rs " + price[i]).grid(row=i - 4, column=1, padx=10)
            Label(frame2, text=shorten(name[i])).grid(row=i - 4, column=0)
            link_label = Label(frame2, text="link", font=('Helvetica 15 underline'), fg="blue", cursor="hand2")
            link_label.grid(row=i - 4, column=2)
            link_label.bind("<Button-1>", lambda e, url=link[i]: callback(url))

    # Create a color dictionary for different retailers
    color_dict = {'Amazon': 'blue', 'Snapdeal': 'orange'}

    # Create lists to store bar colors and labels
    bar_colors = []
    legend_labels = []

    # Iterate through the data and assign colors based on the retailer
    for retailer in data['Sold By']:
        color = color_dict.get(retailer, 'gray')  # Default color for unknown retailers
        bar_colors.append(color)
        if retailer not in legend_labels:
            legend_labels.append(retailer)

    # Create the bar chart with customized colors
    plt.figure(figsize=(10, 6))
    bars = plt.barh(dat['Product Info'], dat['Price'], color=bar_colors)

    # Add legend
    legend_handles = [plt.Rectangle((0,0),1,1, color=color_dict[label]) for label in legend_labels]
    plt.legend(legend_handles, legend_labels)

    plt.xlabel('Price')
    plt.ylabel('Product Name')
    plt.title('Product Prices by Retailer (Sorted)')
    
    # Reverse y-axis to display prices in ascending order
    plt.gca().invert_yaxis()

    plt.tight_layout()
    plt.show()


    root.mainloop()

# Main function to initialize the search window
def search_window():
    root1 = Tk()
    root1.geometry("350x350")

    Label(root1, text="").grid(row=0, column=0)
    Label(root1, text="").grid(row=1, column=0)
    Label(root1, text="").grid(row=2, column=0)
    Label(root1, text="").grid(row=3, column=0)
    Label(root1, text="Enter the product", font=("", 12)).grid(row=4, column=0, pady=10, columnspan=3)

    item = Entry(root1, width=25, font=("Bahnschrift SemiLight", 13))
    item.grid(row=5, column=0, columnspan=3, padx=60)
    bt = Button(root1, text="Search", command=lambda: start(root1, item.get()), padx=15, pady=10)
    bt.grid(row=6, column=0, columnspan=5, pady=10, padx=60)

    Label(root1, text=" I agree to the Terms & Conditions ", fg='grey').grid(row=7, column=0, pady=90, padx=30,columnspan=20)

    frame3 = Frame(root1, highlightbackground="grey", highlightthickness=10, padx=60, pady=40)
    frame3.place(x=610, y=400)

    root1.mainloop()


# Call the create_table() function before using the database
create_table()

# Call the search_window() function to start the search interface
search_window()
