import json
from db import db
from models import Admin, Project, User, Pair, Group, GroupUser, Warn, Ban

admins = [
        {
            "fullname": "Aleekk | Dev of GrimaceCoin",
            "username": "aLeekk0",
            "user_id": "1533375074",
            "password": "shillmaster"
        },
        {
            "fullname": "Kaan $GM ☕️ | Business Developer of GrimaceCoin",
            "username": "KaanApes",
            "user_id": "5191683494",
            "password": "shillmaster"
        },
        {
            "fullname": "WebStar",
            "username": "webstarlee",
            "user_id": "5887308508",
            "password": "55486"
        },
    ]

def admin_mysql():
    for admin in admins:
        exist = Admin.query.filter_by(user_id=admin['user_id']).first()
        if exist == None:
            new_admin = Admin(
                fullname=admin['fullname'],
                username=admin['username'],
                user_id=admin['user_id'],
                password=admin['password']
            )
            new_admin.save_to_db()
            

def project_json_to_mysql():
    f = open('projects.json', encoding="utf8")
    data = json.load(f)
    for i in data:
        project_exist = Project.query.filter_by(user_id=i['user_id']).filter_by(pair_address=i['pair_address']).first()
        if project_exist == None:
            print("add project: ", i['token_symbol'])
            project = Project(
                user_id=i['user_id'],
                group_id=i['chat_id'],
                chain=i['chain_id'],
                token=i['token'],
                symbol=i['token_symbol'],
                pair_address=i['pair_address'],
                pair_url=i['url'],
                marketcap=i['marketcap'],
                ath=i['ath_value'],
                status=i['status'],
            )
            db.session.add(project)
            db.session.commit()

def user_json_to_mysql():
    f = open('projects.json', encoding="utf8")
    data = json.load(f)
    user_lists=[]
    for i in data:
        if i['username'] != "":
            user = {"user_id": i['user_id'], 'username': i['username']}
            exist = [user_list for user_list in user_lists if user_list['user_id'] == user['user_id']]
            if len(exist)==0:
                user_lists.append(user)
    
    for user_list in user_lists:
        user_exist = User.query.filter_by(username=user_list['username']).first()
        if user_exist == None:
            user = User(
                user_id=user_list['user_id'],
                username=user_list['username'],
                fullname=user_list['username']
            )
            db.session.add(user)
            db.session.commit()

def pair_json_to_mysql():
    f = open('pairs.json', encoding="utf8")
    data = json.load(f)
    for i in data:
        pair_exist = Pair.query.filter_by(pair_address=i['pair_address']).first()
        if pair_exist == None:
            print("add project: ", i['pair_address'])
            pair = Pair(
                chain=i['chain_id'],
                token=i['token'],
                symbol=i['symbol'],
                pair_address=i['pair_address'],
                pair_url=i['url'],
                marketcap=i['marketcap'],
                status=i['status'],
            )
            db.session.add(pair)
            db.session.commit()

def warn_json_to_mysql():
    f = open('warns.json', encoding="utf8")
    data = json.load(f)
    for i in data:
        if "-100" in i['chat_id']:
            warn_exist = Warn.query.filter_by(user_id=i['user_id']).filter_by(group_id=i['chat_id']).first()
            if warn_exist == None:
                print("add warning: ", i['user_id'])
                warn = Warn(
                    user_id=i['user_id'],
                    group_id=i['chat_id'],
                    count=i['count']
                )
                db.session.add(warn)
                db.session.commit()

def ban_json_to_mysql():
    f = open('bans.json', encoding="utf8")
    data = json.load(f)
    for i in data:
        if "-100" in i['chat_id']:
            ban_exist = Ban.query.filter_by(user_id=i['user_id']).filter_by(group_id=i['chat_id']).first()
            if ban_exist == None:
                print("add ban: ", i['user_id'])
                ban = Ban(
                    user_id=i['user_id'],
                    group_id=i['chat_id']
                )
                db.session.add(ban)
                db.session.commit()

def group_mysql_from_project():
    projects = Project.query.all()
    group_ids = []
    for project in projects:
        if "-100" in project.group_id and project.group_id not in group_ids:
            group_ids.append(project.group_id)
    
    for group_id in group_ids:
        group_exist = Group.query.filter_by(group_id=group_id).first()
        if group_exist == None:
            group = Group(
                group_id=group_id
            )
            db.session.add(group)
            db.session.commit()

def group_users_mysql_from_project():
    projects = Project.query.all()
    group_user_lists = []
    for project in projects:
        if "-100" in project.group_id:
            group_user = {"user_id": project.user_id, 'group_id': project.group_id}
            exist = [group_user_list for group_user_list in group_user_lists if group_user_list['user_id'] == group_user['user_id'] and group_user_list['group_id'] == group_user['group_id'] ]
            if len(exist) == 0:
                group_user_lists.append(group_user)
    
    for group_user_list in group_user_lists:
        group_user_exist = GroupUser.query.filter_by(group_id=group_user_list['group_id']).filter_by(user_id=group_user_list['user_id']).first()
        if group_user_exist == None:
            print(group_user_list)
            group_user = GroupUser(
                group_id=group_user_list['group_id'],
                user_id=group_user_list['user_id'],
            )
            db.session.add(group_user)
            db.session.commit()