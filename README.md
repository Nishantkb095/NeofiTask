# Note-Taking API

This is a RESTful API for a simple note-taking application. The API allows users to perform basic CRUD operations (Create, Read, Update, Delete) on notes.

## Features

- User registration and login
- Creating, retrieving, updating, and deleting notes
- Sharing notes with other users
- Retrieving the version history of a note

## Setup

1. Install Django and Django REST framework:

```bash
pip install django djangorestframework
```

2. Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/yourusername/notesapi.git
cd notesapi
```

3. Install the requirements

```bash
pip install -r requirements.txt
```

4. Run migrations to create the database tables:

```bash
python manage.py makemigrations notes
python manage.py migrate
```

5. Run the server:

```bash
python manage.py runserver
```

The API will be available at [http://localhost:8000/api/](http://localhost:8000/api/).

## Endpoints

- `POST /signup/`: Register a new user.
- `POST /login/`: Log in a user.
- `POST /notes/create/`: Create a new note.
- `GET /notes/:id`: Retrieve a note.
- `POST /notes/:id/share/`: Share a note with other users.
- `PUT /notes/:id/update/`: Update a note.
- `GET /notes/version-history/:id/`: Retrieve the version history of a note.

## Testing

You can use tools like Postman or cURL to test the API endpoints. Make sure to include the authentication token in the `Authorization` header of your requests (`Authorization: Token <your_token>`).

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Swagger

You can access the Swagger at localhost:8000/swagger
For authorization add the token in swagger as
Token <your_token>
