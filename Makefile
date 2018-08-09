_tests:
	flake8
	python3 -m pytest
tests: _tests

clean:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info
	find . -type d -name "__pycache__" -exec rm -r "{}" \;
