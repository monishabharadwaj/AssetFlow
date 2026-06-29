from uuid import UUID

from app.core.enums import UserRole
from app.core.security import create_access_token, hash_password, verify_password
from app.exceptions.errors import BusinessRuleError, ConflictError, NotFoundError
from app.models.employee import Employee
from app.models.user import User
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserResponse


def user_to_response(user: User) -> UserResponse:
    employee = user.employee
    department = employee.department
    return UserResponse(
        id=user.id,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        employee_id=employee.id,
        email=employee.email,
        full_name=employee.full_name,
        employee_code=employee.employee_code,
        job_title=employee.job_title,
        department_id=employee.department_id,
        department_name=department.name if department else "",
    )


class AuthService:
    def __init__(
        self,
        repository: UserRepository,
        employee_repository: EmployeeRepository,
        department_repository: DepartmentRepository,
    ) -> None:
        self.repository = repository
        self.employee_repository = employee_repository
        self.department_repository = department_repository

    def login(self, data: LoginRequest) -> TokenResponse:
        email = data.email.lower()
        employee = self.employee_repository.get_by_email(email)
        if employee is None or not employee.is_active:
            raise BusinessRuleError("Invalid email or password")

        user = self.repository.get_by_employee_id(employee.id)
        if user is None or not verify_password(data.password, user.hashed_password):
            raise BusinessRuleError("Invalid email or password")
        if not user.is_active:
            raise BusinessRuleError("Account is inactive")

        token = create_access_token(subject=user.id, role=user.role.value)
        return TokenResponse(access_token=token)

    def get_user(self, user_id: UUID) -> UserResponse:
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User", str(user_id))
        return user_to_response(user)

    def list_users(self) -> list[UserResponse]:
        return [user_to_response(user) for user in self.repository.list_all()]

    def create_user(self, data: UserCreate) -> UserResponse:
        employee = self._resolve_employee(data)
        if self.repository.get_by_employee_id(employee.id) is not None:
            raise ConflictError(f"Employee '{employee.employee_code}' already has a login account")

        user = User(
            employee_id=employee.id,
            hashed_password=hash_password(data.password),
            role=data.role,
            is_active=True,
        )
        created = self.repository.create(user)
        self.repository.commit()
        loaded = self.repository.get_by_id(created.id)
        assert loaded is not None
        return user_to_response(loaded)

    def _resolve_employee(self, data: UserCreate) -> Employee:
        if data.employee_id is not None:
            employee = self.employee_repository.get_by_id(data.employee_id)
            if employee is None:
                raise NotFoundError("Employee", str(data.employee_id))
            if not employee.is_active:
                raise BusinessRuleError("Cannot create an account for an inactive employee")
            return employee

        assert data.email is not None
        assert data.employee_code is not None
        assert data.department_id is not None
        assert data.first_name is not None
        assert data.last_name is not None

        email = data.email.lower()
        if self.employee_repository.get_by_email(email) is not None:
            raise ConflictError(f"Employee with email '{email}' already exists")
        if self.employee_repository.get_by_code(data.employee_code) is not None:
            raise ConflictError(f"Employee with code '{data.employee_code}' already exists")

        department = self.department_repository.get_by_id(data.department_id)
        if department is None:
            raise NotFoundError("Department", str(data.department_id))

        employee = Employee(
            department_id=data.department_id,
            employee_code=data.employee_code.strip(),
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            email=email,
            job_title=data.job_title.strip() if data.job_title else None,
            is_active=True,
        )
        self.employee_repository.create(employee)
        self.employee_repository.flush()
        return employee

    @staticmethod
    def require_role(user: User, *allowed: UserRole) -> None:
        if user.role not in allowed:
            raise BusinessRuleError("Insufficient permissions for this action")
