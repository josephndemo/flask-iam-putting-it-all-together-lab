from app import app
from config import db
from models import User, Recipe

with app.app_context():

    db.drop_all()
    db.create_all()

    user1 = User(
        username="chef_john",
        image_url="https://i.pravatar.cc/300",
        bio="Professional chef"
    )
    user1.password_hash = "password123"

    user2 = User(
        username="foodie_sarah",
        image_url="https://i.pravatar.cc/301",
        bio="I love cooking"
    )
    user2.password_hash = "password123"

    db.session.add_all([user1, user2])
    db.session.commit()

    recipe1 = Recipe(
        title="Creamy Pasta",
        instructions="""
        Boil pasta until tender. Prepare creamy sauce
        using butter, garlic, milk, and parmesan cheese.
        Combine pasta and sauce thoroughly before serving.
        """,
        minutes_to_complete=30,
        user_id=user1.id
    )

    recipe2 = Recipe(
        title="Chicken Curry",
        instructions="""
        Cook onions, garlic, ginger, and spices together.
        Add chicken and simmer with coconut milk until
        fully cooked and flavorful before serving.
        """,
        minutes_to_complete=45,
        user_id=user2.id
    )

    db.session.add_all([recipe1, recipe2])
    db.session.commit()

    print("Database seeded successfully!")