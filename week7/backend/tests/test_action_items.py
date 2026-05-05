def test_create_complete_list_and_patch_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False
    assert "created_at" in item and "updated_at" in item

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/", params={"completed": True, "limit": 5, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.patch(f"/action-items/{item['id']}", json={"description": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["description"] == "Updated"


def test_get_delete_and_validate_action_items(client):
    r = client.post("/action-items/", json={"description": "Review PR"})
    assert r.status_code == 201, r.text
    item = r.json()

    r = client.get(f"/action-items/{item['id']}")
    assert r.status_code == 200
    assert r.json()["description"] == "Review PR"

    r = client.delete(f"/action-items/{item['id']}")
    assert r.status_code == 204, r.text

    r = client.get(f"/action-items/{item['id']}")
    assert r.status_code == 404

    r = client.post("/action-items/", json={"description": "   "})
    assert r.status_code == 422

    r = client.get("/action-items/", params={"sort": "-bogus"})
    assert r.status_code == 400

    r = client.get("/action-items/", params={"limit": 0})
    assert r.status_code == 422


