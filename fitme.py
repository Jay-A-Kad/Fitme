import requests
import matplotlib.pyplot as plt
from datetime import datetime
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window

class MyGridLayout(GridLayout):
    firebase_url = "firebase url here"

    def __init__(self, **kwargs):
        super(MyGridLayout, self).__init__(**kwargs)
        self.size_hint = (0.6, 0.7)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.cols = 1
        self.spacing = [0, 20]

        current_hour = datetime.now().hour
        if 6 <= current_hour < 12:
            greeting = "Good Morning"
        elif 12 <= current_hour < 18:
            greeting = "Good Evening"
        else:
            greeting = "Good Night"

        self.label1 = Label(text=f"{greeting} kelpie", font_size=28, color='#00FFCE', bold=True)
        self.add_widget(self.label1)

        self.label3 = Label(text="", font_size=38, color='#8696FE', bold=True)
        self.add_widget(self.label3)

        self.fetch_most_recent_weight()

        self.label2 = Label(text="Enter New Weight (in Kgs)", font_size=18, color='#00FFCE')
        self.add_widget(self.label2)

        self.text_input = TextInput(multiline=False)
        self.text_input.background_disabled_normal
        self.text_input.padding = [10, 10, 10, 10]
        self.add_widget(self.text_input)

        button_layout = GridLayout(cols=2, spacing=10)

        self.button = Button(text="Submit")
        self.button.padding = [10, 10, 10, 10]
        self.button.bold = True
        self.button.background_color = "#00FFCE"
        self.button.bind(on_press=self.fetch_data)
        button_layout.add_widget(self.button)

        self.button1 = Button(text="Status")
        self.button1.padding = [10, 10, 10, 10]
        self.button1.bold = True
        self.button1.background_color = "#00FFCE"
        self.button1.bind(on_press=self.fetch_status)
        button_layout.add_widget(self.button1)

        self.add_widget(button_layout)

        self.fetched_data_label = Label(text="", font_size=18, color='#00FFCE', bold=True)
        self.add_widget(self.fetched_data_label)

    

    def fetch_most_recent_weight(self):
        res = requests.get(url=self.firebase_url)
        if res.status_code == 200:
            data = res.json()
            if data:
                latest_weight = None
                latest_timestamp = datetime.min
                for entry_key, entry_value in data.items():
                    for date_key, date_value in entry_value.items():
                        if "Weight" in date_value and "CurrentTime" in date_value:
                            weight = date_value["Weight"]
                            timestamp_str = date_value["CurrentTime"]
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            if timestamp > latest_timestamp:
                                latest_timestamp = timestamp
                                latest_weight = weight

                if latest_weight is not None:
                    self.label3.text = f" {latest_weight} Kgs"
                else:
                    self.label3.text = "No weight data available."
            else:
                self.label3.text = "No data available."
        else:
            self.label3.text = "Failed to fetch data."

    def fetch_data(self, instance):
        weight = float(self.text_input.text)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_day = datetime.now().strftime("%d")
        current_entry = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        json_data = {
            current_entry: {
                "Weight": weight,
                "CurrentTime": current_time,
                "CurrentDay": current_day
            }
        }

        res = requests.post(url=self.firebase_url, json=json_data)
        if res.status_code == 200:
            self.confirmation = Label(text="Data Updated Boi!")
            self.confirmation.color = "#F6FA70"
            self.add_widget(self.confirmation)
        else:
            self.confirmation = Label(text="Something fishy man...")
            self.confirmation.color = "#F6FA70"
            self.add_widget(self.confirmation)

    # Modify the fetch_status function
    def fetch_status(self, instance):
        res = requests.get(url=self.firebase_url)
        if res.status_code == 200:
            data = res.json()
            if data:
                weights = []
                dates = []
                for entry in data.items():
                    weight = entry.get('Weight')
                    date = entry.get('CurrentTime')
                if weight and date:
                    weights.append(weight)
                    dates.append(date)

            self.create_graph(weights, dates)
            self.update_fetched_data_label(weights, dates)  # Add this line
        else:
            self.confirmation = Label(text="Failed to fetch data.")
            self.confirmation.color = "#F6FA70"
            self.add_widget(self.confirmation)

# Add a new method to update the label with fetched data
    def update_fetched_data_label(self, weights, dates):
        fetched_data = "Fetched Data:\n"
        for weight, date in zip(weights, dates):
            fetched_data += f"Weight: {weight} Kgs, Date: {date}\n"
        self.fetched_data_label.text = fetched_data



    def create_graph(self, weights, dates):
        plt.figure(figsize=(8, 6))
        plt.bar(range(len(weights)), weights, color='lightblue')
        plt.plot(range(len(weights)), weights, color='red', linewidth=2)
        plt.xlabel('Number of Days')
        plt.ylabel('Weight')
        plt.title('Weight Trend')
        plt.xticks(range(len(dates)), dates, rotation=45)
        plt.tight_layout()
        plt.show()


class MyApp(App):
    def build(self):
        Window.clearcolor = "#080202"
        return MyGridLayout()


if __name__ == '__main__':
    MyApp().run()
