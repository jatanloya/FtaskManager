from flask import Flask, g, flash, render_template, redirect, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
import models
import forms

app = Flask(__name__)
app.secret_key = 'skjdfsltyi478idhsklfjfgkljbisghfksgbshjgrajrajhans!'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(u_id):
    try:
        return models.Users.get(models.Users.id == u_id)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    g.db = models.DATABASE_proxy
    g.db.connection()
    g.user = current_user


@app.after_request
def after_request(res):
    g.db.close()
    return res


@app.route('/register', methods=(['GET', 'POST']))
def register():
    form = forms.RegisterForm()

    if form.validate_on_submit():
        models.Users.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        flash('You have registered successfully!', 'success')

        return "Registration Successful, Redirect Somewhere"
    return render_template('register.html', form=form)


@app.route('/', methods=(['GET', 'POST']))
def login():
    form = forms.LoginForm()

    if form.validate_on_submit():
        try:
            user = models.Users.get(models.Users.username == form.username.data)
        except models.DoesNotExist:
            flash("Username or Password does not match", "danger")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Logged in successfully", "success")
                return render_template("tasks.html")
            else:
                flash("Username or Password does not match", "danger")
    return render_template("login.html", form=form)


@app.route('/tasks')
@login_required
def tasks():
    active = None
    projects = models.Projects.select()
    tasks = models.Tasks.select()

    if len(projects) == 1:
        models.Projects.update(
            active=True
        ).where(
            models.Projects.id == projects[0].id
        ).execute()

        active = projects[0].id

    if projects:
        for project in projects:
            if project.active:
                active = project.id
        if not active:
            projects[0].active = True
            active = projects[0].id
    else:
        projects = None

    if projects:
        for task in tasks:
            print(task.task)
        return render_template('tasks.html', tasks=tasks, projects=projects, active=active)
    else:
        return render_template('tasks.html', tasks=tasks, active=active)


@app.route('/add', methods=['POST'])
def add_task():
    found = False
    project_id = None
    task = request.form['task']
    project = request.form['project']

    if not task:
        return redirect('/')

    if not project:
        project = 'Tasks'

    projects = models.Projects.select()

    for proj in projects:
        if proj.name == project:
            found = True

    # add the project if not in database already
    if not found:
        models.Projects.create(
            name=project,
            active=True
        )
        projects = models.Projects.select()

    # set the active tab
    for proj in projects:
        if proj.name == project:
            project_id = proj.id
            proj.active = True
        else:
            proj.active = False

    status = bool(int(request.form['status']))

    # add the new task
    models.Tasks.create(
        project_id=project_id,
        task=task,
        status=status
    )

    return redirect(request.referrer)


@app.route('/close/<int:task_id>')
def close_task(task_id):
    task = models.Tasks.select().where(models.Tasks.id == task_id)[0]

    if not task:
        return redirect(request.referrer)

    if task.status:
        models.Tasks.update(
            status=False
        ).where(
            models.Tasks.id == task_id
        ).execute()
    else:
        models.Tasks.update(
            status=True
        ).where(
            models.Tasks.id == task_id
        ).execute()

    return redirect(request.referrer)


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = models.Tasks.select().where(models.Tasks.id == task_id)[0]

    if not task:
        return redirect(request.referrer)

    models.Tasks.get(
        models.Tasks.id == task_id
    ).delete_instance()

    return redirect(request.referrer)


@app.route('/clear/<delete_id>')
def clear_all(delete_id):
    models.Tasks.get(
        models.Tasks.project_id == delete_id
    ).delete_instance()

    models.Projects.get(
        models.Projects.id == delete_id
    ).delete_instance()

    return redirect(request.referrer)


@app.route('/remove/<lists_id>')
def remove_all(lists_id):
    models.Tasks.get(
        models.Tasks.project_id == lists_id
    ).delete_instance()

    return redirect(request.referrer)


@app.route('/project/<tab>')
def tab_nav(tab):
    """Switches between active tabs"""
    projects = models.Projects.select()

    for project in projects:
        if project.name == tab:
            models.Projects.update(
                active=True
            ).where(
                models.Projects.id == project.id
            ).execute()
        else:
            models.Projects.update(
                active=False
            ).where(
                models.Projects.id == project.id
            ).execute()

    return redirect(request.referrer)



if __name__ == '__main__':
    print("I am here")
    models.initialize()
    app.run()
