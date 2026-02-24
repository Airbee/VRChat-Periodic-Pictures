import customtkinter as ctk
import threading
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

root = ctk.CTk()
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

root.geometry("250x250")
root.title('Periodic Picture')

# Variables
threadRun = threading.Event()
threadEvent = threading.Event()
auto = ctk.BooleanVar(value=False)
seconds = 60
countdown = 0



# --------------------------
# OSC Settings
# --------------------------
OSC_IP = "127.0.0.1"
OSC_PORT = 9000
OSC_PORT_RECEIVE = 9001
client = SimpleUDPClient(OSC_IP, OSC_PORT)

def osc_callback(address, *args):
    if address == "/dolly/Play" and args and args[0] == 1:
        print("Dolly plays!")
    # print(f"Received OSC message: {address} with arguments: {args}")

 
def start_osc_server():
    dispatcher = Dispatcher()
    dispatcher.map("/*", osc_callback)
    server = osc_server.ThreadingOSCUDPServer((OSC_IP, OSC_PORT_RECEIVE), dispatcher)
    server.serve_forever()

def start_osc_server_thread():
    threading.Thread(target=start_osc_server, daemon=True).start()


def autoloop():
    global seconds
    global countdown
    print("Thread is now running")

    # Loop as long as AutoSwitch is on
    while threadRun.is_set():
        countdown = int(seconds)

        # Loop the Countdown
        while countdown >=0:
            label_countdown.configure(text=f"Next picture in: {countdown} seconds.")
            countdown = countdown-1
            threadEvent.wait(timeout=1)

            # Check if AutoSwitch got turned off
            if not threadRun.is_set():
                threadEvent.clear()
                break

        if threadRun.is_set():
            takePic()
        else:
            label_countdown.configure(text=f"Auto Pic Disabled")

    print("Thread will stop now.")
  

def startloop():
    if checkbox_auto.get():
        threadRun.set()
        threading.Thread(target=autoloop, daemon=True).start()
        
    else:
        threadRun.clear()
        threadEvent.set()
  

def setsec():
    global seconds
    global countdown
    seconds = textbox_seconds.get("0.0", "end")
    checkbox_auto.configure(text=f"Auto Pic every {int(seconds)} seconds")
    # threadEvent.set()


def takePic():
        print("Taking a picture!")
        client.send_message("/usercamera/Capture", True)




# --------------------------
# UI
# --------------------------



# Switch
frame_switch = ctk.CTkFrame(master=root)
frame_switch.pack(pady=5, padx=5, expand=True)

button_takePic = ctk.CTkButton(master=frame_switch, text="Take Picture", command=takePic)
button_takePic.grid(row=0, column=0, pady=12,padx=10, columnspan=2)


checkbox_auto = ctk.CTkCheckBox(master=frame_switch, width=100, text=f"Auto Pic every {int(seconds)} seconds", variable=auto, onvalue=True, offvalue=False, command=startloop)
checkbox_auto.grid(row=6, column=0, pady=12,padx=10, columnspan=2)

textbox_seconds = ctk.CTkTextbox(master=frame_switch, activate_scrollbars=False, height=20, width=70)
textbox_seconds.grid(row=7, column=0, pady=12,padx=10, sticky="e")

button_setsec = ctk.CTkButton(master=frame_switch, text="Set", command=setsec, width=70)
button_setsec.grid(row=7, column=1, pady=12,padx=10, sticky="w")

label_countdown = ctk.CTkLabel(master=frame_switch, text="Auto Pic Disabled")
label_countdown.grid(row=9, column=0, pady=2,padx=2, columnspan=2)


if __name__ == "__main__":
    start_osc_server_thread()
    root.mainloop()
