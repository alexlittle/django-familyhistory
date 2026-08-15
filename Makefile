.PHONY: run test cov

run:
	python manage.py runserver_plus \
		--cert-file certs/localhost+1.pem \
		--key-file certs/localhost+1-key.pem

test:
	pytest

cov:
	pytest --cov --cov-report=term-missing