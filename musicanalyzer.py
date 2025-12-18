import librosa
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QLabel, QGridLayout, QWidget, QPushButton, QComboBox, QHBoxLayout, QMessageBox
import operator

class MainWindow(QMainWindow):
    def __init__(self):

        super().__init__()
    
        wid = QWidget(self)
        self.setCentralWidget(wid)
        self.grid = QGridLayout()
        wid.setLayout(self.grid)
        self.boxgrid = QHBoxLayout()
        self.grid.addLayout(self.boxgrid, 999, 0)

        self.setMinimumSize(1024, 768)
        
        self.setStyleSheet("""
                           
        QMainWindow {
        background-color:  #2b2b2b;
        }
                                          
        QLabel{
        font-family: Roboto;
        color: white;
        font-weight: 400;
                           
        }                   
        QPushButton{
                           
        font-family: Roboto;
        font-weight: 400;
        border-radius: 8px;
        border: 1px solid white;
        padding: 5px 15px;
        margin-top: 10px;
        outline: 0px;
                           
        }

        QComboBox{               
        font-family: Roboto;
        font-weight: 400;                
        }                 
         """)
        
        self.file_directory = ""
        self.audio_file = []

        self.song_list = []
        self.bpm_list = []
        self.raw_energy_list = [] # specific list for conversion                      # empty lists that will store data
        self.energy_list = []  # list that specifies high, medium or low          

        energy_header = QLabel("Energy: ")
        song_header = QLabel("Songs: ")
        BPM_header = QLabel("BPM: ")          # labels
        sound_header = QLabel("Sound data:")
        file_chooser = QPushButton("Choose folder") 
        csv_button = QPushButton('Export to CSV')

        sort_box = QComboBox()
        sort_box.addItems(["Sort by BPM (highest to lowest)", "Sort by BPM (lowest to highest)",
                         'Sort by Energy (high to low)', 'Sort by Energy (low to high)'])
        sort_box.setFixedSize(210, 30)

        def basic_ui_load():

            self.grid.addWidget(song_header, 0, 0, Qt.AlignmentFlag.AlignTop)
            self.grid.addWidget(BPM_header, 0, 1, Qt.AlignmentFlag.AlignTop)
            self.grid.addWidget(energy_header, 0, 2, Qt.AlignmentFlag.AlignTop)           # basic ui elements
            self.boxgrid.addWidget(file_chooser)
            file_chooser.setFixedSize(110,35)
            self.grid.addWidget(sound_header, 0, 3, Qt.AlignmentFlag.AlignTop)

        basic_ui_load()

        def file_chooser_func():

            self.file_directory = QFileDialog.getExistingDirectory()
            self.audio_file = glob(self.file_directory + '/*.webm')+ glob(self.file_directory + '/*.wav') + glob(self.file_directory + '/*.flac') + glob(self.file_directory + '/*.ogg') + glob(self.file_directory + '/*.mp3')        
            load_audio_data()                                               # function that lets the user choose a folder, loads corresponding data
            widget_unload_load()                                         
            basic_ui_load()
            sorter_options(0)
            csv_button_placement()

        def load_audio_data():  

            self.song_list = []
            self.bpm_list = []
            self.raw_energy_list = []
            self.energy_list = []

            for i in self.audio_file:
                y, sr = librosa.load(i)
                tempo, beat_frames = librosa.beat.beat_track(y=y,sr=sr,units='time')        # load audio files, track beat, calculate energy, split and append
                energy_calculation = librosa.feature.rms(y=y)
                energy_conversion = np.mean(energy_calculation)
                self.raw_energy_list.append(energy_conversion)
                self.bpm_list.append(tempo[0])
                conv_string = str(i)
                stripped_string = conv_string.rsplit("\\")
                self.song_list.append(stripped_string[1])
                

            for i in self.raw_energy_list:
                if i <= 0.05:
                    self.energy_list.append('Low energy')
                elif i <= 0.15:
                    self.energy_list.append('Medium energy')               # append energy description according to energy calculation1
                else:
                    self.energy_list.append('High energy')

        
        ig_bpm = operator.itemgetter(1)

        energy_mapping = {'Low energy': 0, "Medium energy": 1, "High energy": 2}

        def sorter_options(index):
            try:

                if index == 0: # high to low bpm
                    zipped = zip(self.song_list, self.bpm_list,self.energy_list)
                    sorted_list = sorted(zipped, key=ig_bpm, reverse=True)
                    self.song_list, self.bpm_list, self.energy_list = zip(*sorted_list)
                    widget_unload_load()
                    basic_ui_load()
                    csv_button_placement()

                elif index == 1: # low high bpm
                    zipped = zip(self.song_list, self.bpm_list,self.energy_list)
                    sorted_list = sorted(zipped, key=ig_bpm)
                    self.song_list, self.bpm_list, self.energy_list = zip(*sorted_list)
                    widget_unload_load()
                    basic_ui_load()
                    csv_button_placement()

                elif index == 2: # high low energy
                    zipped = zip(self.song_list, self.bpm_list,self.energy_list)
                    sorted_list = sorted(zipped, key=lambda i: energy_mapping[i[2]], reverse=True)
                    self.song_list, self.bpm_list, self.energy_list = zip(*sorted_list)
                    widget_unload_load()
                    basic_ui_load()
                    csv_button_placement()

                else:  # low high energy
                    zipped = zip(self.song_list, self.bpm_list,self.energy_list)
                    sorted_list = sorted(zipped, key=lambda i: energy_mapping[i[2]])
                    self.song_list, self.bpm_list, self.energy_list = zip(*sorted_list)
                    widget_unload_load()
                    basic_ui_load()
                    csv_button_placement()
            except:
                error_box = QMessageBox(self)
                error_box.setWindowTitle("No songs found!")
                error_box.setText(f"Unable to find a song in {self.file_directory}")
                error_box.exec()

        sort_box.currentIndexChanged.connect(sorter_options)


        d = {'File_Name': pd.Series(self.song_list),
        'BPM': pd.Series(self.bpm_list), 'Energy': pd.Series(self.energy_list)   # basic pandas df             
        }


        def csv_button_placement():
            self.boxgrid.addWidget(csv_button)

        def export_to_csv():
            dlg = QMessageBox(self)
            dlg.setWindowTitle("CSV file created!")
            dlg.setText(f"A CSV file has been created in {self.file_directory}!")
            datalist = zip(self.song_list, self.bpm_list, self.energy_list)
            compiled_df = {'Sound data': pd.Series(datalist)}
            compiled_df['Sound data'].to_csv(self.file_directory + '/sound_data.csv', index=False)
            dlg.exec()
        
        csv_button.clicked.connect(export_to_csv)

        def load_sound_data(i):
                plt.close('all')
                y, sr = librosa.load(self.audio_file[i])
                fig, ax = plt.subplots()
                librosa.display.waveshow(y, sr=sr, ax=ax)
                ax.set(title='Amplitude over Time')                              # visualization via matplotlib
                fig.canvas.manager.set_window_title(self.song_list[i])
                plt.xlabel('Time(Seconds)')
                plt.ylabel('Amplitude')
                plt.show()

        file_chooser.clicked.connect(file_chooser_func)

        def widget_unload_load():
            for i in reversed(range(self.grid.count())):
                widget = self.grid.itemAt(i).widget()                   # unloading widgets and labels
                if widget is not None:
                    widget.setParent(None)

            self.grid.addWidget(sort_box, 0, 4, Qt.AlignmentFlag.AlignTop)

            row = 0
            for f in range(len(self.song_list)):
                songs_label = QLabel(str(self.song_list[f]))
                bpm_label   = QLabel(str(f"{self.bpm_list[f]:.2f}"))
                energy_label = QLabel(self.energy_list[f])
                sound_button = QPushButton("Show sound data")
                sound_button.clicked.connect(lambda checked, i=f: load_sound_data(i))                 # widgets, labels load
                self.grid.addWidget(sound_button, row, 3, Qt.AlignmentFlag.AlignCenter)
                self.grid.addWidget(energy_label, row, 2, Qt.AlignmentFlag.AlignCenter)
                self.grid.addWidget(songs_label, row, 0, Qt.AlignmentFlag.AlignCenter)
                self.grid.addWidget(bpm_label, row, 1, Qt.AlignmentFlag.AlignCenter)

                row += 1

app = QtWidgets.QApplication([])
win = MainWindow()                      # app initialization
win.show()
app.exec()