from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile

from src.projects.projects import GeosProject, FarmProject
from src.keyboards.inline import InlineKeyboards

router = Router()

PROJECTS = {
    "geos": GeosProject(),
    "farm": FarmProject(),
}

@router.callback_query(F.data == "projects")
async def projects_menu(callback: CallbackQuery):
    await callback.message.answer("Выберите проект:", reply_markup=InlineKeyboards.projects_menu())
    await callback.answer()

@router.callback_query(F.data == "geos")
async def geos_project(callback: CallbackQuery):
    project = GeosProject()
    await callback.message.answer(project.get_info(), reply_markup=InlineKeyboards.project_buttons("geos"))
    await callback.answer()

@router.callback_query(F.data == "farm")
async def farm_project(callback: CallbackQuery):
    project = FarmProject()
    await callback.message.answer(project.get_info(), reply_markup=InlineKeyboards.project_buttons("farm"))
    await callback.answer()

@router.callback_query(F.data.startswith("presentation_"))
async def send_presentation(callback: CallbackQuery):
    project_name = callback.data.split("_")[1]

    if project_name in PROJECTS:
        project = PROJECTS[project_name]
        presentation_path = project.get_presentation()

        if presentation_path and presentation_path.stat().st_size > 0:
            file = FSInputFile(presentation_path)
            await callback.message.answer_document(file, caption=f"📄 Презентация проекта {project.name}")
        else:
            await callback.message.answer(f"❌ Презентация для проекта {project.name} не найдена.")
    else:
        await callback.message.answer("❌ Проект не найден.")

    await callback.answer()