def test_enroll_in_class(client, mock_student_token, test_player, test_class):
    response = client.post(
        "/classes/enrollments/",
        headers={"Authorization": f"Bearer {mock_student_token}"},
        json={
            "player_id": str(test_player.player_id),
            "class_id": str(test_class.class_id),
            "start_date": "2024-01-01"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Active"
    assert data["player_id"] == str(test_player.player_id)
    assert data["class_id"] == str(test_class.class_id)

def test_manage_enrollment(client, mock_student_token, test_player, test_class, db_session):
    # Setup initial enrollment
    import models
    from datetime import date
    enrollment = models.Enrollment(
        player_id=test_player.player_id,
        class_id=test_class.class_id,
        start_date=date.today(),
        status=models.StatusEnum.Active
    )
    db_session.add(enrollment)
    db_session.commit()
    db_session.refresh(enrollment)

    # Now update it
    response = client.put(
        f"/classes/enrollments/{enrollment.enrollment_id}",
        headers={"Authorization": f"Bearer {mock_student_token}"},
        json={"status": "Paused"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Paused"
