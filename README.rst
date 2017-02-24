
1. Setup virtualenv:
virtualenv .venv --no-site-packages -ppython2.7

2. Activate virtual environment:
. .venv/bin/activate

3. Install dependencies:
pip install -r requirements.txt

4. Install mongo

5. Run mongo in separate terminal:
mongod --dbpath=var/mongodb

6. Run tests:
nosettests src -s

7. MONGODB_URI is for custom mongo
