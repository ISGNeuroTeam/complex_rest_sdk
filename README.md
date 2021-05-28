# Complex Rest SDK

COMPLEX REST SDK for creating plugins

## Getting Started

### Installing
Install virtual environment from requirements.txt:
```bash
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r ./requirements.txt
```

### Create your plugin
```bash
source ./venv/bin/activate
cd ./complex_rest_sdk
python manage.py createplugin <plugin_name>
```
Your plugin start template will be available in ./plugin_dev/<plugin_name>  
To start developer server run:  

```bash
python manage.py runplugin <plugin_name> --port 8080
```
After starting developer server open http://localhost:8080/<plugin_name>/v1/example/
You must see:  

```json
{
    "message": "plugin with name <plugin_name> created successfully"
}
```
See [creating plugin](docs/creating_plugin.md)



