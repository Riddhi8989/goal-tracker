from peewee import *
import datetime

# Database initialization
db = SqliteDatabase('database.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    email = CharField(unique=True, null=True)
    created_date = DateTimeField(default=datetime.datetime.now)

    def __repr__(self):
        return f'<User {self.username}>'

class StudyGoal(BaseModel):
    user = ForeignKeyField(User, backref='goals')
    title = CharField()
    description = TextField(null=True)
    target_date = DateField()
    created_date = DateTimeField(default=datetime.datetime.now)
    completed = BooleanField(default=False)

    def __repr__(self):
        return f'<StudyGoal {self.title} by {self.user.username}>'

# Helper to initialize DB
def create_tables():
    with db:
        db.create_tables([User, StudyGoal])
