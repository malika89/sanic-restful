## dependency
 + python 3.7
 + mysql
 + consul

## deployment
### step 1: install requirements
``pip install -r requirments.txt``

### step 2: init database with aerich
```
pip install aerich
aerich init -t settings.db_config
aerich init-db
```

### step3: run app
``sh deploy/start.sh
or
python start.py
``

## upgrade the app
### case1 : modify or add the models
``aerich upgrade``
### case2: add new app
```
modify settings.py with installed_apps、db_config to add new app_name/model_name
modify router if needed
add new models/router/views (reference from common/base template)
```
