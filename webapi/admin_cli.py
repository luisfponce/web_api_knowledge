import argparse
import getpass
import logging
import os
from dataclasses import dataclass

from passlib.hash import sha256_crypt
from sqlmodel import Session, select

from db.db_connection import engine
from models.user import User


SUPER_ADMIN_ROLE = "god"
LOGGER = logging.getLogger(__name__)


class SuperAdminBootstrapError(RuntimeError):
    pass


@dataclass(frozen=True)
class SuperAdminBootstrapResult:
    user: User
    action: str


def bootstrap_super_admin(
    session: Session,
    *,
    username: str,
    email: str,
    password: str,
    name: str = "Super",
    last_name: str = "Admin",
) -> SuperAdminBootstrapResult:
    existing_super_admin = session.exec(
        select(User).where(User.role == SUPER_ADMIN_ROLE)
    ).first()
    if existing_super_admin:
        if existing_super_admin.username == username:
            return SuperAdminBootstrapResult(user=existing_super_admin, action="already_exists")
        raise SuperAdminBootstrapError("super admin already exists")

    user = session.exec(select(User).where(User.username == username)).first()
    if user:
        user.name = name
        user.last_name = last_name
        user.email = email
        user.hashed_password = sha256_crypt.hash(password)
        user.role = SUPER_ADMIN_ROLE
        action = "promoted"
    else:
        user = User(
            username=username,
            name=name,
            last_name=last_name,
            email=email,
            hashed_password=sha256_crypt.hash(password),
            role=SUPER_ADMIN_ROLE,
        )
        action = "created"

    session.add(user)
    session.commit()
    session.refresh(user)
    LOGGER.warning(
        "super_admin_bootstrapped action=%s user_id=%s username=%s",
        action,
        user.id,
        user.username,
    )
    return SuperAdminBootstrapResult(user=user, action=action)


def _resolve_password(password_env: str | None) -> str:
    if password_env:
        password = os.getenv(password_env)
        if not password:
            raise SuperAdminBootstrapError(f"environment variable {password_env} is not set")
        return password

    password = getpass.getpass("Super admin password: ")
    if not password:
        raise SuperAdminBootstrapError("password is required")
    return password


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Trusted administrative operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap = subparsers.add_parser(
        "bootstrap-super-admin",
        help="Create or promote the first super admin without exposing a public endpoint",
    )
    bootstrap.add_argument("--username", required=True)
    bootstrap.add_argument("--email", required=True)
    bootstrap.add_argument("--name", default="Super")
    bootstrap.add_argument("--last-name", default="Admin")
    bootstrap.add_argument(
        "--password-env",
        help="Name of an environment variable containing the password; prompts securely when omitted",
    )
    return parser


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    args = build_parser().parse_args()

    try:
        if args.command == "bootstrap-super-admin":
            password = _resolve_password(args.password_env)
            with Session(engine) as session:
                result = bootstrap_super_admin(
                    session,
                    username=args.username,
                    email=args.email,
                    password=password,
                    name=args.name,
                    last_name=args.last_name,
                )
            print(f"super admin {result.action}: {result.user.username}")
            return 0
    except SuperAdminBootstrapError as exc:
        print(f"error: {exc}")
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
