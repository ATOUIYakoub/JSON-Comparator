# How to Set Up This Project

## Create Your Local Virtual Environment

There are two ways of doing this, depending on your way of Python installation. This is going to cover the way of **Pip** Distribution users.
Here are the steps to start:

### Backend Side:

1. **Verify in your CMD (PowerShell) if you have `pip` installed:**

```
C:\Users\DELL>pip
```

You should get the list of commands you can use with `pip`. If you didn't get the desired result, you should check if **Pip** is added to `PATH` environment variables.

2. **Clone the project on your local machine:**

```
git clone https://github.com/ATOUIYakoub/JSON-Comparator.git
```

3. Create your local virtual environment:
```
python -m venv env
#if error try:
python -m pip install virtualenv
```
we are using python 3.11.5 version for this project, you can name the virtual environment as you please `venv` is just an example.

4. Activate your virtual environment:
```
.\env\Scripts\activate
```

5. Install the Backend Dependencies:
```
cd json_comparator
pip install -r requirements.txt
```

6. Test if your backend is running correctly:
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
7.Configure Environment Variables

1. **Create a `.env` file in the root directory of your project.**

   In the root directory of your project, create a file named `.env`.

2. **Add the necessary environment variables, such as `API_KEY`, and other configurations.**

   Example content for `.env` file:
   ```env
   API_KEY=your_api_key_here
   ```
## Test JSON Comparison in Postman

To test the JSON comparison functionality in Postman using files, follow these steps:

1. **Open Postman.**

2. **Create a new POST request.**

3. **Enter the request URL:**
http://127.0.0.1:8000/api/compare-json/

4. **Set the request method to `POST`.**

5. **Go to the `Body` tab.**

6. **Select `form-data`.**

7. **Add two file fields:**

- For the first file:
  - Set the `Key` to `json1`.
  - Set the `Type` to `File`.
  - Choose your first JSON file as the value.

- For the second file:
  - Set the `Key` to `json2`.
  - Set the `Type` to `File`.
  - Choose your second JSON file as the value.

8. **Click "Send" to make the request.**

9. **Observe the response.**

The response should include the differences between the two JSON files, indicating which sections were added, removed, or modified.
