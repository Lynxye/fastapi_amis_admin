import datetime
from typing import Any, AsyncGenerator, List

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlmodel import SQLModel

from tests.conftest import async_db as db
from tests.test_sqlmodel.models import Article, ArticleContent, ArticleTagLink, Category, Tag, User


@pytest.fixture
async def prepare_database() -> AsyncGenerator[None, None]:
    async with db.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
        yield
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def async_client(app: FastAPI, prepare_database: Any) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://testserver") as c:
        yield c


@pytest.fixture
async def fake_users(async_session) -> List[User]:
    data = [
        User(
            id=i,
            username=f"User_{i}",
            password=f"password_{i}",
            create_time=datetime.datetime.strptime(f"2022-01-0{i} 00:00:00", "%Y-%m-%d %H:%M:%S"),
            address=["address_1", "address_2"],
            attach={"attach_1": "attach_1", "attach_2": "attach_2"},
        )
        for i in range(1, 6)
    ]
    async_session.add_all(data)
    await async_session.commit()
    return data


@pytest.fixture
async def fake_categorys(async_session) -> List[Category]:
    data = [Category(id=i, name=f"Category_{i}") for i in range(1, 6)]
    async_session.add_all(data)
    await async_session.commit()
    return data


@pytest.fixture
async def fake_article_contents(async_session) -> List[ArticleContent]:
    data = [ArticleContent(id=i, content=f"Content_{i}") for i in range(1, 6)]
    async_session.add_all(data)
    await async_session.commit()
    return data


@pytest.fixture
async def fake_articles(async_session, fake_users, fake_categorys, fake_article_contents) -> List[Article]:
    data = [
        Article(
            id=i,
            title=f"Article_{i}",
            description=f"Description_{i}",
            user_id=i,
            category_id=i,
            content_id=i,
        )
        for i in range(1, 6)
    ]
    async_session.add_all(data)
    await async_session.commit()
    return data


@pytest.fixture
async def fake_article_tags(async_session, fake_articles) -> List[Tag]:
    # add tags
    data = [Tag(id=i, name=f"Tag_{i}") for i in range(1, 6)]
    async_session.add_all(data)
    await async_session.commit()
    # add article_tag_link
    async_session.add_all([ArticleTagLink(article_id=i, tag_id=i) for i in range(1, 6)])
    await async_session.commit()
    return data
