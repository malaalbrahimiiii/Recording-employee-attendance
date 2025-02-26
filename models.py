from datetime import datetime
import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    attend_id: int = Field(default=0, unique=True)
    weekly_work_hours: int = Field(default=0, nullable=True)

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    attendance: list["Attendance"] = Relationship(back_populates="user", cascade_delete=True)
    daily_attendance: list["DailyAttendance"] = Relationship(back_populates="user", cascade_delete=True)
    weekly_attendance: list["WeeklyAttendance"] = Relationship(back_populates="user", cascade_delete=True)
# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)

class AttendanceBase(SQLModel):
    status: bool = Field(default=False)
    reason: str | None = Field(default=None)
    type_attendance: str = Field(default="")
    full_name: str | None = Field(default=None)
    attend_id: int | None = Field(default=None)

class Attendance(AttendanceBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    user: User | None = Relationship(back_populates="attendance")
    created_at: datetime = Field(default_factory=datetime.now)

class AttendancePublic(AttendanceBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

class AttendancesPublic(SQLModel):
    data: list[AttendancePublic]
    count: int

class AttendanceUpdate(SQLModel):
    reason: str | None = Field(default=None)

class DailyAttendanceBase(SQLModel):
    daily_attendance_hours: int = Field(default=0)
    full_name: str | None = Field(default=None)
    attend_id: int | None = Field(default=None)

class DailyAttendance(DailyAttendanceBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    user: User | None = Relationship(back_populates="daily_attendance")
    created_at: datetime = Field(default_factory=datetime.now)

class DailyAttendancePublic(DailyAttendanceBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

class DailyAttendancesPublic(SQLModel):
    data: list[DailyAttendancePublic]
    count: int

class DailyAttendanceCreate(SQLModel):
    daily_attendance_hours: int = Field(default=0)
    full_name: str | None = Field(default=None)
    attend_id: int | None = Field(default=None)

class DailyAttendanceUpdate(SQLModel):
    daily_attendance_hours: int = Field(default=0)
    full_name: str | None = Field(default=None)
    attend_id: int | None = Field(default=None)

class WeeklyAttendanceBase(SQLModel):
    weekly_attendance_hours: int = Field(default=0)
    start_date: datetime = Field(default_factory=datetime.now)
    end_date: datetime = Field(default_factory=datetime.now)
    full_name: str | None = Field(default=None)
    attend_id: int | None = Field(default=None)

class WeeklyAttendance(WeeklyAttendanceBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    user: User | None = Relationship(back_populates="weekly_attendance")
    created_at: datetime = Field(default_factory=datetime.now)

class WeeklyAttendancePublic(WeeklyAttendanceBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

class WeeklyAttendancesPublic(SQLModel):
    data: list[WeeklyAttendancePublic]
    count: int

class WeeklyAttendanceCreate(SQLModel):
    weekly_attendance_hours: int = Field(default=0)
    start_date: datetime = Field(default_factory=datetime.now)
    end_date: datetime = Field(default_factory=datetime.now)
    full_name: str | None = Field(default=None)
    attend_id: int | None = Field(default=None)

class WeeklyAttendanceUpdate(SQLModel):
    weekly_attendance_hours: int = Field(default=0)
    start_date: datetime = Field(default_factory=datetime.now)
    end_date: datetime = Field(default_factory=datetime.now)
    full_name: str | None = Field(default=None)
    attend_id: int | None = Field(default=None)
