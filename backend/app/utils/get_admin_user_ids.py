def get_admin_user_ids():
    try:
        # Create an application context
        with app.app_context():
            users = LocalUser.query.all()
            admin_user_ids = [user.id for user in users if user.is_admin]
            return admin_user_ids
    except Exception as e:
        print(f"An error occurred while fetching admins' IDs: {str(e)}")
