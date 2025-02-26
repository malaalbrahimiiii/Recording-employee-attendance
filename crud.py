import calendar
import uuid
from typing import Any
from datetime import datetime, time, timedelta
from sqlmodel import Session, select, func

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate, DailyAttendance, Attendance, WeeklyAttendance
from app.logger import logger

def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    logger.info(f"User created: {db_obj.email}")
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    logger.info(f"User updated: {db_user.email}")
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    logger.info(f"User found: {session_user.email}")
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    logger.info(f"User authenticated: {db_user.email}")
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def create_daily_attendance(
        *, session: Session, 
        user_id: uuid.UUID, 
        full_name: str,
        attend_id: int,
        date: datetime) -> DailyAttendance:
    db_attendance_statement = (select(Attendance)
    .where(Attendance.user_id == user_id)
    .where(func.date(Attendance.created_at) == date.date()))
    db_attendance = session.exec(db_attendance_statement).all()

    if len(db_attendance) < 2:
        raise ValueError("Insufficient attendance records for today")

    check_in_time = db_attendance[0].created_at
    check_out_time = db_attendance[1].created_at

    daily_attendance_hours = (check_out_time - check_in_time).total_seconds() / 3600
    db_daily_attendance = DailyAttendance(daily_attendance_hours=daily_attendance_hours, user_id=user_id,
                                          full_name=full_name, attend_id=attend_id)
    session.add(db_daily_attendance)
    session.commit()
    session.refresh(db_daily_attendance)
    logger.info(f"Daily attendance created: {db_daily_attendance.user_id}")
    return db_daily_attendance

def create_weekly_attendance_or_update(
        *, session: Session,                        
        user_id: uuid.UUID,
        full_name: str,
        attend_id: int,
        daily_attendance_hours: int, 
        date: datetime
        ) -> WeeklyAttendance:
    today = date #date.today()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=6)
    
    db_weekly_attendance_statement = (select(WeeklyAttendance)
    .where(WeeklyAttendance.user_id == user_id)
    .where(func.date(WeeklyAttendance.start_date) <= date.date())
    .where(func.date(WeeklyAttendance.end_date) >= date.date()))
    db_weekly_attendance = session.exec(db_weekly_attendance_statement).first()
    if db_weekly_attendance:
        db_weekly_attendance.weekly_attendance_hours += daily_attendance_hours
    else:
        db_weekly_attendance = WeeklyAttendance(
            user_id=user_id, 
            start_date=start_date, 
            end_date=end_date, 
            weekly_attendance_hours=daily_attendance_hours,
            full_name=full_name,
            attend_id=attend_id)
    session.add(db_weekly_attendance)
    session.commit()
    session.refresh(db_weekly_attendance)
    logger.info(f"Weekly attendance created: {db_weekly_attendance.user_id}")
    return db_weekly_attendance
