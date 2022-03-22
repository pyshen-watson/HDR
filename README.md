# Environment
- Language: python 3.7.5
- Modules: openCV, NumPy, matplotlab, pillow, piexif

We use `pipenv` to manage our package. If your don't have `pipenv` , run this: `$ pip install pipenv`
## Install the dependency
```$ pipenv install --dev```
## Run the code
```$ pipenv run python main.py```
Then input the id of the album. If the images doesn't exist, the program will download them from google drive.
