install:
	# install dependencies
	pip install --upgrade pip &&\
		pip --default-timeout=1000 install -r requirements/base.txt 

format:
	# format python code with black
	find . -name "*.py" ! -path "./venv/*" | xargs black
lint:
	# check code syntaxes
	find . -name "*.py" ! -path "./venv/*" |  xargs pylint --disable=R,C