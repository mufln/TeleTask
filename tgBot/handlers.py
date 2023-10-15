#начать работу над добавлением задач

import logging
from aiogram import Router,F
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import dbWorker
from aiogram.fsm.state import StatesGroup, State
import re
from cfg import DB_PATH
import linePreparer
r = Router()
db = dbWorker.dataBaseWorker(DB_PATH)
logging.basicConfig(level=logging.INFO)
class Register(StatesGroup): # - step by step registration
    waitingForKey = State()
    waitingForUserName = State()
    waitingForPassword = State()


class Login(StatesGroup):
    waitingForLogin = State()
    waitingForPassword = State()


class CreateSubject(StatesGroup):
    waitingForSubjectName = State()


class DeleteSubject(StatesGroup):
    waitingForDeletingSubject = State()


class CreateTask(StatesGroup):
    pass


class AddAlias(StatesGroup):
    waitingForSubjectNAlias = State()
    waitingForSubject = State()
    waitingForAlias = State()


@r.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет, если у тебя уже есть учетная запись, напиши /login, иначе /register😁\nчтобы отменить текущее действие, напиши /cancel")


@r.message(Command("register"))
async def register(message: types.Message, state: FSMContext):
    await state.clear()
    if db.isUserTG(message.chat.id):
        await message.answer("Вы уже авторизованы😌")
        return
    await message.answer("Введите ключ доступа для продолжения работы🙃\nНапишите /login,если у вас уже есть учетная запись")
    await state.set_state(Register.waitingForKey)


@r.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Текущее действие отменено🗑️")


@r.message(Register.waitingForKey)
async def verifyKey(message: types.Message, state: FSMContext):
    if not db.verifyOneTimeKey(message.text):
        await message.answer("Неверный ключ, попробуй еще раз🙄")
        return
    await state.update_data(usedKey = message.text)
    await message.answer("Введите имя пользователя"
                  "\nНапример: NaGiBaTor228"
                  "\nНе используйте спецсимволы и пробелы"
                  "\nДлина до 64 символов")
    await state.set_state(Register.waitingForUserName)


@r.message(Register.waitingForUserName)
async def setUpUserName(message: types.Message, state: FSMContext):
    if not re.fullmatch(r"[\w\d]{4,64}",message.text):
        await message.answer("Имя пользователя не соответствует требованиям☹️")
        return
    await state.update_data(userName = message.text)
    await message.answer("Придумайте сложный пароль🤓")
    await state.set_state(Register.waitingForPassword)


@r.message(Register.waitingForPassword)
async def setUpPassword(message: types.Message, state: FSMContext):
    if not re.fullmatch(r".{8,1024}",message.text):
        await message.answer("Пароль слишком короткий🫡")
        return
    userData = await state.get_data()
    db.delOneTimeKey(userData["usedKey"])
    db.addUser(userData["userName"], message.chat.id, message.text, 0)
    await message.answer("Регистрация прошла успешно😎")
    await state.clear()


@r.message(Command("login"))
async def login(message: types.Message, state: FSMContext):
    await state.clear()
    if db.isUserTG(message.chat.id):
        await message.answer("Вы уже авторизованы")
        return
    await message.answer("Введите логин")
    await state.set_state(Login.waitingForLogin)


@r.message(Login.waitingForLogin)
async def parseLogin(message: types.Message, state: FSMContext):
    if not db.isUserNAME(message.text):
        await message.answer("Пользователь не найден❎\nПопробуйте еще раз")
        return
    await message.answer("Пользователь найден✅\nВведите пароль")
    await state.update_data(userName = message.text)
    await state.set_state(Login.waitingForPassword)


@r.message(Login.waitingForPassword)
async def parsePassword(message: types.Message, state: FSMContext):
    userData = await state.get_data()
    if not db.checkPassword(userData["userName"],message.text):
        await message.answer("Пароль неверный🫤")
    db.addTelegramToExisting(message.chat.id,userData["userName"])
    await message.answer("Авторизация прошла успешно🙃")
    await state.clear()
    return


@r.message(F.text.lower().startswith("добавь"))
async def addTask(message: types.Message, state: FSMContext):
    if linePreparer.taskIsValid(message.text,db):
        subject,date,description = linePreparer.prepareTask(message.text)
        if linePreparer.subjectExists(subject,db):
            db.addTask(subject,date,description)
            await message.answer(f"На {date} число по предмету {subject} добавлено задание {description}")
            return
    await message.answer("Ты неверно описал задание или предмета не существует, формат:\nДобавь (Название предмета) на (дата вида 00.00) (описание задания)")


@r.message(Command("newsub"))
async def addSubject(message: types.Message, state: FSMContext):
    t = message.text
    if len(t.split())==1:
        await message.answer("Введи название предмета🥸")
        await state.set_state(CreateSubject.waitingForSubjectName)
        return
    else:
        name = linePreparer.prepareSub(t).lower()
        db.addSub(name)
        await message.answer(f"Предмет {name} добавлен🥲")


@r.message(CreateSubject.waitingForSubjectName)
async def addSubjectByName(message: types.Message, state: FSMContext):
    t = message.text.lower()
    db.addSub(t)
    await message.answer(f"Предмет {t} добавлен🥲")
    await state.clear()


@r.message(Command("delsub"))
async def prepToDelSubject(message: types.Message, state: FSMContext):
    subjects = db.getSubjectNamesAndIDs()
    buttons = [[types.InlineKeyboardButton(text = i[1], callback_data=f"DS {i[0]}")] for i in subjects]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выбери предмет для удаления🫠",reply_markup=kb)


@r.callback_query(F.data.startswith("DS"))
async def delSubject(data:types.CallbackQuery):
    subject = int(data.data.split()[1])
    db.delSubByID(subject)
    await data.message.edit_text(f"Предмет удален😁",reply_markup=None)


@r.message(Command("deltask"))
async def prepToDelTask(message: types.Message, state: FSMContext):
    tasks = db.getTasks()
    buttons = [[types.InlineKeyboardButton(text = i[1],callback_data=f"DT {i[0]}")] for i in tasks]
    kb = types.InlineKeyboardMarkup(keyboard=buttons)
    await message.answer("Выбери задание для удаления",reply_markup=kb)


@r.callback_query(F.data.startswith("DT"))
async def delTask(data: types.CallbackQuery):
    taskID = int(data.message.text.split()[1])
    db.delTask(taskID)
    await data.answer("Задание удалено😎")


@r.message(Command("listtasks"))
async def displayTasks(message: types.Message, state: FSMContext):
    txt = db.getAllTasksWithSubjects()
    await message.answer("Задачи:\n"+txt)


@r.message(Command("addalias"))
async def startAddAlias(message: types.Message, state: FSMContext):
    await message.answer("Отправь мне название предмета, для которого ты хочешь добавить синоним,\nИ сам синоним в одном сообщении (через запятую)🤯")
    await state.set_state(AddAlias.waitingForSubjectNAlias)


@r.message(AddAlias.waitingForSubjectNAlias)
async def addAlias(message: types.Message, state: FSMContext):
    subject_name, alias = linePreparer.prepareAlias(message.text)
    print(subject_name, alias)
    reply = db.aliasIsValid(subject_name,alias)
    if reply==0:
        db.addAlias(subject_name,alias)
        await message.answer(f"Добавлен синоним {alias} для предмета {subject_name}")
        await state.clear()
        return
    elif reply==1: await message.answer("Такой предмет не найден")
    elif reply==2: await message.answer("Такой синоним уже существует")


