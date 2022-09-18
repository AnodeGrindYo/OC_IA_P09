import requests
from flask import Flask, request, render_template

NB_USERS = 322896
user_id = 1


app = Flask(__name__)

# Endpoint homepage
@app.route('/', methods=["GET","POST"])
def index():

    global user_id
    if request.form.get('user'):
        user_id = int(request.form.get('user'))

    user_id = user_id if user_id <= NB_USERS else NB_USERS
    user_id = user_id if user_id >= 0 else 0

    global selected_type
    if request.form.get('rec'):
        selected_type = str(request.form.get('rec'))

    return render_template(
        'index.html', 
        sended=False, 
        user_id=user_id, 
    )

# Endpoint appel API
@app.route('/recommend/', methods=["GET","POST"])
def recommendArticles():

    params = {"user_id": user_id}
    # print('params : ' + str(params), flush=True)
    
    # Appel Azure function
    r = requests.get(
        'https://recommander.azurewebsites.net/api/getRecommandation', 
        # "http://localhost:7071/api/getRecommandation",
        json=params, 
        verify=True
    )

    content = r.content.decode("utf-8")

    remove ='[ ]'
    for charac in remove:
        content = content.replace(charac, '')

    content = content.split(',')

    return render_template(
        'index.html', 
        sended=True, 
        user_id=user_id, 
        result=content
    )

if __name__ == "__main__":
    app.run()