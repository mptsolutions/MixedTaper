import json
from simple_discogs import SimpleDiscogs
    
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QFileDialog, QMessageBox
from mixed_taper_ui import Ui_MainWindow
from datetime import datetime, timedelta

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.artist_list.cellClicked.connect(self.populate_release_list)
        self.artist_list.keyPressed.connect(self.refresh_artists)
        self.release_list.cellClicked.connect(self.populate_track_list)
        self.track_list.cellDoubleClicked.connect(self.populate_side_a_list)

        self.side_a_list.cellDoubleClicked.connect(self.remove_item_a)
        self.side_a_list.cellChanged.connect(lambda: self.resize_side_table(self.side_a_list))

        self.side_b_list.cellDoubleClicked.connect(self.remove_item_b)
        self.side_b_list.cellChanged.connect(lambda: self.resize_side_table(self.side_b_list))

        self.calculate_button.clicked.connect(self.calculate_sides)
        self.save_button.clicked.connect(self.save_to_file)
        self.clear_button.clicked.connect(self.clear_tracks)
        
        self.tracker = {'ARTIST':'', 'RELEASES':[], 'RELEASE':{}, 'TRACKS':[]}
        self.initialize_databases()
        self.populate_artists_list()

    def initialize_databases(self):
        with open('./simple_discogs.conf', 'r') as config_file:
            creds = json.loads(config_file.read())
        self.sd = SimpleDiscogs(creds['discogs_user_id'], creds['discogs_user_token'], user_agent='MixedTaper/1.0')

    def populate_artists_list(self):
        self.artist_list.clearSelection()
        self.artist_list.clearContents()
        self.release_list.clearSelection()
        self.release_list.clearContents()
        self.track_list.clearSelection()
        self.track_list.clearContents()
        artists = self.sd.get_unique_list('ARTIST')
        self.artist_list.setRowCount(len(artists))
        for row, artist in enumerate(artists):
            self.artist_list.setItem(row, 0, QTableWidgetItem(artist['name']))
        self.artist_list.resizeRowsToContents()
    
    def populate_release_list(self):
        self.release_list.clearSelection()
        self.release_list.clearContents()
        self.tracker = {'ARTIST':'', 'RELEASES':[], 'RELEASE':{}, 'TRACKS':[]}
        self.tracker['ARTIST'] = self.artist_list.selectedItems()[0].text()
        self.tracker['RELEASES'] = self.sd.browse('ARTIST', self.tracker['ARTIST'])
        self.release_list.setRowCount(len(self.tracker['RELEASES']))
        for row, release in enumerate(self.tracker['RELEASES']):
            self.release_list.setItem(row, 0, QTableWidgetItem('(' + str(release['YEAR']) + ') ' + release['TITLE']))
        self.release_list.resizeRowsToContents()
        self.release_list.item(0, 0).setSelected(True)
        self.populate_track_list()

    def populate_track_list(self):
        self.track_list.clearSelection()
        self.track_list.clearContents()
        row_index = self.release_list.selectionModel().selectedRows()[0].row()
        release = self.sd.get_release(self.tracker['RELEASES'][row_index]['RELEASE_ID'])
        tracks = self.sd.query_songs(discogs_release_id=release['RELEASE_ID'])
        if tracks == []:
            _ = self.sd.get_track_list(release['RELEASE_ID'])
            tracks = self.sd.query_songs(discogs_release_id=release['RELEASE_ID'])
        self.track_list.setRowCount(len(tracks))
        for row, track in enumerate(tracks):
            self.track_list.setItem(row, 0, QTableWidgetItem(track['DISCOGS_RELEASE_TRACK']))
            self.track_list.setItem(row, 1, QTableWidgetItem(track['LENGTH']))
            self.track_list.setItem(row, 2, QTableWidgetItem(track['TITLE']))
        
        self.track_list.resizeRowsToContents()
        self.track_list.resizeColumnToContents(0)
        self.track_list.resizeColumnToContents(1)
        self.tracker['RELEASE'] = release
        self.tracker['TRACKS'] = tracks
    
    def populate_side_a_list(self):
        row_index = self.track_list.selectionModel().selectedRows()[0].row()

        release_id = release = self.tracker['RELEASE']['RELEASE_ID']
        artist = self.tracker['ARTIST']
        release = self.tracker['RELEASE']['TITLE']
        position = self.tracker['TRACKS'][row_index]['DISCOGS_RELEASE_TRACK']
        title = self.tracker['TRACKS'][row_index]['TITLE']
        duration = self.tracker['TRACKS'][row_index]['LENGTH']
        self.side_a_list.setRowCount(self.side_a_list.rowCount()+1)
        new_row = self.side_a_list.rowCount()-1
        self.side_a_list.setItem(new_row, 0, QTableWidgetItem(release))
        self.side_a_list.setItem(new_row, 1, QTableWidgetItem(artist))
        self.side_a_list.setItem(new_row, 2, QTableWidgetItem(position))
        self.side_a_list.setItem(new_row, 3, QTableWidgetItem(duration))
        self.side_a_list.setItem(new_row, 4, QTableWidgetItem(title))
        
    def clear_tracks(self):
        self.side_a_list.clearSelection()
        self.side_a_list.clearContents()
        self.side_b_list.clearSelection()
        self.side_b_list.clearContents()
        
    def resize_side_table(self, table):
        table.resizeRowsToContents()
        table.resizeColumnToContents(0)
        table.resizeColumnToContents(1)
    
    def refresh_artists(self, key):
        if key == 16777268: # F5
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Refreshing the artist list from Discogs will take a little time, depending on the size of the collection.")
            msg.setWindowTitle("Artist Refresh")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)               
            response = msg.exec_()
            if response == 1024:
                self.sd.update_releases()
                self.populate_artists_list()
                msg.setText("Refresh complete!")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

    def save_to_file(self):
        filename, _ = QFileDialog.getSaveFileName(self,caption='Save Track List', directory='.',  filter='Simple Text (*.txt);;Spreadsheet (*.csv)')
        if filename is None or filename == '':
            return None
        side = 'A'
        csv_file_contents = 'SIDE,TRACK NO,TIME,TITLE,ARTIST,RELEASE\n'
        text_file_contents = ''
        for table in [self.side_a_list, self.side_b_list]:
            text_file_contents += 'SIDE ' + side + '\n'
            for row in list(range(0, table.rowCount())):
                duration = table.item(row, 3).text()
                if duration == '':
                    duration = '00:00:00'
                txt_row_list = '\t'.join([str(row+1), table.item(row, 3).text(), table.item(row, 4).text() + ' - ' + table.item(row, 1).text() + ' [' + table.item(row, 0).text() + ']'])
                csv_row_list = ','.join([side, str(row+1), table.item(row, 3).text(), '"'+table.item(row, 4).text()+'"', '"'+table.item(row, 1).text()+'"', '"'+table.item(row, 0).text()+'"'])
                text_file_contents += '\t' + txt_row_list + '\n'
                csv_file_contents += csv_row_list + '\n'
            side = 'B'
        with open(filename, 'w', encoding='utf-8') as out_file:
            if filename.endswith('csv'):
                out_file.write(csv_file_contents)
            else:
                out_file.write(text_file_contents)

    def calculate_sides(self):       
        side_stats = [{'side':'A', 'table':self.side_a_list, 'tracks':[]}, {'side':'B', 'table':self.side_b_list, 'tracks':[]}]
        for entry in side_stats:
            for row in list(range(0, entry['table'].rowCount())):
                entry['tracks'].append({'artist':entry['table'].item(row, 1).text(), 'release':entry['table'].item(row, 0).text(), 
                                        'orig_position':entry['table'].item(row, 2).text(), 'duration':entry['table'].item(row, 3).text(), 
                                        'title':entry['table'].item(row, 4).text(), 'new_position':row+1})
            total_time = timedelta(hours=0, minutes=0, seconds=0)
            for track in entry['tracks']:
                if track['duration'].count(':') == 2:
                    hrs, mts, sec = track['duration'].split(':')
                elif track['duration'].count(':') == 1:
                    mts, sec = track['duration'].split(':')
                    hrs = 0
                else:
                    hrs = 0
                    mts = 0
                    sec = 0
                total_time += timedelta(hours=int(hrs), minutes=int(mts), seconds=int(sec))
            total_time = str(total_time)
            if len(total_time.split(':')[0]) == 1:
                total_time = '0' + total_time
            entry['total_time'] = str(total_time)
            entry['track_count'] = len(entry['tracks'])
        self.side_a_time_box.setText(side_stats[0]['total_time'])
        self.side_b_time_box.setText(side_stats[1]['total_time'])
            
    def remove_item_a(self):
        index = self.side_a_list.selectionModel().selectedRows()[0].row()
        self.side_a_list.removeRow(index)

    def remove_item_b(self):
        index = self.side_b_list.selectionModel().selectedRows()[0].row()
        self.side_b_list.removeRow(index)
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
