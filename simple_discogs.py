import requests
import pathlib
import sqlite3
from os import path
from sqlite3.dbapi2 import DatabaseError

class SimpleDiscogs:
    def __init__(self, discogs_user_id, discogs_user_token, user_agent='SimpleDiscogs/0.1', database_location=None):
        self.discogs_user_id = discogs_user_id
        self.discogs_user_token = discogs_user_token
        self.discogs_headers = {'User-Agent': user_agent}
        self.user_releases_url = 'https://api.discogs.com/users/' + self.discogs_user_id 
        self.user_releases_url += '/collection/folders/0/releases?token=' + self.discogs_user_token
        self.release_fields = ['RELEASE_ID', 'FOLDER_ID', 'CATALOG_ID', 'ARTISTS_ID', 'DATE_ADDED', 'YEAR', 'DECADE', 'ARTIST',
                               'TITLE', 'LABEL', 'FORMAT', 'GENRE', 'STYLE', 'RELEASE_URL', 'MASTER_URL', 'THUMB_URL', 'COVER_URL']
        self.song_fields = ['SONG_ID', 'TITLE', 'RELEASE', 'ARTIST', 'LENGTH', 'DISCOGS_RELEASE_ID', 'DISCOGS_RELEASE_TRACK']
        if database_location:
            self.database_file = path.join(database_location, 'simple_discogs.sqlite')
        else:
            self.database_file = './simple_discogs.sqlite'
        if not pathlib.Path(self.database_file).is_file():
            self.update_releases()

    def clean_time(self, time_value):
        sections = time_value.split(':')
        if len(sections[0]) == 1:
            sections[0] = '0' + sections[0]
        if len(sections) == 2:
            sections = ['00'] + sections
        return ':'.join(sections)
        
    def connect_to_database(self):
        try:
            conn = sqlite3.connect(self.database_file)
        except:
            raise DatabaseError
        return conn, conn.cursor()

    def get_releases_from_discogs(self):
        response = requests.get(self.user_releases_url + '&per_page=100', headers=self.discogs_headers)
        pagination = response.json()['pagination']
        releases = response.json()['releases']

        if pagination['items'] > 100:
            for page in range(2, pagination['pages'] + 1):
                response = requests.get(self.user_releases_url + '&per_page=100&page=' + str(page), headers=self.discogs_headers)
                releases += response.json()['releases']

        for release in releases:
            if release['basic_information']['year'] == 0:
                master_url = 'https://api.discogs.com/masters/' + str(release['basic_information']['master_id'])
                master_url += '?per_page=100&token=' + self.discogs_user_token
                response = requests.get(master_url, headers=self.discogs_headers)

                if 'year' in response.json():
                    release['basic_information']['year'] = response.json()['year']
        return releases

    def update_releases(self):
        releases = self.get_releases_from_discogs()
        conn, cursor = self.connect_to_database()
        if conn and cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            table_list = [row[0] for row in cursor.fetchall()]

            if 'RELEASES' in table_list:
                cursor.execute('DROP TABLE RELEASES')
                conn.commit()

            sql_statement = 'CREATE TABLE RELEASES (' + ','.join(self.release_fields) + ')'
            sql_statement = sql_statement.replace('RELEASE_ID', 'RELEASE_ID INTEGER PRIMARY KEY')
            sql_statement = sql_statement.replace('DATE_ADDED', 'DATE_ADDED DATETIME')
            cursor.execute(sql_statement)
            conn.commit()

            if 'SONGS' not in table_list:
                sql_statement = f'CREATE TABLE SONGS ({",".join(self.song_fields)})'
                sql_statement = sql_statement.replace('SONG_ID', 'SONG_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL')
                sql_statement = sql_statement.replace('DISCOGS_RELEASE_ID', 'DISCOGS_RELEASE_ID INTEGER')
                cursor.execute(sql_statement)
                conn.commit()

            for release in releases:
                clean_release = {}
                clean_release['year'] = release['basic_information']['year']
                clean_release['decade'] = int(str(clean_release['year'])[:-1]+'0')
                clean_release['master_url'] = release['basic_information']['master_url']
                clean_release['id'] = release['basic_information']['id']
                clean_release['thumb'] = release['basic_information']['thumb']
                clean_release['title'] = release['basic_information']['title']
                clean_release['cover_image'] = release['basic_information']['cover_image']
                clean_release['resource_url'] = release['basic_information']['resource_url']
                clean_release['folder_id'] = release['folder_id']
                clean_release['date_added'] = release['date_added']

                catalog_numbers = []
                label_names = []
                for label in release['basic_information']['labels']:
                    catalog_numbers.append(label['catno'])
                    label_names.append(label['name'])
                clean_release['catalog'] = '|'.join(list(set(catalog_numbers)))
                clean_release['labels'] = '|'.join(list(set(label_names)))

                artists = []
                artists_ids = []
                for artist in release['basic_information']['artists']:
                    artists.append(artist['name'])
                    artists_ids.append(str(artist['id']))
                clean_release['artists'] = '|'.join(list(set(artists)))
                clean_release['artists_ids'] = '|'.join(artists_ids)

                clean_release['genres'] = '|'.join([genre for genre in release['basic_information']['genres']])
                clean_release['styles'] = '|'.join([style for style in release['basic_information']['styles']])

                formats = []
                for release_format in release['basic_information']['formats']:
                    formats.append(release_format['name'])
                    if 'descriptions' in release_format:
                        for description in release_format['descriptions']:
                            formats.append(description)
                clean_release['formats'] = '|'.join(list(set(formats)))

                for key, value in clean_release.items():
                    if value == None:
                        clean_release[key] = ''
                    elif type(value) == str:
                        clean_release[key] = clean_release[key].replace('"', "''")

                cursor = conn.cursor()
                sql_statement = 'INSERT INTO RELEASES (' + ','.join(self.release_fields) +') VALUES (' + ','.join('?' * 17) + ')'

                sql_values = (clean_release['id'], clean_release['folder_id'], clean_release['catalog'],
                    clean_release['artists_ids'], clean_release['date_added'][:19].replace('T', ' '), clean_release['year'], 
                    clean_release['decade'], clean_release['artists'], clean_release['title'], 
                    clean_release['labels'], clean_release['formats'].lower(), clean_release['genres'].lower(), 
                    clean_release['styles'].lower(), clean_release['resource_url'], clean_release['master_url'], 
                    clean_release['thumb'], clean_release['cover_image'])

                cursor.execute(sql_statement, sql_values)
            conn.commit()
            conn.close()
            return len(releases)
        return 0

    def get_release(self, release_id):
        conn, cursor = self.connect_to_database()
        if conn and cursor:
            select_statement = 'SELECT ' + ','.join(self.release_fields) + ' FROM RELEASES WHERE RELEASE_ID=?'
            cursor.execute(select_statement, (release_id,))
            result_list = [{[name for name in self.release_fields][index]:element for index, element in enumerate(row)} for row in cursor.fetchall()][0]
            conn.close()
            return result_list
        return None

    def browse(self, category, selection=None):
        conn, cursor = self.connect_to_database()
        if conn and cursor:
            if category == 'RANDOM' and selection is not None:
                select_statement = 'SELECT ' + ','.join(self.release_fields) + ' FROM RELEASES ORDER BY RANDOM() LIMIT ?'
                cursor.execute(select_statement, (selection, ))
            elif category == 'all':
                select_statement = 'SELECT ' + ','.join(self.release_fields) + ' FROM RELEASES '
                select_statement += 'ORDER BY ARTIST COLLATE NOCASE ASC, DECADE ASC, TITLE COLLATE NOCASE ASC'
                cursor.execute(select_statement)
            elif category and selection:
                select_statement = 'SELECT ' + ','.join(self.release_fields) + ' FROM RELEASES WHERE '
                select_statement += category.upper() + ' LIKE ? OR '
                select_statement += category.upper() + ' LIKE ? OR '
                select_statement += category.upper() + ' LIKE ? OR '
                select_statement += category.upper() + ' LIKE ? '
                select_statement += 'COLLATE NOCASE ORDER BY ARTIST ASC, DECADE ASC, TITLE ASC'
                cursor.execute(select_statement, (selection, selection + '|%', '%|' + selection + '|%', '%|' + selection))
            else:
                conn.close()
                return []
            result_list = [{[name for name in self.release_fields][index]:element for index, element in enumerate(row)} for row in cursor.fetchall()]
            conn.close()
            return result_list
        return []

    def get_available_categories(self):
        conn, cursor = self.connect_to_database()
        if conn and cursor:
            cursor.execute("SELECT sql FROM sqlite_master WHERE tbl_name = 'RELEASES' AND type = 'table'")
            entry_list = []
            for row in cursor.fetchall():
                entry_list += row[0].split('(')[1].split(')')[0].split(',')
            conn.close()
            entry_list = [entry for entry in entry_list if 'ID' not in entry and 'URL' not in entry and 'DATE' not in entry]
            entry_list = [{'name':entry, 'count':len(self.get_unique_list(entry))} for entry in entry_list]
            artist_count = [entry['count'] for entry in entry_list if entry['name'] == 'ARTIST'][0]
            entry_list.append({'name':'RANDOM', 'count':artist_count})
            entry_list = sorted(entry_list, key=lambda k: k['name'].upper())
            return entry_list
        return []

    def get_unique_list(self, category):
        conn, cursor = self.connect_to_database()
        if conn and cursor:
            cursor.execute("SELECT " + category + " FROM RELEASES")
            entry_list = []
            for row in cursor.fetchall():
                if type(row[0]) == str:
                    for entry in row[0].split('|'):
                        entry_list.append(entry)
                elif type(row[0]) == int:
                    if row[0] == 0:
                        entry = 'unknown'
                    else:
                        entry = str(row[0])
                    entry_list.append(entry)
            conn.close()
            entry_counts = list(set([(entry, entry_list.count(entry)) for entry in entry_list]))
            entry_list = [{'name':entry, 'count':total} for entry, total in entry_counts]
            entry_list = sorted(entry_list, key=lambda k: k['name'].upper())
            return entry_list
        return []

    def get_video_list(self, release_id):
        release_url = 'https://api.discogs.com/releases/' + str(release_id)
        release_url += '?per_page=100&token=' + self.discogs_user_token
        response = requests.get(release_url, headers=self.discogs_headers)
        if 'videos' in response.json() and response.json()['videos']:
            video_list = response.json()['videos']
        else:
            video_list = []
        return video_list

    def get_track_list(self, release_id):
        release_url = 'https://api.discogs.com/releases/' + str(release_id)
        release_url += '?per_page=100&token=' + self.discogs_user_token
        response = requests.get(release_url, headers=self.discogs_headers)
        if response.json()['tracklist']:
            tracklist = response.json()['tracklist']
        else:
            tracklist = []
        return tracklist
    
    def insert_song(self, title, release, artist, length, discogs_release_id, discogs_release_track):
        conn, curs = self.connect_to_database()
        sql_statement = f'INSERT INTO SONGS ({",".join(self.song_fields)}) VALUES ({",".join("?" * len(self.song_fields))})'
        sql_values = (None, title, release, artist, self.clean_time(length), discogs_release_id, discogs_release_track)
        curs.execute(sql_statement, sql_values)
        conn.commit()
        conn.close()
        return True
    
    def remove_song(self, song_id):
        conn, curs = self.connect_to_database()
        sql_statement = f'DELETE FROM SONGS WHERE SONG_ID = {song_id}'
        curs.execute(sql_statement)
        conn.commit()
        conn.close()
        return True

    def get_songs(self):
        conn, curs = self.connect_to_database()
        sql_statement = f'SELECT {",".join(self.song_fields)} FROM SONGS'
        curs.execute(sql_statement)
        songs = [{[name for name in self.song_fields][index]:element for index, element in enumerate(row)} for row in curs.fetchall()]
        conn.close()
        return songs

    def query_songs(self, song_id=None, title=None, release=None, artist=None, 
                    max_length=None, min_length=None, discogs_release_id=None, discogs_release_track=None):
        conn, curs = self.connect_to_database()
        sql_statement = f'SELECT {",".join(self.song_fields)} FROM SONGS WHERE '
        criteria_list = []
        for criteria in [(title, 'TITLE'), (release, 'RELEASE'), (artist, 'ARTIST')]:
            if criteria[0]:
                criteria_list.append(f'{criteria[1]} LIKE "%{criteria[0]}%" ')
        if max_length:
            criteria_list.append(f'LENGTH <= "{self.clean_time(max_length)}" ')
        if min_length:
            criteria_list.append(f'LENGTH >= "{self.clean_time(min_length)}" ')
        if song_id:
            criteria_list.append(f'SONG_ID = {song_id} ')
        if discogs_release_id:
            criteria_list.append(f'DISCOGS_RELEASE_ID = {discogs_release_id} ')
        if discogs_release_track:
            criteria_list.append(f'DISCOGS_RELEASE_ID = {discogs_release_track} ')
        sql_statement += 'AND '.join(criteria_list)
        curs.execute(sql_statement)
        try:
            songs = [{[name for name in self.song_fields][index]:element for index, element in enumerate(row)} for row in curs.fetchall()]
        except:
            songs = []
        conn.close()
        return songs
