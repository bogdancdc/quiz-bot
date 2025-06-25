import pytest
from unittest.mock import MagicMock
import sys, os
sys.path.append(os.path.abspath("."))
pytest.importorskip("telegram")
from telegram import Update, Bot
from telegram.ext import CallbackContext
from app.bot_runner import QuizBot
from app.handlers import _escape_markdown, SELECTING_ACTION
from app import main_menu_text

@pytest.fixture
def bot_instance(monkeypatch):
    bot = MagicMock(spec=Bot)
    qb = QuizBot("token", "data/questions.json", "data/staff.json", "data/reports.json", MagicMock())
    qb.application.bot = bot
    qb.conv_quiz_start = MagicMock()
    qb.conv_add_question_start = MagicMock()
    qb.career_start = MagicMock()
    return qb

@pytest.fixture
def mock_update():
    upd = MagicMock(spec=Update)
    upd.effective_user.id = 12345
    upd.effective_chat.id = 12345
    return upd

@pytest.fixture
def mock_context():
    return MagicMock(spec=CallbackContext)

@pytest.mark.asyncio
async def test_command_start(bot_instance, mock_update, mock_context):
    await bot_instance.command_start(mock_update, mock_context)
    mock_context.bot.send_message.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        text=_escape_markdown(main_menu_text),
        parse_mode="MarkdownV2",
        reply_markup=MagicMock.ANY
    )

@pytest.mark.asyncio
async def test_command_quiz(bot_instance, mock_update, mock_context):
    await bot_instance.command_quiz(mock_update, mock_context)
    bot_instance.conv_quiz_start.assert_called_once_with(mock_update, mock_context)

@pytest.mark.asyncio
async def test_command_add_question(bot_instance, mock_update, mock_context):
    await bot_instance.command_add_question(mock_update, mock_context)
    bot_instance.conv_add_question_start.assert_called_once_with(mock_update, mock_context)

@pytest.mark.asyncio
async def test_command_restart(bot_instance, mock_update, mock_context):
    await bot_instance.command_restart(mock_update, mock_context)
    mock_context.bot.send_message.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        text=_escape_markdown(main_menu_text),
        parse_mode="MarkdownV2",
        reply_markup=MagicMock.ANY
    )
    assert mock_context.user_data["state"] == SELECTING_ACTION

@pytest.mark.asyncio
async def test_command_career(bot_instance, mock_update, mock_context):
    await bot_instance.command_career(mock_update, mock_context)
    bot_instance.career_start.assert_called_once_with(mock_update, mock_context)

@pytest.mark.asyncio
async def test_career_scoring(monkeypatch, mock_context):
    bot = QuizBot("token", "data/questions.json", "data/staff.json", "data/reports.json", MagicMock())
    bot.career_questions = [{"text":"q1","options":["a","b","c","d","e","f"]}]
    mock_update = MagicMock(spec=Update)
    query = MagicMock()
    query.data = "B"
    mock_update.callback_query = query
    mock_update.effective_chat.id = 1
    mock_context.bot.send_message = MagicMock()
    monkeypatch.setattr(bot, "career_send_question", MagicMock())
    bot_context = mock_context
    bot_context.user_data = {"career": {"current_index": 0, "scores": {c:0 for c in ["Realistic","Investigative","Artistic","Social","Enterprising","Conventional"]}}}
    await bot.career_handle_answer(mock_update, bot_context)
    assert bot_context.user_data["career"]["scores"]["Investigative"] == 1
