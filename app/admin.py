from sqladmin import Admin, ModelView

from app.models.user import User
from app.models.team import Team
from app.models.task import Task
from app.models.evaluation import Evaluation
from app.models.meeting import Meeting


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    can_create = False
    can_edit = True
    can_delete = True

    column_list = [
        User.id,
        User.email,
        User.full_name,
        User.role,
        User.is_active,
        User.team_id,
        User.team,
    ]

    column_searchable_list = [User.email, User.full_name]
    column_sortable_list = [User.id, User.email, User.role]
    form_columns = [
        User.email,
        User.full_name,
        User.role,
        User.is_active,
        User.team_id,
    ]


class TeamAdmin(ModelView, model=Team):
    name = "Team"
    name_plural = "Teams"
    icon = "fa-solid fa-users"

    column_list = [
        Team.id,
        Team.name,
        Team.code,
    ]

    column_searchable_list = [Team.name, Team.code]
    column_sortable_list = [Team.id, Team.name, Team.code]

    form_columns = [
        Team.name,
        Team.code,
    ]


class TaskAdmin(ModelView, model=Task):
    name = "Task"
    name_plural = "Tasks"
    icon = "fa-solid fa-list-check"

    column_list = [
        Task.id,
        Task.title,
        Task.status,
        Task.deadline,
        Task.author,
        Task.executor,
        Task.team,
    ]

    column_searchable_list = [Task.title, Task.description]
    column_sortable_list = [Task.id, Task.title, Task.status, Task.deadline]

    form_columns = [
        Task.title,
        Task.description,
        Task.status,
        Task.deadline,
        Task.author,
        Task.executor,
        Task.team,
    ]


class EvaluationAdmin(ModelView, model=Evaluation):
    name = "Evaluation"
    name_plural = "Evaluations"
    icon = "fa-solid fa-star"

    column_list = [
        Evaluation.id,
        Evaluation.score,
        Evaluation.task,
        Evaluation.manager,
        Evaluation.employee,
        Evaluation.created_at,
    ]

    column_searchable_list = [Evaluation.comment]
    column_sortable_list = [
        Evaluation.id,
        Evaluation.score,
        Evaluation.created_at,
    ]

    form_columns = [
        Evaluation.score,
        Evaluation.comment,
        Evaluation.task,
        Evaluation.manager,
        Evaluation.employee,
    ]


class MeetingAdmin(ModelView, model=Meeting):
    name = "Meeting"
    name_plural = "Meetings"
    icon = "fa-solid fa-calendar-days"

    can_create = False
    can_edit = False

    column_list = [
        Meeting.id,
        Meeting.title,
        Meeting.start_time,
        Meeting.end_time,
        Meeting.organizer,
    ]

    column_searchable_list = [Meeting.title, Meeting.description]
    column_sortable_list = [
        Meeting.id,
        Meeting.title,
        Meeting.start_time,
        Meeting.end_time,
    ]

    form_columns = [
        Meeting.title,
        Meeting.description,
        Meeting.start_time,
        Meeting.end_time,
        Meeting.organizer,
        Meeting.participants,
    ]


def setup_admin(app, engine):
    admin = Admin(app, engine)

    admin.add_view(UserAdmin)
    admin.add_view(TeamAdmin)
    admin.add_view(TaskAdmin)
    admin.add_view(EvaluationAdmin)
    admin.add_view(MeetingAdmin)
