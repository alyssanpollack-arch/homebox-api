from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

from auth import get_current_member
from categories import categorize
from database import Base, engine, get_db
from models import Household, Item, Member
from nlp import parse
from schemas import (
    AddItemRequest,
    AddItemResponse,
    CreateHouseholdRequest,
    DeleteResponse,
    ErrorResponse,
    HealthResponse,
    HouseholdResponse,
    ItemListResponse,
    ItemResponse,
    JoinHouseholdRequest,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
)
from search import fuzzy_search

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Homebox", version="1.0.0")


# --- Health ---

@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}


# --- Households ---

@app.post("/households", response_model=HouseholdResponse | ErrorResponse)
def create_household(body: CreateHouseholdRequest, db: Session = Depends(get_db)):
    if not body.household_name.strip() or not body.your_name.strip():
        return ErrorResponse(error="Household name and your name are required.")

    household = Household(name=body.household_name.strip())
    db.add(household)
    db.flush()

    member = Member(household_id=household.id, name=body.your_name.strip())
    db.add(member)
    db.commit()
    db.refresh(household)
    db.refresh(member)

    return HouseholdResponse(
        household_name=household.name,
        join_code=household.join_code,
        your_name=member.name,
        token=member.token,
    )


@app.post("/households/join", response_model=HouseholdResponse | ErrorResponse)
def join_household(body: JoinHouseholdRequest, db: Session = Depends(get_db)):
    code = body.join_code.strip().upper()
    household = db.query(Household).filter(Household.join_code == code).first()
    if not household:
        return ErrorResponse(error=f"No household found with code {code}. Check the code and try again.")

    if not body.your_name.strip():
        return ErrorResponse(error="Your name is required.")

    member = Member(household_id=household.id, name=body.your_name.strip())
    db.add(member)
    db.commit()
    db.refresh(member)

    return HouseholdResponse(
        household_name=household.name,
        join_code=household.join_code,
        your_name=member.name,
        token=member.token,
    )


# --- Items ---

@app.post("/items", response_model=AddItemResponse | ErrorResponse)
def add_item(
    body: AddItemRequest,
    member: Member | None = Depends(get_current_member),
    db: Session = Depends(get_db),
):
    if not member:
        return ErrorResponse(error="Invalid or missing token. Run Setup Homebox first.")

    result = parse(body.raw_input)
    if result is None:
        return ErrorResponse(
            error="I couldn't understand that. Try something like: 'the drill is in the garage' or 'drill, garage'."
        )

    item_name, location = result
    category = categorize(item_name)

    item = Item(
        household_id=member.household_id,
        added_by=member.id,
        name=item_name,
        location=location,
        category=category,
        raw_input=body.raw_input,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return AddItemResponse(
        message=f"Got it. {item_name} is in {location}.",
        item=ItemResponse(
            id=item.id,
            name=item.name,
            location=item.location,
            category=item.category,
            added_by=member.name,
            created_at=item.created_at,
        ),
    )


@app.post("/search", response_model=SearchResponse | ErrorResponse)
def search_items_post(
    body: SearchRequest,
    member: Member | None = Depends(get_current_member),
    db: Session = Depends(get_db),
):
    if not member:
        return ErrorResponse(error="Invalid or missing token. Run Setup Homebox first.")

    all_items = db.query(Item).filter(Item.household_id == member.household_id).all()
    matches = fuzzy_search(all_items, body.query)

    if not matches:
        message = "I didn't find anything matching that."
    else:
        parts = [f"{item.name} is in {item.location}" for item, score in matches[:3]]
        message = ". ".join(parts) + "."

    return SearchResponse(
        query=body.query,
        message=message,
        results=[
            SearchResultItem(
                id=item.id, name=item.name, location=item.location,
                category=item.category, score=score,
            )
            for item, score in matches
        ],
    )


@app.get("/items/search", response_model=SearchResponse | ErrorResponse)
def search_items(
    q: str = Query(..., min_length=1),
    member: Member | None = Depends(get_current_member),
    db: Session = Depends(get_db),
):
    if not member:
        return ErrorResponse(error="Invalid or missing token. Run Setup Homebox first.")

    all_items = db.query(Item).filter(Item.household_id == member.household_id).all()
    matches = fuzzy_search(all_items, q)

    return SearchResponse(
        query=q,
        results=[
            SearchResultItem(
                id=item.id,
                name=item.name,
                location=item.location,
                category=item.category,
                score=score,
            )
            for item, score in matches
        ],
    )


@app.get("/items", response_model=ItemListResponse | ErrorResponse)
def list_items(
    category: str | None = Query(None),
    location: str | None = Query(None),
    member: Member | None = Depends(get_current_member),
    db: Session = Depends(get_db),
):
    if not member:
        return ErrorResponse(error="Invalid or missing token. Run Setup Homebox first.")

    query = db.query(Item).filter(Item.household_id == member.household_id)

    if category:
        query = query.filter(Item.category.ilike(f"%{category}%"))
    if location:
        query = query.filter(Item.location.ilike(f"%{location}%"))

    items = query.order_by(Item.created_at.desc()).all()

    # We need member names for the response — batch lookup
    member_ids = {i.added_by for i in items}
    members = {m.id: m.name for m in db.query(Member).filter(Member.id.in_(member_ids)).all()} if member_ids else {}

    return ItemListResponse(
        count=len(items),
        items=[
            ItemResponse(
                id=i.id,
                name=i.name,
                location=i.location,
                category=i.category,
                added_by=members.get(i.added_by, "Unknown"),
                created_at=i.created_at,
            )
            for i in items
        ],
    )


@app.delete("/items/{item_id}", response_model=DeleteResponse | ErrorResponse)
def delete_item(
    item_id: int,
    member: Member | None = Depends(get_current_member),
    db: Session = Depends(get_db),
):
    if not member:
        return ErrorResponse(error="Invalid or missing token. Run Setup Homebox first.")

    item = (
        db.query(Item)
        .filter(Item.id == item_id, Item.household_id == member.household_id)
        .first()
    )
    if not item:
        return ErrorResponse(error="Item not found.")

    db.delete(item)
    db.commit()
    return DeleteResponse(message=f"Deleted {item.name}.")
