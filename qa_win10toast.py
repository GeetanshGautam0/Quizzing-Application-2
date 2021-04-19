from win10toast import ToastNotifier as toast
import threading
toaster = toast()

class T(threading.Thread):
    def __init__(self, tt, te, ico, d):
        self.thread = threading.Thread
        self.thread.__init__(self)
        self.start()
        
        toaster.show_toast(tt, te, icon_path = ico, duration = d)    

    def __del__(self):
        self.thread.join(self, 0)

def Toast(Title, Text, Icon = None, Duration = 5):
    if not type(Title) is str or not type(Text) is str:
        raise TypeError("Inavlid datatype")
    
    T(Title, Text, Icon, Duration)