## ID Checker for Tc id cards

A simple flask server that has two routes;
    -/Idchecker : Take as input an image and return if it is a TC id and front or back picture.
    -/imageReader : Take an image as input and return from the front of the id; Tc, name, surname, dob and serie no.

Run flask server with flask run or gunicorn -w 4 -b 0.0.0.0:5000 app:app with 4 workers.