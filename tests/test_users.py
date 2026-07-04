def test_edit_profile_as_student(client, mock_student_token, test_player):
    response = client.patch(
        f"/players/{test_player.player_id}",
        headers={"Authorization": f"Bearer {mock_student_token}"},
        json={"parent_name": "New Parent Name"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["parent_name"] == "New Parent Name"

def test_edit_profile_as_student_wrong_player(client, mock_student_token, db_session, test_player):
    # create another player
    import models
    another_player = models.Player(
        first_name="Another",
        last_name="Player",
        parent_name="Parent Another",
        email="another@test.com",
    )
    db_session.add(another_player)
    db_session.commit()
    db_session.refresh(another_player)

    response = client.patch(
        f"/players/{another_player.player_id}",
        headers={"Authorization": f"Bearer {mock_student_token}"},
        json={"parent_name": "Hacked Name"}
    )
    # Should be forbidden
    assert response.status_code == 403

def test_edit_profile_change_email(client, mock_student_token, test_player, db_session):
    response = client.patch(
        f"/players/{test_player.player_id}",
        headers={"Authorization": f"Bearer {mock_student_token}"},
        json={"email": "new_email@test.com", "parent_name": "Parent Test"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new_email@test.com"

    # Verify user email was also updated
    import models
    user = db_session.query(models.User).filter(models.User.player_id == test_player.player_id).first()
    assert user.email == "new_email@test.com"
