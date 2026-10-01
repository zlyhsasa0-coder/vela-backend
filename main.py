from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI(title="VELA API")


# =========================
# DATABASE
# =========================

DATABASE_URL = "sqlite:///./vela.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


class OrderDB(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    items = Column(Text)
    total = Column(Float)
    status = Column(String)


Base.metadata.create_all(bind=engine)


# =========================
# MODELS
# =========================

class OrderCreate(BaseModel):
    order_number: str
    items: str
    total: float


# =========================
# BASIC ROUTES
# =========================

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "VELA API",
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "message": "VELA backend работает",
    }


# =========================
# ORDERS
# =========================

@app.post("/api/orders")
def create_order(order: OrderCreate):
    db = SessionLocal()

    new_order = OrderDB(
        order_number=order.order_number,
        items=order.items,
        total=order.total,
        status="Принят",
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    result = {
        "id": new_order.id,
        "order_number": new_order.order_number,
        "items": new_order.items,
        "total": new_order.total,
        "status": new_order.status,
    }

    db.close()

    return result


@app.get("/api/orders")
def get_orders():
    db = SessionLocal()

    orders = db.query(OrderDB).order_by(OrderDB.id.desc()).all()

    result = [
        {
            "id": order.id,
            "order_number": order.order_number,
            "items": order.items,
            "total": order.total,
            "status": order.status,
        }
        for order in orders
    ]

    db.close()

    return result