import datetime

from flask import Blueprint, jsonify, request
from loguru import logger

from todo.models import db
from todo.models.todo import Todo

api = Blueprint("api", __name__, url_prefix="/api/v1")

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00",
}


@api.route("/health")
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route("/todos", methods=["GET"])
def get_todos():
    """Return the list of todo items"""
    completed = request.args.get("completed", None, type=bool)
    window = request.args.get("window", None, type=int)

    query = db.select(Todo)

    if completed is not None:
        query = query.where(Todo.completed == completed)

    if window is not None:
        cur_time = datetime.datetime.now(datetime.UTC)
        window_time = cur_time + datetime.timedelta(days=window)

        query = query.where(Todo.deadline_at < window_time)

    todos: list[Todo] = db.session.execute(query).scalars()

    return jsonify([todo.to_dict() for todo in todos])


@api.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id: int):
    """Return the details of a todo item"""
    todo: Todo | None = db.session.execute(
        db.select(Todo).where(Todo.id == todo_id)
    ).scalar_one_or_none()

    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    return jsonify(todo.to_dict())


@api.route("/todos", methods=["POST"])
def create_todo():
    """Create a new todo item and return the created item"""
    body: dict = request.json

    allowed_fields = set(["title", "description", "completed", "deadline_at"])
    for key in body.keys():
        if key not in allowed_fields:
            logger.debug(f"Key '{key}' not allowed")
            return jsonify({"error": "Extra fields are detected."}), 400

    title = body.get("title", None)
    if title is None:
        return jsonify({"error": "Title field is not given in request body"}), 400

    todo = Todo(
        title=title,
        description=body.get("description"),
        completed=body.get("completed", False),
    )

    m_deadline_at: str | None = body.get("deadline_at", None)

    if m_deadline_at is not None:
        try:
            todo.deadline_at = datetime.datetime.fromisoformat(m_deadline_at)
        except TypeError as e:
            logger.debug(f"Type Error - {e}")
            return jsonify({"error": "Invalid 'deadline_at' datetime"}), 404
        except ValueError as e:
            logger.debug(f"Value Error - {e}")
            return jsonify({"error": "Invalid 'deadline_at' datetime"}), 404

    # Adds a new record to the database or will update an existing record.
    db.session.add(todo)

    # Commits the changes to the database.
    # This must be called for the changes to be saved.
    db.session.commit()
    return jsonify(todo.to_dict()), 201


@api.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id: int):
    """Update a todo item and return the updated item"""

    body: dict = request.json

    allowed_fields = set(["title", "description", "completed", "deadline_at"])
    for key in body.keys():
        if key not in allowed_fields:
            logger.debug(f"Key '{key}' not allowed")
            return jsonify({"error": "Extra fields are detected."}), 400

    todo: Todo | None = db.session.execute(
        db.select(Todo).where(Todo.id == todo_id)
    ).scalar_one_or_none()

    if todo is None:
        return jsonify({"error": "Todo not found"}), 404

    if body.get("id", None) is not None:
        return jsonify({"error": "Not allowed to change the 'id' field of a todo"}), 400

    todo.title = body.get("title", todo.title)
    todo.description = body.get("description", todo.description)
    todo.completed = body.get("completed", todo.completed)
    todo.deadline_at = body.get("deadline_at", todo.deadline_at)

    db.session.commit()
    return jsonify(todo.to_dict())


@api.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id: int):
    """Delete a todo item and return the deleted item"""

    todo: Todo | None = db.session.execute(
        db.select(Todo).where(Todo.id == todo_id)
    ).scalar_one_or_none()

    if todo is None:
        return jsonify({}), 200

    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
