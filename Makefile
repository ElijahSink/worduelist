update-env:
	cat .heroku.env | xargs heroku config:set
