# Importieren der benötigten Module
import cv2  # Für die Videobearbeitung
import tkinter as tk  # Für die GUI-Erstellung
from tkinter import filedialog  # Für Dateiauswahldialoge
from PIL import Image, ImageTk  # Für die Bildbearbeitung und Anzeige in Tkinter

# Erstellen der Klasse für die Video-Overlay-Anwendung
class VideoOverlayApp:
    def __init__(self, window):
        # Initialisierung der Anwendung mit dem Hauptfenster
        self.window = window
        self.window.title("Video Overlay")  # Titel des Hauptfensters
        self.window.geometry("800x600")  # Größe des Hauptfensters

        # Initialisierung der Variablen für die Videos und den Writer
        self.video1 = None
        self.video2 = None
        self.writer = None

        # Erstellen der Widgets für die Benutzeroberfläche
        self.create_widgets()

    def create_widgets(self):
        # Erstellen und Anordnen der Widgets im Hauptfenster
        self.video1_label = tk.Label(self.window, text="Kein Video 1 ausgewählt")
        self.video1_label.pack()

        # Button zum Auswählen von Video 1
        self.video1_button = tk.Button(self.window, text="Video 1 auswählen", command=self.select_video1)
        self.video1_button.pack()

        self.video2_label = tk.Label(self.window, text="Kein Video 2 ausgewählt")
        self.video2_label.pack()

        # Button zum Auswählen von Video 2
        self.video2_button = tk.Button(self.window, text="Video 2 auswählen", command=self.select_video2)
        self.video2_button.pack()

        self.overlay_label = tk.Label(self.window, text="Wähle einen Overlay aus:")
        self.overlay_label.pack()

        # Dropdown-Menü für die Auswahl des Overlays
        self.overlay_var = tk.StringVar(self.window)
        self.overlay_var.set("Addition")  # Standardwert setzen
        self.overlay_menu = tk.OptionMenu(
            self.window, self.overlay_var, "Addition", "Subtraktion", "Multiplikation", "Division", "AND", "OR", "XOR"
        )
        self.overlay_menu.pack()

        # Button zum Anwenden des Overlays
        self.apply_button = tk.Button(self.window, text="Overlay anwenden", command=self.apply_overlay)
        self.apply_button.pack()

        # Button zum Speichern des Videos
        self.save_button = tk.Button(self.window, text="Video speichern", command=self.save_video, state=tk.DISABLED)
        self.save_button.pack()

    def select_video1(self):
        # Funktion zum Auswählen von Video 1
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi")])
        if file_path:
            self.video1 = cv2.VideoCapture(file_path)
            self.video1_label.config(text=file_path.split("/")[-1])
            if self.video2:  # Wenn beide Videos ausgewählt sind, Button aktivieren
                self.apply_button.config(state=tk.NORMAL)

    def select_video2(self):
        # Funktion zum Auswählen von Video 2
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi")])
        if file_path:
            self.video2 = cv2.VideoCapture(file_path)
            self.video2_label.config(text=file_path.split("/")[-1])
            if self.video1:  # Wenn beide Videos ausgewählt sind, Button aktivieren
                self.apply_button.config(state=tk.NORMAL)




    def apply_overlay(self):
        # Funktion zum Anwenden des Overlays auf die aktuellen Frames der Videos
        ret1, frame1 = self.video1.read()
        ret2, frame2 = self.video2.read()
        if ret1 and ret2:
            # Frames auf gleiche Größe bringen
            height, width, _ = frame1.shape
            frame2 = cv2.resize(frame2, (width, height))
            # Gewähltes Overlay anwenden
            overlay_name = self.overlay_var.get()
            frame = self.apply_selected_overlay(frame1, frame2, overlay_name)
            # Vorschau des Overlays anzeigen
            self.show_preview(frame)
            self.save_button.config(state=tk.NORMAL)  # Speichern-Button aktivieren
        else:
            # Videos beenden, wenn das Ende erreicht ist
            self.release_resources()

    def apply_selected_overlay(self, frame1, frame2, overlay_name):
        # Funktion zum Anwenden des ausgewählten Overlays
        if overlay_name == "Addition":
            return cv2.add(frame1, frame2)
        elif overlay_name == "Subtraktion":
            return cv2.subtract(frame1, frame2)
        elif overlay_name == "Multiplikation":
            return cv2.multiply(frame1, frame2)
        elif overlay_name == "Division":
            return cv2.divide(frame1, frame2)
        elif overlay_name == "AND":
            return cv2.bitwise_and(frame1, frame2)
        elif overlay_name == "OR":
            return cv2.bitwise_or(frame1, frame2)
        elif overlay_name == "XOR":
            return cv2.bitwise_xor(frame1, frame2)

    def show_preview(self, frame):
        # Funktion zum Anzeigen einer Vorschau des Overlays
        if not self.preview_window:
            self.preview_window = tk.Toplevel(self.window)
            self.preview_window.title("Vorschau")
        self.preview_label = tk.Label(self.preview_window)
        self.preview_label.pack()
        image = Image.fromarray(frame)  # Frame in ein PIL-Image konvertieren
        photo = ImageTk.PhotoImage(image)  # PIL-Image in ein PhotoImage konvertieren
        self.preview_label.config(image=photo)  # Bild im Label anzeigen
        self.preview_label.image = photo  # Referenz auf das Bild halten

    def save_video(self):
        # Funktion zum Speichern des Videos mit dem Overlay
        save_path = filedialog.asksaveasfilename(filetypes=[("Video files", "*.mp4;*.avi")])
        if save_path:
            fps = self.video1.get(cv2.CAP_PROP_FPS)
            width = int(self.video1.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.video1.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
            self.apply_button.config(state=tk.DISABLED)  # Buttons deaktivieren
            self.save_button.config(state=tk.DISABLED)
            self.preview_window.destroy()  # Vorschau-Fenster schließen
            self.save_frame()  # Speicherfunktion aufrufen

    def save_frame(self):
        # Funktion zum Speichern eines Frames im Video
        ret1, frame1 = self.video1.read()
        ret2, frame2 = self.video2.read()
        if ret1 and ret2:
            height, width, _ = frame1.shape
            frame2 = cv2.resize(frame2, (width, height))
            overlay_name = self.overlay_var.get()
            frame = self.apply_selected_overlay(frame1, frame2, overlay_name)
            self.writer.write(frame)  # Frame ins Video schreiben
            self.window.after(10, self.save_frame)  # Funktion erneut aufrufen
        else:
            self.release_resources()  # Ressourcen freigeben

    def release_resources(self):
        # Funktion zum Freigeben von Ressourcen
        if self.video1:
            self.video1.release()
        if self.video2:
            self.video2.release()
        if self.writer:
            self.writer.release()
        self.overlay_label.config(text="Video gespeichert")
    def show_preview(self, frame):
        # Überprüfen, ob das Vorschau-Fenster bereits existiert
        if not hasattr(self, 'preview_window'):
            # Wenn nicht, erstelle ein neues Toplevel-Fenster für die Vorschau
            self.preview_window = tk.Toplevel(self.window)
            self.preview_window.title("Vorschau")
    
        # Überprüfen, ob das Label für die Vorschau bereits existiert
        if not hasattr(self, 'preview_label'):
            # Wenn nicht, erstelle ein neues Label im Vorschau-Fenster
            self.preview_label = tk.Label(self.preview_window)
            self.preview_label.pack()
    
        # Konvertieren des Frames in ein PIL-Image und dann in ein Tkinter-kompatibles PhotoImage
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image)
    
        # Aktualisiere das Bild im Vorschau-Label
        self.preview_label.config(image=photo)
        self.preview_label.image = photo  # Referenz auf das Bild halten

# Hauptanwendung starten
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoOverlayApp(root)
    root.mainloop()
