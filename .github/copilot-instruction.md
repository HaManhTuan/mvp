# Quy tắc Coding cho dự án FastAPI và SQLAlchemy

# I. Common checklist coding

## 1. Không có code/chức năng thừa (Clean code)
- (PASS/FAIL) Không có code/comment thừa, lặp lại, không cần thiết
- (PASS/FAIL) Tránh sự trùng lặp (DRY principle)
- (PASS/FAIL) Đặt tên biến và hàm có ý nghĩa
- (PASS/FAIL) Giới hạn độ dài function (tối đa 20-30 dòng)

Ví dụ:
```python
# Không tốt
def p(u, db):
    # Process user
    pass

# Tốt
def process_user_data(user: User, db: Session) -> UserResponse:
    """Process and transform user data."""
    pass
```

## 2. Có comment cho những đoạn logic khó hiểu
- (PASS/FAIL) Có comment cho những đoạn logic khó hiểu hoặc phức tạp

Ví dụ:
```python
# Không tốt
def calculate_total(cart):
    return sum([item.price * item.quantity * (1 - item.discount / 100) for item in cart])

# Tốt
def calculate_total(cart):
    """
    Calculate total cart value including discounts.
    Formula: Sum of (item price * quantity * (1 - discount percentage/100))
    """
    return sum([
        item.price * item.quantity * (1 - item.discount / 100) 
        for item in cart
    ])
```

## 3. Xử lý ngoại lệ (Error handling)
- (PASS/FAIL) Sử dụng HTTPException với status code phù hợp
- (PASS/FAIL) Tạo exception handlers tập trung
- (PASS/FAIL) Tránh "swallowing exceptions" (bắt ngoại lệ nhưng không xử lý)
- (PASS/FAIL) Tránh để lộ thông tin nhạy cảm trong message của exception

Ví dụ:
```python
@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = user_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 4. Quản lý transactions (Transaction management)
- (PASS/FAIL) Luôn xử lý rollback trong trường hợp lỗi
- (PASS/FAIL) Sử dụng context manager để quản lý transactions
- (PASS/FAIL) Xuất log lỗi khi có lỗi transaction xảy ra

Ví dụ:
```python
def transfer_funds(db: Session, from_account_id: int, to_account_id: int, amount: float):
    try:
        from_account = db.query(Account).filter(Account.id == from_account_id).with_for_update().first()
        to_account = db.query(Account).filter(Account.id == to_account_id).with_for_update().first()
        
        if not from_account or not to_account:
            raise ValueError("One or both accounts not found")
            
        if from_account.balance < amount:
            raise ValueError("Insufficient funds")
            
        from_account.balance -= amount
        to_account.balance += amount
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Transfer failed: {str(e)}")
        raise
```

## 5. Performance

### 5.1. Tối ưu hóa database
- (PASS/FAIL) Sử dụng các indexes phù hợp
- (PASS/FAIL) Eager loading với SQLAlchemy để tránh N+1 queries
- (PASS/FAIL) Sử dụng paging và limiting cho các collections lớn
- (PASS/FAIL) Sử dụng connection pooling cho scalability
- (PASS/FAIL) Sử dụng batch operations cho multiple records
- (PASS/FAIL) Chọn transaction isolation levels phù hợp
- (PASS/FAIL) Áp dụng concurrency controls (optimistic or pessimistic locking)

```python
# Không tốt - N+1 problem
users = db.query(User).all()
for user in users:
    print(user.posts)  # Gây ra query riêng biệt cho mỗi user

# Tốt - Eager loading
users = db.query(User).options(joinedload(User.posts)).all()
for user in users:
    print(user.posts)  # Không có additional queries
```

### 5.2. Caching
- (PASS/FAIL) Triển khai caching cho các truy vấn tốn kém
- (PASS/FAIL) Sử dụng Redis hoặc Memcached cho caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_expensive_calculation(param1: str, param2: int) -> dict:
    """Perform an expensive calculation - results will be cached."""
    # logic phức tạp
    return result
```

## 6. Async/await/Concurrency
- (PASS/FAIL) Sử dụng async/await cho I/O bound operations
- (PASS/FAIL) Hiểu được sự khác biệt giữa I/O bound và CPU bound
- (PASS/FAIL) Sử dụng scheduler/worker để chạy các task đa luồng (multi-threading) (nếu có)

Ví dụ:
```python
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## 7. Error Handling & Logging
- (PASS/FAIL) Sử dụng logging module thay vì print
- (PASS/FAIL) Định cấu hình các log levels phù hợp
- (PASS/FAIL) Log thông tin về các lỗi quan trọng, nhưng không lộ thông tin nhạy cảm

Ví dụ:
```python
import logging

logger = logging.getLogger(__name__)

def create_user(db: Session, user: UserCreate):
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            logger.warning(f"Attempted to create user with existing email: {user.email}")
            raise ValueError("Email already registered")
        
        db_user = User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Created new user with id: {db_user.id}")
        return db_user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.rollback()
        raise
```

## 8. Constants/Environment variables
- (PASS/FAIL) Không sử dụng hardcoded constants cho các thông số quan trọng. Mà sử dụng environment variables.
- (PASS/FAIL) Sử dụng secrets module để lưu trữ các biến môi trường nhạy cảm (nếu cần)
- (PASS/FAIL) Các constants phải được cân nhắc để đưa vào environment variables (nếu bị thay đổi theo môi trường), hoặc có thể được đưa vào class constant như constants.py

Ví dụ:
```python
# Không tốt
SECRET_KEY = "your-secret-key"

# Tốt
SECRET_KEY = os.environ.get("SECRET_KEY")
```

## 9. Libraries
- (PASS/FAIL) Không sử dụng các libraries không cần thiết
- (PASS/FAIL) Chỉ sử dụng các libraries có nguồn gốc rõ ràng và tin cậy (ví dụ: các libraries được đề xuất bởi FastAPI, SQLAlchemy, Pydantic, etc.)

## 10. Bảo mật xác thực
- (PASS/FAIL) Luôn băm mật khẩu, không lưu trữ mật khẩu văn bản thuần túy
- (PASS/FAIL) Luôn sử dụng JWT hoặc OAuth2 cho xác thực tất cả các API endpoints (trừ các API endpoints được đánh dấu là public như login, register, etc.)

Ví dụ:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
```

Ví dụ:
```python
# Không tốt - Kiểm tra người dùng một cách thủ công
@router.get("/users/me")
def get_current_user(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token or not validate_token(token):
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = get_user_id_from_token(token)
    # ...

# Tốt - Sử dụng OAuth2PasswordBearer và dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@router.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

## 11. Áp dụng RESTful API design
- (PASS/FAIL) Áp dụng RESTful API design cho tất cả các API endpoints
- (PASS/FAIL) Sử dụng HTTP methods và status codes phù hợp cho từng API endpoint
- (PASS/FAIL) Sử dụng query/path parameters hoặc request body phù hợp cho từng API endpoint.
Ví dụ: Khi cần submit dữ liệu (đặc biệt là dữ liệu cần bảo mật) từ client lên server, sử dụng request body. Khi cần lấy dữ liệu từ server về client, sử dụng query/path parameters.

Ví dụ:
```python
# Lấy danh sách users
@router.get("/user/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    # remove password field from response
    user.password = None
    return user

# Tạo user mới
@router.post("/user")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)
```

## 12. Xử lý dữ liệu nhạy cảm, bảo mật của người dùng
- (PASS/FAIL) Mã hóa dữ liệu nhạy cảm trong database
- (PASS/FAIL) Triển khai khái niệm least privilege
- (PASS/FAIL) Loại bỏ các field chứa dữ liệu nhạy cảm trong đầu ra để tránh data leakage như password, phone number, etc.

```python
from cryptography.fernet import Fernet

# Khóa mã hóa nên được lưu trữ an toàn trong biến môi trường
key = os.environ.get("ENCRYPTION_KEY")
cipher_suite = Fernet(key)

def encrypt_sensitive_data(data: str) -> str:
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data: str) -> str:
    return cipher_suite.decrypt(encrypted_data.encode()).decode()
```

## 12. Phòng chống tấn công (application security)
- (PASS/FAIL) Ngăn chặn SQL Injection bằng parameterized queries
- (PASS/FAIL) Sử dụng Content Security Policy (CSP)
- (PASS/FAIL) Ngăn chặn CSRF attacks

```python
# Tránh các sự cố SQL injection với SQLAlchemy
def search_users(db: Session, search_term: str):
    # An toàn - SQLAlchemy tham số hóa giá trị
    return db.query(User).filter(User.username.ilike(f"%{search_term}%")).all()
    
    # KHÔNG AN TOÀN - Không bao giờ sử dụng:
    # return db.execute(f"SELECT * FROM users WHERE username LIKE '%{search_term}%'").all()
```

# II. FastAPI specific rules

## 1. Có docstring cho tất cả các function
- (PASS/FAIL) Có docstring cho tất cả các function

## 2. Cấu trúc dự án
- (PASS/FAIL) Tổ chức dự án theo mô hình nhiều lớp (layers): routers, services, repositories, models, schemas
- (PASS/FAIL) Đặt tên file và thư mục theo kiểu snake_case

## 3. Quy ước đặt tên
- (PASS/FAIL) **Classes**: PascalCase (ví dụ: `UserModel`, `OrderService`)
- (PASS/FAIL) **Functions/Methods**: snake_case (ví dụ: `get_user_by_id`, `validate_email`)
- (PASS/FAIL) **Variables**: snake_case (ví dụ: `user_id`, `email_address`)
- (PASS/FAIL) **Constants**: UPPER_CASE (ví dụ: `MAX_LOGIN_ATTEMPTS`, `DEFAULT_PAGE_SIZE`)
- (PASS/FAIL) **Type hints**: Sử dụng cho tất cả parameters và return values

```python
def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()
```

## 4. Docstrings
- (PASS/FAIL) Sử dụng Google style docstrings
- (PASS/FAIL) Mô tả rõ parameters, returns, raises

```python
def create_user(user: UserCreate) -> User:
    """Create a new user.
    
    Args:
        user: User data transfer object.
        
    Returns:
        Created user instance.
        
    Raises:
        ValueError: If user with email already exists.
    """
```

## 5. Imports
- (PASS/FAIL) Sắp xếp imports theo thứ tự: standard library, third-party, local
- (PASS/FAIL) Tránh wildcard imports (`from module import *`)

```python
# Standard library
import os
from typing import List, Optional

# Third-party 
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

# Local
from app.models.user import User
from app.schemas.user import UserCreate
```

## 6. Validation
- (PASS/FAIL) Sử dụng Pydantic để validation
- (PASS/FAIL) Xác thực dữ liệu đầu vào trước khi thực hiện các hoạt động database

```python
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    
    @validator('username')
    def username_must_be_valid(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v
```

## 7. Defensive Programming

### 7.1. Kiểm tra đầu vào
- (PASS/FAIL) Không tin tưởng dữ liệu đầu vào từ người dùng
- (PASS/FAIL) Xác thực và làm sạch (sanitize) tất cả các tham số đầu vào

```python
def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
):
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > 100:
        limit = 100
    
    query = db.query(User)
    if search:
        search = search.strip()
        if search:
            query = query.filter(User.username.ilike(f"%{search}%"))
    
    return query.offset(skip).limit(limit).all()
```

### 7.2. Xử lý đầu ra
- (PASS/FAIL) Không trả về thông tin nhạy cảm hoặc lỗi chi tiết cho người dùng
- (PASS/FAIL) Sử dụng Pydantic cho định nghĩa schemas đầu ra

```python
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    
    class Config:
        orm_mode = True  # Cho phép chuyển đổi ORM model sang Pydantic model
```

## 8. Phân chia trách nhiệm
- (PASS/FAIL) Tuân thủ nguyên tắc Single Responsibility Principle
- (PASS/FAIL) Tách logic nghiệp vụ khỏi các API endpoints

```python
# Router chỉ xử lý logic endpoint
@router.post("/users/", response_model=UserResponse)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)

# Service xử lý logic nghiệp vụ
def create_user(db: Session, user: UserCreate):
    if user_repository.get_by_email(db, user.email):
        raise ValueError("Email already registered")
    
    hashed_password = get_password_hash(user.password)
    return user_repository.create(db, user, hashed_password)

# Repository xử lý tương tác database
def create(db: Session, user: UserCreate, hashed_password: str):
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

## 9. Áp dụng Dependency Injection
- (PASS/FAIL) Sử dụng Dependency Injection để code ngắn gọn và dễ bảo trì

```python
# Không tốt - Truy cập database trực tiếp trong router
@router.get("/users/")
def get_users():
    db = get_db()
    return db.query(User).all()

# Tốt - Sử dụng dependency injection
@router.get("/users/")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

## 10. Bảo vệ API
- (PASS/FAIL) Sử dụng Rate Limiting để ngăn chặn tấn công DoS (nếu cần)

Ví dụ:
```python
# Không tốt - Không có rate limiting
@router.post("/login")
def login(credentials: LoginRequest):
    # Logic đăng nhập

# Tốt - Áp dụng rate limiting
limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
def login(credentials: LoginRequest, request: Request):
    # Logic đăng nhập
```

## 11. Test code
- (PASS/FAIL) Viết unit tests cho mỗi function
- (PASS/FAIL) Sử dụng pytest cho testing framework
- (PASS/FAIL) Sử dụng monkeypatch của pytest để mock các dependencies
- (PASS/FAIL) Sử dụng TestClient của FastAPI để test API endpoints
- (PASS/FAIL) Áp dụng TDD khi có thể

```python
# Test sử dụng monkeypatch
def test_get_current_user(monkeypatch):
    # Arrange
    mock_user = User(id=1, username="testuser", email="test@example.com")
    
    def mock_get_user_by_id(*args, **kwargs):
        return mock_user
        
    monkeypatch.setattr(user_service, "get_user_by_id", mock_get_user_by_id)
    
    # Act
    result = user_service.get_current_user(token="fake_token", db=None)
    
    # Assert
    assert result == mock_user
    assert result.username == "testuser"

# Test sử dụng TestClient
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_user():
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data
```