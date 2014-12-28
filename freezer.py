from flask_frozen import Freezer
from w35found import app

freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()