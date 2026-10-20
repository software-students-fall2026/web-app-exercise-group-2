import mongomock
import pytest
from bson import ObjectId

import app as post_app


@pytest.fixture
def client():
    collection = mongomock.MongoClient().test_posts.posts
    post_app.app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        POSTS_COLLECTION=collection,
    )
    collection.delete_many({})
    yield post_app.app.test_client(), collection
    post_app.app.config.pop("POSTS_COLLECTION", None)


def token_for(client):
    client.get("/add_post")
    with client.session_transaction() as session:
        return session["csrf_token"]


def add_owned_post(client, collection):
    token = token_for(client)
    response = client.post(
        "/save",
        data={
            "csrf_token": token,
            "title": "Lost keys",
            "description": "Three keys on a red loop",
            "last_seen": "Library, today",
        },
    )
    assert response.status_code == 302
    return collection.find_one({"title": "Lost keys"})


def test_feed_renders_database_posts_and_only_owner_controls(client):
    client, collection = client
    owned = add_owned_post(client, collection)
    collection.insert_one(
        {"title": "Old post", "description": "Legacy", "last_seen": "Campus"}
    )

    page = client.get("/home")

    assert b"Lost keys" in page.data
    assert b"Old post" in page.data
    assert page.data.count(b">Edit</a>") == 1
    assert page.data.count(b">Delete</a>") == 1
    assert str(owned["_id"]).encode() in page.data


def test_edit_prefills_and_saves_all_fields(client):
    client, collection = client
    post = add_owned_post(client, collection)
    edit_url = f"/posts/{post['_id']}/edit"

    page = client.get(edit_url)
    assert b'value="Lost keys"' in page.data
    assert b"Three keys on a red loop" in page.data
    assert b'value="Library, today"' in page.data
    assert b"Cancel" in page.data

    response = client.post(
        edit_url,
        data={
            "csrf_token": token_for(client),
            "title": "Found keys",
            "description": "Dropped near the entrance",
            "last_seen": "Main entrance",
        },
    )
    assert response.status_code == 302
    updated = collection.find_one({"_id": post["_id"]})
    assert (updated["title"], updated["description"], updated["last_seen"]) == (
        "Found keys",
        "Dropped near the entrance",
        "Main entrance",
    )


def test_edit_rejects_missing_fields_and_csrf(client):
    client, collection = client
    post = add_owned_post(client, collection)
    edit_url = f"/posts/{post['_id']}/edit"

    invalid = client.post(
        edit_url,
        data={"csrf_token": token_for(client), "title": "", "description": "x", "last_seen": "y"},
    )
    assert invalid.status_code == 400
    assert collection.find_one({"_id": post["_id"]})["title"] == "Lost keys"
    assert client.post(edit_url, data={"title": "forged"}).status_code == 400


def test_create_rejects_missing_fields_and_csrf(client):
    client, collection = client
    token = token_for(client)
    invalid = client.post(
        "/save",
        data={"csrf_token": token, "title": "Only title", "description": "", "last_seen": ""},
    )
    assert invalid.status_code == 400
    assert collection.count_documents({}) == 0
    assert client.post(
        "/save",
        data={"title": "No CSRF", "description": "text", "last_seen": "somewhere"},
    ).status_code == 400
    assert collection.count_documents({}) == 0


def test_other_session_cannot_edit_or_delete_post(client):
    client, collection = client
    post = add_owned_post(client, collection)
    ownerless = collection.insert_one(
        {"title": "Legacy", "description": "No owner", "last_seen": "Campus"}
    ).inserted_id
    other_client = post_app.app.test_client()

    assert other_client.get(f"/posts/{post['_id']}/edit").status_code == 404
    assert other_client.post(
        f"/posts/{post['_id']}/edit",
        data={"title": "hacked", "description": "x", "last_seen": "y"},
    ).status_code == 404
    assert other_client.post(
        f"/posts/{post['_id']}/delete", data={"csrf_token": "anything"}
    ).status_code == 404
    assert client.get(f"/posts/{ownerless}/edit").status_code == 404
    assert client.get(f"/posts/{ownerless}/delete").status_code == 404
    assert collection.find_one({"_id": post["_id"]})["title"] == "Lost keys"


def test_delete_requires_confirmation_get_then_csrf_protected_post(client):
    client, collection = client
    post = add_owned_post(client, collection)
    delete_url = f"/posts/{post['_id']}/delete"

    page = client.get(delete_url)
    assert page.status_code == 200
    assert b"Are you sure?" in page.data
    assert collection.find_one({"_id": post["_id"]}) is not None

    assert client.post(delete_url, data={"csrf_token": "bad"}).status_code == 400
    assert collection.find_one({"_id": post["_id"]}) is not None
    response = client.post(delete_url, data={"csrf_token": token_for(client)})
    assert response.status_code == 302
    assert collection.find_one({"_id": post["_id"]}) is None


@pytest.mark.parametrize("post_id, expected", [("nope", 400), (str(ObjectId()), 404)])
def test_invalid_or_missing_post_ids_are_handled(client, post_id, expected):
    client, _ = client
    add_owned_post(client, client.application.config["POSTS_COLLECTION"])
    assert client.get(f"/posts/{post_id}/edit").status_code == expected
    assert client.get(f"/posts/{post_id}/delete").status_code == expected
