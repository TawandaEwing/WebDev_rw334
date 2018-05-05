from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
from datetime import datetime
import os
import uuid

url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
username = os.environ.get('NEO4J_USERNAME')
password = os.environ.get('NEO4J_PASSWORD')

graph = Graph(url + '/db/data/', username=username, password=password)

class User:
    def __init__(self, username):
        self.username = username

    def find(self):
        user = graph.find_one("User", "username", self.username)
        return user

    def register(self, email, password):
        if not self.find():
            user = Node("User", username=self.username, email=email, password=bcrypt.encrypt(password))
            graph.create(user)
            return True
        else:
            return False
			
	def verify_password(self, password):
        user = self.find()
        if user:
            return bcrypt.verify(password, user['password'])
        else:
            return False
			
	def add_question(self, text, topics):
        user = self.find()
        question = Node(
            "Question",
            id=str(uuid.uuid4()),
            text=text,
            timestamp=timestamp(),
            date=date()
        )
        rel = Relationship(user, "ASKED", question)
        graph.create(rel)

        topics = [x.strip() for x in topics.lower().split(',')]
        for t in set(topics):
            topic = graph.merge_one("Topic", "name", t)
            rel = Relationship(topic, "TAGGED", question)
            graph.create(rel)