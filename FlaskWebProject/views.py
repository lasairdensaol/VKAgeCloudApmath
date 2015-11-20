"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from FlaskWebProject import app

@app.route('/', methods = ['GET', 'POST'])
def index():
	###results = {}
	###errors = []
	###if request.method == 'POST':
		###try:
			###user_id = request.form['id']
			###mynum = np.random.randint(100)
			###errors.append(str(mynum))
			###if user_id:
			###	errors.append("Mi")
			###	age = find_age.find_user_age(int(user_id))
			###	results  = [('Method 1', age[0]),
			###				('Method 2', age[1]),
			###				('Method 3', age[2]),
			###				('Method 4', age[3]),
			###				('Method 5', age[4])]
			###	return render_template('index.html', errors = errors, user_id = user_id, results = results)
			###else:
			###	errors.append("The form should not be empty")
			###	return render_template('index.html', errors = errors)
		###except:
			###errors.append("Wrong id or no access the Internet. Please make sure it is right and try again")
			###return render_template('index.html', errors = errors)

	return render_template('index.html')
