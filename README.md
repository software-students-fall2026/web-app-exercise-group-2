# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

Our goal is to create a centralized lost and found app for users to report losing certain items, report the discovery of lost items, share information about lost items, and claim lost items.

## User stories

User stories are being tracked with github issues: https://github.com/software-students-fall2026/web-app-exercise-group-2/issues

## Steps necessary to run the software

1. Prerequisites

Python
Git
A MongoDB database like MongoDB atlas

2. Clone the Repo

```bash
git clone https://github.com/software-students-fall2026/web-app-exercise-group-2.git
cd web-app-exercise-group-2
```

3. Run the Setup Script

Mac: 

```bash
python3 .automations/setup.py
```

Windows: 

```bash
python .automations/setup.py
```

4. Create a virtual environment and install dependencies

Mac:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows:

```bash
python -m venv .venv   
.venv\Scripts\activate.bat     
pip install -r requirements.txt
```

5. Configure environment variables

Create a file called `.env` in the root directory, Use `env.example` as a template:

```bash
cp env.example .env
```

Fill in these values in .env:

| Variable | Description |
|---|---|
| `MONGO_URI` | MongoDB connection string |
| `MONGO_DBNAME` | Name of the Mongo database |
| `SECRET_KEY` | a secret key used by Flask |

6. Run the app

Activate your virtual environment and run: 

```bash
python app.py
```

and then go to: http://127.0.0.1:5000

7. Create an account to use the app

Create and log in with your account and you can create, delete, update, view and search lost and found posts or reply to other posts

| Page | URL | Description |
|---|---|---|
| Sign Up | `/signup` | Create an account |
| Login | `/login` | Log in |
| Home | `/home` | View and search lost and found posts |
| Add Post | `/add_post` | Create a new post |
| Post Details | `/post/<post_id>` | View a post and its replies |
| Edit Post | `/edit/<post_id>` | Edit a post |

## Task boards

https://github.com/orgs/software-students-fall2026/projects/5
