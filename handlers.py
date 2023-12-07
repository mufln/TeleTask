import logging
from aiogram import Router,F
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import dbWorker
from aiogram.fsm.state import StatesGroup, State
from cfg import DB_PATH
import matcher
import json
r = Router()
db = dbWorker.dataBaseWorker(DB_PATH)
logging.basicConfig(level=logging.INFO)
users = db.getUsers()


class Register(StatesGroup):
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


class EditTask(StatesGroup):
    waitingForDescription = State()
    waitingForDate = State()
    waitingForBoth = State()


class AddAlias(StatesGroup):
    waitingForSubjectNAlias = State()
    waitingForSubject = State()
    waitingForAlias = State()


class Notify(StatesGroup):
    waitingForMessage = State()


#-------------------MISC-------------------
@r.message(Command("notify"),F.from_user.id==799100592)
async def notifyAll(message: types.Message, state: FSMContext):
    await message.answer("Отправь сообщение для всех")
    await state.set_state(Notify.waitingForMessage)


@r.message(Notify.waitingForMessage)
async def notify(message: types.Message, state: FSMContext):
    await state.update_data(msg = message.text)
    buttons = [[types.InlineKeyboardButton(text = "Подтвердить",callback_data="ACCEPTNOTIFICATION 0"),
               types.InlineKeyboardButton(text = "Отменить",callback_data="CANCEL"),
               types.InlineKeyboardButton(text = "Изменить",callback_data="ACCEPTNOTIFICATION 1")]]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(message.text, reply_markup=kb)


@r.callback_query(F.data.startswith("ACCEPTNOTIFICATION"))
async def sendNotification(data: types.CallbackQuery, state: FSMContext):
    mode = int(data.data.split()[1])
    user_data = await state.get_data()
    msg = user_data["msg"]
    if mode == 0:
        await data.message.edit_text("Сообщение отправлено")
        for chat_id in db.getUserIDS():
            await data.bot.send_message(chat_id, msg)
        return
    await data.message.delete()
    await notifyAll(data.message, state)


@r.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("Привет, если у тебя уже есть учетная запись, напиши /login, иначе /register, для отмены действия /cancel")


@r.message(Command("help"))
async def help(message: types.Message, state: FSMContext):
    await message.answer("""
    Расскажу коротко обо всех доступных тебе командах😁
    
    Предметы
    /newsub (название предмета) - добавляет новый предмет для тебя и твоей группы🥲
    /delsub - показывает меню, выбрав элемент которого будет удален соответствующий предмет
    /addalias - добавляет синоним для предмета, чтобы ты мог написать как линал, так и линейка или ЛиНеЙнАя АлГеБра🤓
    /listsubs - показывает предметы
    
    Задачи
    /deltask - показывает меню, выбрав элемент которого будет удалено соответствующее задание
    /edittask - позволяет изменить существующее задание
    /setcomplete - отмечает задачу, как выполненную
    /listtasks - показывает всю домашку
    /cancel - отменяет текущее действие
    
    
    Чтобы добавить домашку отправь сообщение в следующем формате:
    Добавь (название предмета) на (дата вида ДД.ММ) (текст задания)
    Например: Добавь матан на 18.10 подготовка к контрольной
    """)
    pass


@r.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Текущее действие отменено🗑️")
    return


@r.callback_query(F.data.startswith("CANCEL"))
async def cancelKB(data: types.CallbackQuery, state: FSMContext):
    await data.message.edit_text("Действие отменено")
    await state.clear()



#------------------REGISTATION------------------
@r.message(Command("register"))
async def registerNewUser(message: types.Message, state: FSMContext):
    await state.clear()
    if db.isUserTG(message.chat.id):
        await message.answer("Вы уже авторизованы😌")
        await help(message, state)
        return
    await message.answer("Введите ключ доступа для продолжения работы🙃\nНапишите /login,если у вас уже есть учетная запись")
    await state.set_state(Register.waitingForKey)


@r.message(Register.waitingForKey)
async def verifyKey(message: types.Message, state: FSMContext):
    if not db.verifyOneTimeKey(message.text):
        await message.answer("Неверный ключ, попробуй еще раз🙄")
    else:
        await state.update_data(usedKey = message.text)
        await message.answer("Введите имя пользователя"
                      "\nНапример: Adskiy_Botan"
                      "\nНе используйте спецсимволы и пробелы"
                      "\nДлина до 64 символов")
        await state.set_state(Register.waitingForUserName)


@r.message(Register.waitingForUserName)
async def setUpUserName(message: types.Message, state: FSMContext):
    if not matcher.isUserNameValid(message.text):
        await message.answer("Имя пользователя не соответствует требованиям☹️")
        return
    await state.update_data(userName = message.text)
    await message.answer("Придумайте сложный пароль (не менее 8 символов)🤓")
    await state.set_state(Register.waitingForPassword)


@r.message(Register.waitingForPassword)
async def setUpPassword(message: types.Message, state: FSMContext):
    if not matcher.isPasswordValid(message.text):
        await message.answer("Пароль слишком короткий 🍆 🫡")
        return
    await message.delete()
    userData = await state.get_data()
    db.delOneTimeKey(userData["usedKey"])
    db.addUser(userData["userName"], message.chat.id, message.text, 0)
    global users
    users.append(message.chat.id)
    await message.answer("Регистрация прошла успешно😎")
    await help(message, state)
    await state.clear()
#------------------END------------------




#------------------LOGIN------------------
@r.message(Command("login"))
async def login(message: types.Message, state: FSMContext):
    await state.clear()
    if db.isUserTG(message.chat.id):
        await message.answer("Вы уже авторизованы")
        await help(message, state)
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
        return
    db.addTelegramToExisting(message.chat.id,userData["userName"])
    await message.delete()
    await message.answer("Авторизация прошла успешно🙃")
    await help(message, state)
    await state.clear()
    return
#------------------END------------------




#------------------Task------------------
@r.message(F.text.lower().startswith("добавь"),F.from_user.id.in_(users))
async def addTask(message: types.Message, state: FSMContext):
    res = matcher.prepareTask(message.text)
    if res[0]==None:
        await message.answer("Предмет не указан или указан неверно")
        return
    elif res[1]==None:
        await message.answer("Дата не указана или указана неверно")
        return
    elif res[2]==None:
        await message.answer("Нет описания задачи")
        return
    elif not db.isSubjectExists(res[0].group().capitalize()):
        await message.answer("Такого предмета нет")
        return
    subject,date,description = res[0].group().capitalize(), res[1].group(), res[2].group().capitalize()
    db.addTask(subject,date,description)
    await message.answer(f"На {date} число по предмету {subject} добавлено задание {description}")
    return


@r.message(Command("deltask"),F.from_user.id.in_(users))
async def prepToDelTask(message: types.Message, state: FSMContext):
    tasks = db.getTasks(db.getUserNameByTGID(message.from_user.id))
    buttons = [[types.InlineKeyboardButton(text = i[1],callback_data=f"DT {i[0]}")] for i in tasks]
    buttons+= [[types.InlineKeyboardButton(text = "Отмена", callback_data="CANCEL")]]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    if len(tasks)!=0: await message.answer("Выбери задание для удаления",reply_markup=kb)
    else: await message.answer("Заданий нет😁")


@r.callback_query(F.data.startswith("DT"))
async def delTask(data: types.CallbackQuery):
    taskID = int(data.data.split()[1])
    db.delTask(taskID)
    await data.message.edit_text("Задание удалено😎")


@r.message(Command("listtasks"),F.from_user.id.in_(users))
async def displayTasks(message: types.Message, state: FSMContext):
    txt = db.getUncompletedTasks(db.getUserNameByTGID(message.from_user.id))
    await message.answer("Задачи:\n"+txt)


@r.message(Command("edittask"),F.from_user.id.in_(users))
async def prepToEditTask(message: types.Message, state: FSMContext):
    tasks = db.getTasks(db.getUserNameByTGID(message.from_user.id))
    buttons = [[types.InlineKeyboardButton(text=i[1], callback_data=f"ETST {i[0]}")] for i in tasks]
    buttons += [[types.InlineKeyboardButton(text="Отмена", callback_data="CANCEL")]]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    if len(tasks)!=0: await message.answer("Выбери задание для изменения😶",reply_markup=kb)
    else: await message.answer("Нечего редактировать, все выполнено!🥳")


@r.callback_query(F.data.startswith("ETST"))
async def editTask(data: types.CallbackQuery, state: FSMContext):
    ID = int(data.data.split()[1])
    buttons = [[types.InlineKeyboardButton(text = i, callback_data = f"ETET {a}")] for a,i in enumerate(["описание","дата"])]
    buttons += [[types.InlineKeyboardButton(text="Отмена",callback_data="CANCEL")]]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await data.message.delete()
    await state.update_data(taskID = ID)
    await data.message.answer("Что ты хочешь изменить?",reply_markup=kb)


@r.callback_query(F.data.startswith("ETET"))
async def selectEditingParameter(data: types.CallbackQuery, state: FSMContext):
    editingType = int(data.data.split()[1])
    await data.message.delete()
    if editingType == 0:
        await data.message.answer("Введи новое описание задачи🗣")
        await state.set_state(EditTask.waitingForDescription)
    elif editingType == 1:
        await data.message.answer("Введи новый дедлайн задачи📆")
        await state.set_state(EditTask.waitingForDate)

@r.message(EditTask.waitingForDescription)
async def editTaskDescription(message: types.Message, state: FSMContext):
    userData = await state.get_data()
    db.updateTask(task_id = userData["taskID"],description=message.text.capitalize())
    await message.answer("Задание обновлено")
    await state.clear()


@r.message(EditTask.waitingForDate)
async def editTaskDate(message: types.Message, state: FSMContext):
    if not matcher.isDateValid(message.text):
        await message.answer("Ты ввел дату в неверном формате🤡"); return
    data = await state.get_data()
    db.updateTask(task_id = data["taskID"], date = message.text.capitalize())
    await message.answer("Задание обновлено😵‍💫")
    await state.clear()


@r.message(Command("setcomplete"),F.from_user.id.in_(users))
async def prepToMarkAsComplete(message: types.Message, state: FSMContext):
    tasks = db.getTasks(db.getUserNameByTGID(message.from_user.id))
    buttons = [[types.InlineKeyboardButton(text=x[1], callback_data=f"MC {x[0]}")] for x in tasks]
    buttons += [[types.InlineKeyboardButton(text="Отмена",callback_data="CANCEL")]]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выбери задание, которое нужно отметить как выполненное",reply_markup=kb)

@r.callback_query(F.data.startswith("MC"))
async def MarkAsComplete(data: types.CallbackQuery, state: FSMContext):
    taskID = int(data.data.split()[1])
    db.markAsComplete(taskID, db.getUserNameByTGID(data.from_user.id))
    await data.message.delete()
    await data.message.answer("Молодец, задание вычеркнуто из списка дел✍️")


#------------------END------------------




#------------------Subject------------------
@r.message(Command("newsub"),F.from_user.id.in_(users))
async def addSubject(message: types.Message, state: FSMContext):
    t = message.text
    if len(t.split())==1:
        await message.answer("Введи название предмета🥸")
        await state.set_state(CreateSubject.waitingForSubjectName)
        return
    else:
        name = matcher.prepareSub(t).lower()
        db.addSub(name)
        await message.answer(f"Предмет {name} добавлен🥲")


@r.message(CreateSubject.waitingForSubjectName)
async def addSubjectByName(message: types.Message, state: FSMContext):
    t = message.text.lower()
    db.addSub(t)
    await message.answer(f"Предмет {t} добавлен🥲")
    await state.clear()


@r.message(Command("delsub"),F.from_user.id.in_(users))
async def prepToDelSubject(message: types.Message, state: FSMContext):
    subjects = db.getSubjectNamesAndIDs()
    buttons = [[types.InlineKeyboardButton(text = i[1], callback_data=f"DS {i[0]}")] for i in subjects]
    buttons += [[types.InlineKeyboardButton(text="Отмена", callback_data="CANCEL")]]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выбери предмет для удаления🫠",reply_markup=kb)


@r.message(AddAlias.waitingForSubjectNAlias)
async def addAlias(message: types.Message, state: FSMContext):
    if not matcher.isAliasStringValid(message.text):
        await message.answer("Название предмета и синоним надо писать через запятую в одном сообщении🤡")
        return
    subject_name, alias = matcher.prepareAlias(message.text)
    reply = db.isAliasValid(subject_name, alias)
    if reply==0:
        db.addAlias(subject_name,alias)
        await message.answer(f"Добавлен синоним {alias} для предмета {subject_name}")
        await state.clear()
        return
    elif reply==1: await message.answer("Такой предмет не найден")
    elif reply==2: await message.answer("Такой синоним уже существует")


@r.callback_query(F.data.startswith("DS"),F.from_user.id.in_(users))
async def delSubject(data:types.CallbackQuery):
    subject = int(data.data.split()[1])
    db.delSubByID(subject)
    await data.message.edit_text(f"Предмет удален😁",reply_markup=None)


@r.message(Command("addalias"),F.from_user.id.in_(users))
async def startAddAlias(message: types.Message, state: FSMContext):
    await message.answer("Отправь мне название предмета, для которого ты хочешь добавить синоним,\nИ сам синоним в одном сообщении (через запятую)🤯")
    await state.set_state(AddAlias.waitingForSubjectNAlias)


@r.message(Command("listsubs"),F.from_user.id.in_(users))
async def listsubs(message: types.Message, state: FSMContext):
    subs = db.getSubjectNamesAndAliases()
    l = '\n'.join([f"{i[0].capitalize()} aka " + ', '.join(json.loads(i[1])) for i in subs])
    await message.answer(l)