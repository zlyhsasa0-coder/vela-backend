from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker


app = FastAPI(title="VELA API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://vela-7li.pages.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    telegram_user_id = Column(
        String,
        index=True,
        nullable=True,
    )

    telegram_username = Column(
        String,
        nullable=True,
    )

    telegram_first_name = Column(
        String,
        nullable=True,
    )


Base.metadata.create_all(bind=engine)


def migrate_orders_table():
    with engine.begin() as connection:
        columns = connection.execute(
            text("PRAGMA table_info(orders)")
        ).fetchall()

        existing_columns = {
            column[1]
            for column in columns
        }

        if "telegram_user_id" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE orders "
                    "ADD COLUMN telegram_user_id VARCHAR"
                )
            )

        if "telegram_username" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE orders "
                    "ADD COLUMN telegram_username VARCHAR"
                )
            )

        if "telegram_first_name" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE orders "
                    "ADD COLUMN telegram_first_name VARCHAR"
                )
            )


migrate_orders_table()


class OrderCreate(BaseModel):
    order_number: str
    items: str
    total: float

    telegram_user_id: str | None = None
    telegram_username: str | None = None
    telegram_first_name: str | None = None


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


@app.post("/api/orders")
def create_order(order: OrderCreate):
    db = SessionLocal()

    new_order = OrderDB(
        order_number=order.order_number,
        items=order.items,
        total=order.total,
        status="Принят",

        telegram_user_id=order.telegram_user_id,
        telegram_username=order.telegram_username,
        telegram_first_name=order.telegram_first_name,
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

        "telegram_user_id": new_order.telegram_user_id,
        "telegram_username": new_order.telegram_username,
        "telegram_first_name": new_order.telegram_first_name,
    }

    db.close()

    return result


@app.get("/api/orders")
def get_orders():
    db = SessionLocal()

    orders = (
        db.query(OrderDB)
        .order_by(OrderDB.id.desc())
        .all()
    )

    result = [
        {
            "id": order.id,
            "order_number": order.order_number,
            "items": order.items,
            "total": order.total,
            "status": order.status,

            "telegram_user_id": order.telegram_user_id,
            "telegram_username": order.telegram_username,
            "telegram_first_name": order.telegram_first_name,
        }
        for order in orders
    ]

    db.close()

    return result