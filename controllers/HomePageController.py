from webbrowser import open

class HomePageController():
    @staticmethod
    def open_url(item):
        if item.text()[:3] == 'www':
            open(item.text())
        if item.text() == "10.1039/D2CC02238A":
            open("https://pubs.rsc.org/en/content/articlelanding/2022/CC/D2CC02238A")
