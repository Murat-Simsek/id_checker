import requests


def send_image(filename):
    url = 'http://localhost:5000/Idchecker'
    url = 'http://localhost:5000/imageReader'

    # Read the image file
    with open(filename, 'rb') as file:
        # Create the payload with the file data
        payload = {'file': file}

        # Send the POST request to the server
        response = requests.post(url, files=payload)

        # Print the response from the server
        print(response.text)


# Specify the path to the image file
image_filename = 'test1.jpg'

# Call the function to send the image
send_image(image_filename)
