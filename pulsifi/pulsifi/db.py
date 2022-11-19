import sqlite3
from dataclasses import dataclass
from typing import *
import urllib
import __init__

@dataclass
class User:
    id = str;
    username = str;
    bio = str;
    profile_pic = str;
    password_salt = str;
    password_hash = str;

    def dictionary(self) -> Dict:
        result = {}
        result["ID"] = self.id
        result["username"] = self.username
        result["bio"] = self.bio
        result["profile_pic"] = self.profile_pic
        result["password_salt"] = self.password_salt
        result["password_hash"] = self.password_hash

        return result




class db:
    conn: sqlite3.Connection

    def __init__(self, filename: str):
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self._setup()

    def _setup(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Users
            ([ID] STRING PRIMARY KEY, [username] TEXT, [bio] TEXT, [profile_pic] TEXT, [password_salt] TEXT, [password_hash] TEXT)
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Posts
            ([ID] STRING PRIMARY KEY, [message] TEXT, [likes] INTEGER, [dislikes] INTEGER)
            """
        )
        self.conn.commit()
        cursor.close()

        def getUser(self, ID):
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE ID = ?", ID)

            result = cursor.fetchall()
            cursor.close()
            
            user = User(result[0], result[1], result[2], result[3], result[4], result[5])
            return user

        def addUser(self, user):
            userArray = [user.id, user.username, user.bio, user.profile_pic, user.password_salt, user.password_hash]

            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO Posts (ID, username, bio, profile_pic, password_salt, password_hash) VALUES (?, ?, ?, ?, ?, ?);",
             userArray)
            
            self.conn.commit()
            cursor.close()

        def updateUser(self, user):
            userArray = [user.id, user.username, user.bio, user.profile_pic, user.password_salt, user.password_hash]

            cursor = self.conn.cursor()
            cursor.execute("UPDATE Users SET ID = ?,  username = ?, bio = ?, profile_pic = ?, password_salt = ?, password_hash = ?", userArray)

            self.conn.commit()
            cursor.close()

        def deleteUser(self, id):
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM Users WHERE ID = ?", id)

            self.conn.commit()
            cursor.close()