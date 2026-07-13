import argparse
import getpass
import logging
import os
from dataclasses import dataclass

from passlib.hash import sha256_crypt
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError
from sqlmodel import SQLModel, Session, create_engine, select

from core import config
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
    bootstrap.add_argument(
        "--db-url",
        help="Database URL override. Defaults to DB_URL from the environment or app config.",
    )
    return parser


def create_cli_engine(db_url: str | None = None):
    return create_engine(db_url or config.DB_URL, echo=True)


def _compose_host_fallback_db_url(db_url: str | None = None) -> str | None:
    configured_url = make_url(db_url or config.DB_URL)
    if configured_url.host != "mariadb":
        return None

    port_text = os.getenv("MARIADB_HOST_PORT") or str(configured_url.port or 3306)
    try:
        port = int(port_text)
    except ValueError as exc:
        raise SuperAdminBootstrapError("MARIADB_HOST_PORT must be an integer") from exc

    return configured_url.set(host="127.0.0.1", port=port).render_as_string(
        hide_password=False
    )


def _database_error_message(db_url: str | None = None) -> str:
    configured_url = make_url(db_url or config.DB_URL)
    message = (
        "error: unable to connect to the configured database. "
        "Verify DB_URL is reachable from where this command is running."
    )

    if configured_url.host == "mariadb":
        message += (
            " The hostname 'mariadb' only resolves inside the Docker Compose "
            "network. Run this command with `docker compose exec backend ...` "
            "or use a host-reachable DB URL such as "
            "`mariadb+mariadbconnector://USER:PASSWORD@127.0.0.1:3306/DB_NAME`."
        )

    return message


def _run_bootstrap_command(args, password: str, db_url: str | None = None) -> int:
    engine = create_cli_engine(db_url)
    SQLModel.metadata.create_all(engine)
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


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    args = build_parser().parse_args()

    try:
        if args.command == "bootstrap-super-admin":
            password = _resolve_password(args.password_env)
            try:
                return _run_bootstrap_command(args, password, args.db_url)
            except OperationalError as exc:
                fallback_url = _compose_host_fallback_db_url(args.db_url)
                if not fallback_url:
                    raise

                fallback_port = make_url(fallback_url).port or 3306
                print(
                    "warning: could not connect to Compose hostname 'mariadb'; "
                    f"retrying through 127.0.0.1:{fallback_port}."
                )
                try:
                    return _run_bootstrap_command(args, password, fallback_url)
                except OperationalError:
                    LOGGER.debug("database fallback connection failed", exc_info=True)
                    raise
    except SuperAdminBootstrapError as exc:
        print(f"error: {exc}")
        return 1
    except OperationalError as exc:
        print(_database_error_message(args.db_url if hasattr(args, "db_url") else None))
        LOGGER.debug("database connection failed", exc_info=True)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
