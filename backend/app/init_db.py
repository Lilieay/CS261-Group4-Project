from app.db import Base, engine
from app.models.user import User
from app.models.course import Course
from app.models.guide import Guide

def main():
    Base.metadata.create_all(bind=engine)
    

if __name__ == "__main__":
    main()
