from app import app, db
from models.user import User

with app.app_context():
    # First delete test user if exists
    existing = User.query.filter_by(username='testuser').first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
    
    # Create test user
    test_user = User(username='testuser', email='test@test.com', name='Test User', village='TestVillage', state='TestState')
    test_user.set_password('password123')
    
    db.session.add(test_user)
    db.session.commit()
    
    # Verify password checking works
    retrieved_user = User.query.filter_by(username='testuser').first()
    print(f'User created: {retrieved_user.username}')
    print(f'User village: {retrieved_user.village}')
    print(f'Password hash exists: {bool(retrieved_user.password_hash)}')
    print(f'Password check (correct): {retrieved_user.check_password("password123")}')
    print(f'Password check (wrong): {retrieved_user.check_password("wrongpassword")}')

