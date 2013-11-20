from flask import flash, Flask, render_template
app = Flask(__name__)
app.secret_key = 'some_secret'

@app.route('/')
def index():
	return render_template('index.html')

if __name__ == '__main__':
	app.debug = True
	app.run()