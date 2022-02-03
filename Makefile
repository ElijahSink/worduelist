update-env:
	cat .env | xargs heroku config:set
