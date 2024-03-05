from aiogram import Router
from aiogram.types import ChosenInlineResult

from database import crud


router = Router()


@router.chosen_inline_result()
async def pagination_demo(
        chosen_result: ChosenInlineResult,
):
    await crud.increment_pass_counter(int(chosen_result.result_id))
