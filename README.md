# Travelux Backend app with FastAPI and PostgreSQL

An app similar to Airbnb, designed for users to explore rental properties or list their own. 

It incorporates collections for Users, Properties, and Ratings. JWT tokens are employed for authentication. 

The application is containerized using Docker and deployed on the Cloud. 

It's configured to interact with the corresponding React JS frontend, available at https://github.com/MartinKraychev/TraveLux.

## To test locally

Clone the project

```bash
  git clone https://github.com/MartinKraychev/TraveLux-Backend.git
```

Go to the project directory

```bash
  cd travelux-backend
```
Install Virtual env - for Windows
```bash
  pip install virtualenv
  python -m venv venv
  venv/Scripts/activate
```

```bash
  pip install -r requirements.txt
```

You need to have postgresql instance and .env file with the following variables: DB_USER, DB_PASSSWORD, DB_SERVER, DB_NAME

Start the server

```bash
  uvicorn main:app --reload
```

## API Reference
 The main URL for this is https://travelux-ooow2st62q-nw.a.run.app if used directly or http://localhost:8000 if tested locally.
 
 Alternative to the explanation below is the FastApi swagger for this app
https://travelux-ooow2st62q-nw.a.run.app/docs
#### Auth

##### Register

```http
  POST URL/auth/register
```
With body {email, password, phone_number}


##### Login

```http
  POST URL/auth/login
```
With body {email, password}


##### Logout

```http
  POST URL/auth/logout
```
With no body

#### Property

#### Get all properties

```http
  GET URL/properties
```

##### Create property

```http
  POST URL/properties
```
With body {title, type, image_url, price_per_night, address, summary, location}

##### Get my properties

```http
  GET URL/properties/my-properties
```

##### Get random property photos

```http
  GET URL/properties/photos
```

##### Get property by id

```http
  GET URL/properties/{id}
```

##### Edit property by id

```http
  PUT URL/properties/{id}
```

##### Delete property by id

```http
  DELETE URL/properties/{id}
```

#### Ratings

##### Can rate?

```http
  POST URL/rating/check-rating
```
With body {property_id}

##### Rate property

```http
  POST URL/rating/{roperty_id}
```
With body {vote}
