from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(port=5000, debug=True)  # Removed allow_unsafe_werkzeug as it's not needed here
