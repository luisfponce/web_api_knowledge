# Database Diagram Documentation

This document describes the ORM data model implemented in [`User`](../webapi/models/user.py:8) and [`Prompts`](../webapi/models/prompts.py:6), and provides a DBML definition ready for dbdiagram.io.

## Source of truth

- [`User`](../webapi/models/user.py:8)
- [`Prompts`](../webapi/models/prompts.py:6)
- DB engine initialization in [`engine = create_engine(config.DB_URL, echo=True)`](../webapi/db/db_connection.py:6)
- Schema bootstrap in [`SQLModel.metadata.create_all(engine)`](../webapi/db/db_connection.py:10)

## DBML for dbdiagram.io
Visualize below code at: https://dbdiagram.io/d

```dbml
Table user {
  id int [pk, increment]
  username varchar(50) [not null]
  name varchar(100) [not null]
  last_name varchar(100) [not null]
  phone bigint [unique]
  email varchar(100) [not null]
  hashed_password varchar(255) [not null]

  Note: 'Mapped from SQLModel User entity'
}

Table prompts {
  id int [pk, increment]
  user_id int [not null, ref: > user.id]
  model_name varchar(30) [not null]
  prompt_text varchar(150) [not null]
  category varchar(30) [not null]
  rate varchar(30) [not null]

  Note: 'Mapped from SQLModel Prompts entity'
}
```

## Relationship cardinality

- One-to-many from [`User.prompts`](../webapi/models/user.py:18) to [`Prompts.user`](../webapi/models/prompts.py:14)
- Foreign key defined at [`user_id: int = Field(foreign_key='user.id', nullable=False)`](../webapi/models/prompts.py:8)

## Notes and naming consistency

- ORM class is pluralized as [`class Prompts(SQLModel, table=True):`](../webapi/models/prompts.py:6), while the related attribute in [`User`](../webapi/models/user.py:18) is also plural.
- File naming appears to include both [`webapi/models/prompts.py`](../webapi/models/prompts.py) and a visible editor tab for [`webapi/models/prompt.py`](../webapi/models/prompt.py). Consolidating to one naming convention may reduce confusion.
- If desired in a future refactor, entity naming could be normalized to singular class names with explicit `__tablename__` values to keep SQL table names stable.
