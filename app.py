from main import create_app # Import flask app from main folder

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)