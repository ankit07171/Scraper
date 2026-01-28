import matplotlib.pyplot as plt

def plot_bar(category_count):
    category_count.plot(kind='bar')
    plt.title("Comment Category Distribution")
    plt.xlabel("Category")
    plt.ylabel("Count")
    plt.show()

def plot_pie(category_count):
    category_count.plot(
        kind='pie',
        autopct='%1.1f%%',
        startangle=90
    )
    plt.title("Comment Category Percentage")
    plt.ylabel("")
    plt.show()
