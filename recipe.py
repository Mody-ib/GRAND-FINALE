from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List
import pymysql
import pymysql.cursors

router = APIRouter()

# Database Configuration

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "recipe",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": False
}


def get_db():
    connection = pymysql.connect(**db_config)
    try:
        yield connection
    finally:
        connection.close()

# Recipe Schemas

class RecipeCreate(BaseModel):
    user_id: int
    name: str
    instructions: str
    servings: int
    prep_time: int


class RecipeResponse(BaseModel):
    recipe_id: int
    user_id: int
    name: str
    instructions: str
    servings: int
    prep_time: int

# Get All Recipes

@router.get(
    "/recipes",
    response_model=List[RecipeResponse]
)
def get_all_recipes(db=Depends(get_db)):

    with db.cursor() as cursor:

        cursor.execute("""
            SELECT
                recipe_id,
                user_id,
                name,
                instructions,
                servings,
                prep_time
            FROM Recipe
        """)

        return cursor.fetchall()

#Get One Recipe

@router.get(
    "/recipes/{recipe_id}",
    response_model=RecipeResponse
)
def get_recipe(
    recipe_id: int,
    db=Depends(get_db)
):

    with db.cursor() as cursor:

        cursor.execute("""
            SELECT
                recipe_id,
                user_id,
                name,
                instructions,
                servings,
                prep_time
            FROM Recipe
            WHERE recipe_id = %s
        """, (recipe_id,))

        recipe = cursor.fetchone()

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found"
            )

        return recipe

# POST - Create Recipe

@router.post(
    "/recipes",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_recipe(
    recipe: RecipeCreate,
    db=Depends(get_db)
):

    try:

        with db.cursor() as cursor:

            cursor.execute("""
                INSERT INTO Recipe
                (
                    user_id,
                    name,
                    instructions,
                    servings,
                    prep_time
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                recipe.user_id,
                recipe.name,
                recipe.instructions,
                recipe.servings,
                recipe.prep_time
            ))

            recipe_id = cursor.lastrowid

            db.commit()

            cursor.execute("""
                SELECT
                    recipe_id,
                    user_id,
                    name,
                    instructions,
                    servings,
                    prep_time
                FROM Recipe
                WHERE recipe_id = %s
            """, (recipe_id,))

            return cursor.fetchone()

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )



# PUT - Update Recipe


@router.put(
    "/recipes/{recipe_id}",
    response_model=RecipeResponse
)
def update_recipe(
    recipe_id: int,
    recipe: RecipeCreate,
    db=Depends(get_db)
):

    try:

        with db.cursor() as cursor:

            # Check if recipe exists
            cursor.execute("""
                SELECT recipe_id
                FROM Recipe
                WHERE recipe_id = %s
            """, (recipe_id,))

            existing_recipe = cursor.fetchone()

            if not existing_recipe:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recipe not found"
                )

            # Update recipe
            cursor.execute("""
                UPDATE Recipe
                SET
                    user_id = %s,
                    name = %s,
                    instructions = %s,
                    servings = %s,
                    prep_time = %s
                WHERE recipe_id = %s
            """, (
                recipe.user_id,
                recipe.name,
                recipe.instructions,
                recipe.servings,
                recipe.prep_time,
                recipe_id
            ))

            db.commit()

            # Return updated recipe
            cursor.execute("""
                SELECT
                    recipe_id,
                    user_id,
                    name,
                    instructions,
                    servings,
                    prep_time
                FROM Recipe
                WHERE recipe_id = %s
            """, (recipe_id,))

            return cursor.fetchone()

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


# Delete Recipe


@router.delete(
    "/recipes/{recipe_id}"
)
def delete_recipe(
    recipe_id: int,
    db=Depends(get_db)
):

    try:

        with db.cursor() as cursor:

            # Check if recipe exists
            cursor.execute("""
                SELECT recipe_id
                FROM Recipe
                WHERE recipe_id = %s
            """, (recipe_id,))

            existing_recipe = cursor.fetchone()

            if not existing_recipe:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recipe not found"
                )

            # Delete recipe
            cursor.execute("""
                DELETE FROM Recipe
                WHERE recipe_id = %s
            """, (recipe_id,))

            db.commit()

            return {
                "message": "Recipe deleted successfully"
            }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )