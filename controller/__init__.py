import os 
import glob
import os
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))  # Retrieve from environment variable or fallback to random key
#postgresql://techtrendz_user:v1RuGVslYbUOHPJ352yA49EqgSmZ2yNB@dpg-d031au3uibrs73bb22b0-a.oregon-postgres.render.com/techtrendz

__all__=[os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py")]